"""LangGraph 多节点状态机 — 智能体引导教学模式。

核心流程：
1. classify_intent — 识别学生意图，判断任务量
2. plan_steps — 规划 N 个教学步骤
3. [循环 N 步] retrieve_context → generate_teaching → check_understanding
4. summarize_session — 总结学习过程
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any, Literal, TypedDict

from backend.app.services.database import (
    get_guided_session,
    save_guided_session,
    update_guided_session,
)
from backend.app.services.llm import LLMError, deepseek_client
from backend.app.services.rag import rag_service


class TeachingStep(TypedDict):
    title: str
    goal: str
    knowledge_points: list[str]


class GuidedAgentState(TypedDict, total=False):
    session_id: str
    task_id: str
    course_line_id: str
    student_id: str
    student_input: str
    task_context: dict[str, Any]

    intent: str  # "request_answer" | "ask_concept" | "submit_code" | "need_hint"
    task_complexity: int  # 1-5
    steps: list[TeachingStep]
    current_step: int
    step_results: list[dict[str, Any]]
    conversation: list[dict[str, str]]

    final_summary: str
    status: str  # "planning" | "teaching" | "waiting" | "summarizing" | "done"


# ─── Intent Classification ────────────────────────────────────────────

INTENT_PROMPT = """你是一个教学意图识别器。根据学生的输入，判断其意图。

学生输入：{student_input}
任务上下文：{task_context}

请返回 JSON：
{{
  "intent": "request_answer | ask_concept | submit_code | need_hint",
  "task_complexity": 1-5,
  "reason": "判断理由"
}}

规则：
- request_answer: 学生要求直接给出答案或完整代码
- ask_concept: 学生在问概念、原理、为什么
- submit_code: 学生提交了自己的代码或答案
- need_hint: 学生说不会、卡住了、需要提示
- task_complexity: 1=简单填空, 5=复杂项目"""


async def classify_intent(state: GuidedAgentState) -> GuidedAgentState:
    """识别学生意图，判断任务复杂度。"""
    prompt = INTENT_PROMPT.format(
        student_input=state["student_input"],
        task_context=json.dumps(state.get("task_context", {}), ensure_ascii=False),
    )
    result = await deepseek_client.answer(prompt, citations=[])
    try:
        parsed = json.loads(result)
        state["intent"] = parsed.get("intent", "ask_concept")
        state["task_complexity"] = parsed.get("task_complexity", 3)
    except (json.JSONDecodeError, KeyError):
        state["intent"] = "ask_concept"
        state["task_complexity"] = 3
    return state


# ─── Step Planning ─────────────────────────────────────────────────────

PLAN_PROMPT = """你是一个教学步骤规划器。根据任务和学生输入，规划教学步骤。

任务信息：
- 标题：{task_title}
- 目标：{task_goal}
- 说明：{task_instruction}
- 场景：{task_scenario}

学生输入：{student_input}
任务复杂度：{complexity}/5

请规划 {step_count} 个教学步骤，返回 JSON：
{{
  "steps": [
    {{
      "title": "步骤标题",
      "goal": "这一步要达成什么",
      "knowledge_points": ["知识点1", "知识点2"]
    }}
  ]
}}

规则：
- 每步聚焦一个具体目标
- 从理解需求到编码实现，循序渐进
- 每步都要包含相关知识点
- 不要直接给完整答案，而是引导学生思考"""


async def plan_steps(state: GuidedAgentState) -> GuidedAgentState:
    """规划教学步骤。"""
    task = state.get("task_context", {})
    complexity = state.get("task_complexity", 3)
    step_count = min(max(complexity, 2), 5)

    prompt = PLAN_PROMPT.format(
        task_title=task.get("title", ""),
        task_goal=task.get("goal", ""),
        task_instruction=task.get("instruction", ""),
        task_scenario=task.get("scenario", ""),
        student_input=state["student_input"],
        complexity=complexity,
        step_count=step_count,
    )
    result = await deepseek_client.answer(prompt, citations=[])
    try:
        parsed = json.loads(result)
        state["steps"] = parsed.get("steps", [])
    except (json.JSONDecodeError, KeyError):
        state["steps"] = [
            {"title": "理解任务", "goal": "理解任务要求", "knowledge_points": []},
            {"title": "设计方案", "goal": "设计实现方案", "knowledge_points": []},
            {"title": "编写代码", "goal": "完成代码实现", "knowledge_points": []},
        ]
    state["current_step"] = 0
    state["step_results"] = []
    state["status"] = "teaching"
    return state


# ─── Context Retrieval ─────────────────────────────────────────────────

async def retrieve_context(state: GuidedAgentState) -> GuidedAgentState:
    """检索知识库。无结果时标记需要联网搜索。"""
    current = state["steps"][state["current_step"]]
    query = f"{current['title']} {' '.join(current.get('knowledge_points', []))}"
    task = state.get("task_context", {})

    citations = rag_service.search(
        query,
        top_k=3,
        lesson_id=None,
        course_id=state.get("course_line_id"),
    )

    state.setdefault("step_results", [])
    if citations:
        state["step_results"].append({
            "step": state["current_step"],
            "context": [{"title": c.title, "snippet": c.snippet, "source": c.source} for c in citations],
            "needs_web_search": False,
        })
    else:
        state["step_results"].append({
            "step": state["current_step"],
            "context": [],
            "needs_web_search": True,
        })
    return state


# ─── Teaching Content Generation ───────────────────────────────────────

TEACHING_PROMPT = """你是一个 AI 实训助教。当前正在引导学生完成第 {step_num}/{total_steps} 步。

当前步骤：{step_title}
步骤目标：{step_goal}
涉及知识点：{knowledge_points}

任务信息：
- 标题：{task_title}
- 目标：{task_goal}
- 说明：{task_instruction}

参考资料：
{context}

学生原始输入：{student_input}

请生成该步骤的教学内容，要求：
1. 先说明这一步要做什么、为什么要做
2. 如果涉及代码，给出代码框架（不是完整答案），并逐行解析每一行的含义
3. 列出涉及的知识点，用结构化方式说明
4. 最后提出一个引导性问题，让学生思考或动手

格式要求：
- 用清晰的标题分段
- 代码用 ``` 包裹
- 知识点用列表展示
- 不要直接给出完整答案"""


async def generate_teaching(state: GuidedAgentState) -> GuidedAgentState:
    """生成当前步骤的教学内容。"""
    current_step = state["steps"][state["current_step"]]
    step_result = state["step_results"][state["current_step"]] if state["step_results"] else {}

    context_text = ""
    if step_result.get("context"):
        context_text = "\n".join(
            f"- [{c['title']}] {c['snippet']}" for c in step_result["context"]
        )
    elif step_result.get("needs_web_search"):
        context_text = "（知识库无相关内容，请基于你的知识回答，但要标注这不是来自课程资料）"

    task = state.get("task_context", {})
    prompt = TEACHING_PROMPT.format(
        step_num=state["current_step"] + 1,
        total_steps=len(state["steps"]),
        step_title=current_step["title"],
        step_goal=current_step["goal"],
        knowledge_points=", ".join(current_step.get("knowledge_points", [])),
        task_title=task.get("title", ""),
        task_goal=task.get("goal", ""),
        task_instruction=task.get("instruction", ""),
        context=context_text,
        student_input=state["student_input"],
    )

    teaching_content = await deepseek_client.answer(prompt, citations=[])

    state.setdefault("conversation", [])
    state["conversation"].append({
        "role": "assistant",
        "step": state["current_step"],
        "content": teaching_content,
    })

    return state


# ─── Session Management ────────────────────────────────────────────────

async def start_guided_session(
    task_id: str,
    course_line_id: str,
    student_id: str,
    student_input: str,
    task_context: dict[str, Any],
) -> dict[str, Any]:
    """启动引导会话，执行 classify → plan → 第一步 retrieve + teach。"""
    session_id = f"guided-{uuid.uuid4().hex[:12]}"

    state: GuidedAgentState = {
        "session_id": session_id,
        "task_id": task_id,
        "course_line_id": course_line_id,
        "student_id": student_id,
        "student_input": student_input,
        "task_context": task_context,
        "conversation": [],
        "current_step": 0,
        "step_results": [],
        "status": "planning",
    }

    # 1. 意图识别
    state = await classify_intent(state)

    # 2. 规划步骤
    state = await plan_steps(state)

    # 3. 第一步：检索 + 教学
    if state["steps"]:
        state = await retrieve_context(state)
        state = await generate_teaching(state)

    # 4. 持久化
    save_guided_session(
        session_id=session_id,
        student_id=student_id,
        task_id=task_id,
        course_line_id=course_line_id,
        steps=state["steps"],
        conversation=state["conversation"],
        current_step=state["current_step"],
        status="waiting",
    )

    return {
        "sessionId": session_id,
        "intent": state["intent"],
        "steps": state["steps"],
        "currentStep": state["current_step"],
        "message": state["conversation"][-1]["content"] if state["conversation"] else "",
        "status": "waiting",
    }


async def continue_guided_session(
    session_id: str,
    student_message: str,
) -> dict[str, Any]:
    """继续引导会话，处理学生回应，推进到下一步。"""
    session = get_guided_session(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    steps = json.loads(session["steps_json"])
    conversation = json.loads(session["conversation_json"])
    current_step = session["current_step"]

    # 记录学生回应
    conversation.append({"role": "student", "content": student_message})

    # 判断是否需要推进到下一步
    if current_step < len(steps) - 1:
        next_step = current_step + 1
        state: GuidedAgentState = {
            "session_id": session_id,
            "task_id": session["task_id"],
            "course_line_id": session["course_line_id"],
            "student_id": session["student_id"],
            "student_input": student_message,
            "task_context": {},
            "steps": steps,
            "current_step": next_step,
            "step_results": [],
            "conversation": conversation,
        }

        state = await retrieve_context(state)
        state = await generate_teaching(state)

        update_guided_session(
            session_id=session_id,
            conversation=state["conversation"],
            current_step=next_step,
            status="waiting",
        )

        return {
            "sessionId": session_id,
            "currentStep": next_step,
            "totalSteps": len(steps),
            "message": state["conversation"][-1]["content"],
            "status": "waiting",
        }
    else:
        # 最后一步，生成总结
        summary = await _generate_summary(steps, conversation)
        conversation.append({"role": "assistant", "content": summary, "type": "summary"})

        update_guided_session(
            session_id=session_id,
            conversation=conversation,
            current_step=current_step,
            status="completed",
        )

        return {
            "sessionId": session_id,
            "currentStep": current_step,
            "totalSteps": len(steps),
            "message": summary,
            "status": "completed",
        }


async def _generate_summary(steps: list[dict], conversation: list[dict]) -> str:
    """生成学习总结。"""
    steps_text = "\n".join(f"- {s['title']}: {s['goal']}" for s in steps)
    recent = conversation[-6:] if len(conversation) > 6 else conversation
    recent_text = "\n".join(f"{m['role']}: {m['content'][:200]}" for m in recent)

    prompt = f"""请根据以下学习过程生成简洁的总结。

学习步骤：
{steps_text}

最近对话：
{recent_text}

总结要求：
1. 回顾学生完成了哪些步骤
2. 指出学生的亮点
3. 提出后续建议
4. 不超过 200 字"""

    return await deepseek_client.answer(prompt, citations=[])
