"""Guided teaching agent for published task questions.

The workflow is intentionally node-like and lightweight:
load_task_context -> classify_intent -> plan_steps -> retrieve_step_context
-> generate_teaching_step -> wait_student_response -> advance_or_summarize.
"""

from __future__ import annotations

import json
import re
import uuid
from typing import Any, Literal, TypedDict

from backend.app.models import Citation
from backend.app.services.agent_flow import NoCitationError
from backend.app.services.database import (
    get_guided_session,
    record_interaction,
    save_guided_session,
    update_guided_session,
)
from backend.app.services.llm import deepseek_client
from backend.app.services.rag import rag_service
from backend.app.services.web_search import WebSearchError, web_search_service


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
    code_draft: str
    task_context: dict[str, Any]
    intent: str
    task_complexity: int
    steps: list[TeachingStep]
    current_step: int
    citations: list[Citation]
    conversation: list[dict[str, Any]]
    status: str
    held: bool


ANSWER_REQUEST_PATTERN = re.compile(
    r"完整|直接.*答案|直接.*代码|生成.*完整|帮我写完|给我答案|给出答案|full answer|complete code",
    re.I,
)
STAY_ON_STEP_INTENTS = {"ask_concept", "need_hint", "request_answer"}


def classify_intent(state: GuidedAgentState) -> GuidedAgentState:
    text = f"{state.get('student_input', '')}\n{state.get('code_draft', '')}".lower()
    if ANSWER_REQUEST_PATTERN.search(text):
        state["intent"] = "request_answer"
        state["task_complexity"] = 4
    elif any(word in text for word in ["不会", "卡住", "提示", "hint", "怎么写"]):
        state["intent"] = "need_hint"
        state["task_complexity"] = 3
    elif "```" in text or "public " in text or "select " in text or "return " in text:
        state["intent"] = "submit_code"
        state["task_complexity"] = 3
    elif any(word in text for word in ["为什么", "原理", "区别", "解释", "是什么", "什么是"]):
        state["intent"] = "ask_concept"
        state["task_complexity"] = 2
    else:
        state["intent"] = "guided_practice"
        state["task_complexity"] = 3
    return state


def plan_steps(state: GuidedAgentState) -> GuidedAgentState:
    task = state.get("task_context", {})
    question = task.get("question") or {}
    stem = question.get("stem") or state.get("student_input", "")
    task_type = str(task.get("type") or "").lower()
    artifact = str(task.get("requiredArtifactType") or "")
    title = str(task.get("title") or "当前任务")

    steps: list[TeachingStep] = [
        {
            "title": "读题与定位资料",
            "goal": f"先确认《{title}》要解决的问题边界，并从资料中找依据。",
            "knowledge_points": ["需求理解", "资料引用", "任务边界"],
        },
        {
            "title": "拆解实现思路",
            "goal": "把题目拆成可独立完成的小步骤，而不是一次性生成完整答案。",
            "knowledge_points": ["分层设计", "接口路径", "数据流"],
        },
    ]

    if "code" in artifact or "coding" in task_type or question.get("type") == "code_fill":
        steps.append(
            {
                "title": "补全关键代码片段",
                "goal": "只完成当前步骤需要的局部代码，并逐行理解每一行的作用。",
                "knowledge_points": ["Controller", "Service", "Mapper/Entity", "逐行解析"],
            }
        )
    else:
        steps.append(
            {
                "title": "组织答案要点",
                "goal": "把依据、知识点和自己的判断整理成可提交的答案。",
                "knowledge_points": ["结构化表达", "证据支撑", "反思复盘"],
            }
        )

    if "项目5" in title or "Vue" in title or "联调" in title or "前后端" in stem:
        steps.append(
            {
                "title": "前后端联调检查",
                "goal": "核对请求路径、参数、统一返回和页面状态是否能对应起来。",
                "knowledge_points": ["Axios", "路由", "统一响应", "联调自测"],
            }
        )

    steps.append(
        {
            "title": "自检与提交",
            "goal": "用评分规则检查答案是否达标，再提交 AI 验收。",
            "knowledge_points": ["Rubric", "自检", "迭代修改"],
        }
    )
    state["steps"] = steps[:5]
    state["current_step"] = 0
    state["status"] = "teaching"
    return state


async def retrieve_step_context(state: GuidedAgentState) -> GuidedAgentState:
    step = state["steps"][state["current_step"]]
    task = state.get("task_context", {})
    question = task.get("question") or {}
    query = " ".join(
        part
        for part in [
            step["title"],
            step["goal"],
            " ".join(step.get("knowledge_points", [])),
            task.get("title", ""),
            task.get("goal", ""),
            question.get("stem", ""),
            state.get("student_input", ""),
        ]
        if part
    )
    citations = rag_service.search(
        query,
        limit=5,
        lesson_id=None,
        course_id=state.get("course_line_id"),
        task_id=state.get("task_id"),
    )
    if state.get("intent") == "ask_concept":
        try:
            web_citations = await web_search_service.search(state.get("student_input", query), limit=2)
            seen = {citation.source for citation in citations}
            citations.extend(citation for citation in web_citations if citation.source not in seen)
        except WebSearchError:
            pass
    if not citations:
        try:
            citations = await web_search_service.search(query, limit=3)
        except WebSearchError as exc:
            raise NoCitationError(f"本地知识库没有检索到可用资料，联网搜索也不可用：{exc}") from exc
    if not citations:
        raise NoCitationError("本地知识库和联网搜索都没有检索到可用于引导的资料。")
    state["citations"] = citations
    return state


async def generate_teaching_step(state: GuidedAgentState) -> GuidedAgentState:
    prompt = _build_teaching_prompt(state)
    message = await deepseek_client.answer(prompt, state.get("citations", []), "student")
    _append_assistant_message(state, message)
    return state


async def stream_teaching_step(state: GuidedAgentState):
    prompt = _build_teaching_prompt(state)
    parts: list[str] = []
    async for delta in deepseek_client.stream_answer(prompt, state.get("citations", []), "student"):
        parts.append(delta)
        yield delta
    _append_assistant_message(state, "".join(parts))


def _append_assistant_message(state: GuidedAgentState, message: str) -> None:
    state.setdefault("conversation", [])
    state["conversation"].append(
        {
            "role": "assistant",
            "step": state["current_step"],
            "content": message,
            "citations": [citation.model_dump() for citation in state.get("citations", [])],
        }
    )


def _build_teaching_prompt(state: GuidedAgentState) -> str:
    step = state["steps"][state["current_step"]]
    task = state.get("task_context", {})
    question = task.get("question") or {}
    answer_guard = ""
    if state.get("intent") == "request_answer":
        answer_guard = "学生正在请求完整答案。必须明确说明不能一次性代写完整答案，然后把请求拆成当前步骤的局部引导。"
    concept_guard = ""
    if state.get("intent") == "ask_concept":
        concept_guard = (
            "学生正在追问基础概念。必须先用初学者能听懂的话直接回答这个概念问题，"
            "可以说明课程资料是否直接定义了该概念；如果引用资料只是提供上下文，"
            "要把通用解释标注为“通用理解”，再把概念连接回当前题目。"
            "不要把学生赶去自己查资料，也不要只要求学生继续完成小任务。"
        )
    hold_guard = ""
    if state.get("intent") == "acknowledge":
        hold_guard = (
            "学生只是回复了确认/敷衍短句，并没有提交本步骤要求的实质内容。"
            "不要推进步骤，不要假设学生已经完成。必须指出还缺少什么，"
            "并要求学生在右侧答案区补充当前题目需要的具体答案或代码。"
        )
    question_guard = ""
    if question:
        option_lines = ""
        options = question.get("options") or []
        if options:
            option_lines = "；选项为：" + "；".join(
                f"{item.get('key')}. {item.get('text')}" for item in options if isinstance(item, dict)
            )
        question_guard = (
            "当前是教师发布的具体题目，不是让学生重新完成整个项目任务。"
            f"必须围绕题干“{question.get('stem', '')}”{option_lines}来引导。"
            "“你现在要完成的小任务”只能要求学生分析这道题、选择/填写这道题的答案，"
            "不能临时改成列业务模块、写 SQL、写代码等题干没有要求的任务。"
        )

    return f"""
你是“Web 系统应用开发”课程的智能体实训助教，正在陪同学生完成发布题目。

强规则：
- 不一次性给完整答案或完整项目代码。
- 每一步都必须基于引用资料或外部网页引用说明依据。
- 如果给代码，只给当前步骤所需的局部代码骨架或关键片段。
- 代码片段后必须逐行解释每一行的作用。
- 最后必须给出一个引导问题，推动学生自己在右侧输入框继续完成。

{answer_guard}
{concept_guard}
{hold_guard}
{question_guard}

当前任务：
- 标题：{task.get("title", "")}
- 目标：{task.get("goal", "")}
- 场景：{task.get("scenario", "")}
- 要求：{task.get("instruction", "")}
- 题目：{question.get("stem", state.get("student_input", ""))}
- 题型：{question.get("type", "guided")}

当前步骤：第 {state["current_step"] + 1}/{len(state["steps"])} 步
- 步骤标题：{step["title"]}
- 步骤目标：{step["goal"]}
- 涉及知识点：{"、".join(step.get("knowledge_points", []))}

学生当前输入：
{state.get("student_input", "")}

右侧代码/答案草稿：
{state.get("code_draft", "") or "暂未填写"}

请严格按以下 Markdown 结构输出：
## 本步目标
## 资料依据
## 知识点拆解
## 局部示例与逐行解析
## 你现在要完成的小任务
"""


async def start_guided_session(
    task_id: str,
    course_line_id: str,
    student_id: str,
    student_input: str,
    task_context: dict[str, Any],
    *,
    code_draft: str = "",
) -> dict[str, Any]:
    session_id = f"guided-{uuid.uuid4().hex[:12]}"
    state: GuidedAgentState = {
        "session_id": session_id,
        "task_id": task_id,
        "course_line_id": course_line_id,
        "student_id": student_id,
        "student_input": student_input,
        "code_draft": code_draft,
        "task_context": task_context,
        "conversation": [_context_message(task_context)],
        "current_step": 0,
        "status": "planning",
    }
    state = classify_intent(state)
    state = plan_steps(state)
    state = await retrieve_step_context(state)
    state = await generate_teaching_step(state)

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
    await _record_guided_interaction(state, state["conversation"][-1]["content"])
    return _response(state, "waiting")


async def prepare_guided_start(
    task_id: str,
    course_line_id: str,
    student_id: str,
    student_input: str,
    task_context: dict[str, Any],
    *,
    code_draft: str = "",
) -> GuidedAgentState:
    session_id = f"guided-{uuid.uuid4().hex[:12]}"
    state: GuidedAgentState = {
        "session_id": session_id,
        "task_id": task_id,
        "course_line_id": course_line_id,
        "student_id": student_id,
        "student_input": student_input,
        "code_draft": code_draft,
        "task_context": task_context,
        "conversation": [_context_message(task_context)],
        "current_step": 0,
        "status": "planning",
    }
    state = classify_intent(state)
    state = plan_steps(state)
    state = await retrieve_step_context(state)
    return state


def finish_guided_start(state: GuidedAgentState) -> dict[str, Any]:
    save_guided_session(
        session_id=state["session_id"],
        student_id=state["student_id"],
        task_id=state["task_id"],
        course_line_id=state["course_line_id"],
        steps=state["steps"],
        conversation=state["conversation"],
        current_step=state["current_step"],
        status="waiting",
    )
    state["status"] = "waiting"
    _record_guided_interaction_sync(state, state["conversation"][-1]["content"])
    return _response(state, "waiting")


async def continue_guided_session(
    session_id: str,
    student_message: str,
    *,
    code_draft: str = "",
) -> dict[str, Any]:
    session = get_guided_session(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    steps = json.loads(session["steps_json"])
    conversation = json.loads(session["conversation_json"])
    task_context = _conversation_task_context(conversation)
    current_step = int(session["current_step"])
    conversation.append({"role": "student", "content": student_message, "codeDraft": code_draft})

    state: GuidedAgentState = {
        "session_id": session_id,
        "task_id": session["task_id"],
        "course_line_id": session["course_line_id"],
        "student_id": session["student_id"],
        "student_input": student_message,
        "code_draft": code_draft,
        "task_context": task_context,
        "steps": steps,
        "current_step": current_step,
        "conversation": conversation,
        "status": "teaching",
    }
    state = classify_intent(state)
    hold_reason = _hold_step_reason(state)
    should_stay = state.get("intent") in STAY_ON_STEP_INTENTS or bool(hold_reason)

    if should_stay or current_step < len(steps) - 1:
        if hold_reason:
            _append_hold_message(state, hold_reason)
        elif not should_stay:
            current_step += 1
            state["current_step"] = current_step
            state = await retrieve_step_context(state)
            state = await generate_teaching_step(state)
        else:
            state = await retrieve_step_context(state)
            state = await generate_teaching_step(state)
        status: Literal["waiting", "completed"] = "waiting"
        conversation = state["conversation"]
    else:
        state = {
            "session_id": session_id,
            "task_id": session["task_id"],
            "course_line_id": session["course_line_id"],
            "student_id": session["student_id"],
            "student_input": student_message,
            "code_draft": code_draft,
            "steps": steps,
            "current_step": current_step,
            "conversation": conversation,
            "citations": [],
        }
        summary = _summary_message(steps, conversation)
        conversation.append({"role": "assistant", "step": current_step, "content": summary, "type": "summary", "citations": []})
        state["conversation"] = conversation
        status = "completed"

    update_guided_session(
        session_id=session_id,
        conversation=conversation,
        current_step=current_step,
        status=status,
    )
    await _record_guided_interaction(state, conversation[-1]["content"])
    state["status"] = status
    return _response(state, status)


async def prepare_guided_continue(
    session_id: str,
    student_message: str,
    *,
    code_draft: str = "",
) -> tuple[GuidedAgentState, Literal["waiting", "completed"]]:
    session = get_guided_session(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    steps = json.loads(session["steps_json"])
    conversation = json.loads(session["conversation_json"])
    task_context = _conversation_task_context(conversation)
    current_step = int(session["current_step"])
    conversation.append({"role": "student", "content": student_message, "codeDraft": code_draft})

    state: GuidedAgentState = {
        "session_id": session_id,
        "task_id": session["task_id"],
        "course_line_id": session["course_line_id"],
        "student_id": session["student_id"],
        "student_input": student_message,
        "code_draft": code_draft,
        "task_context": task_context,
        "steps": steps,
        "current_step": current_step,
        "conversation": conversation,
        "status": "teaching",
    }
    state = classify_intent(state)
    hold_reason = _hold_step_reason(state)
    should_stay = state.get("intent") in STAY_ON_STEP_INTENTS or bool(hold_reason)

    if should_stay or current_step < len(steps) - 1:
        if hold_reason:
            _append_hold_message(state, hold_reason)
            state["citations"] = []
            return state, "waiting"
        if not should_stay:
            current_step += 1
            state["current_step"] = current_step
        state = await retrieve_step_context(state)
        return state, "waiting"

    summary = _summary_message(steps, conversation)
    conversation.append({"role": "assistant", "step": current_step, "content": summary, "type": "summary", "citations": []})
    state["conversation"] = conversation
    state["citations"] = []
    return state, "completed"


def finish_guided_continue(state: GuidedAgentState, status: Literal["waiting", "completed"]) -> dict[str, Any]:
    update_guided_session(
        session_id=state["session_id"],
        conversation=state["conversation"],
        current_step=state["current_step"],
        status=status,
    )
    state["status"] = status
    _record_guided_interaction_sync(state, state["conversation"][-1]["content"])
    return _response(state, status)


def _summary_message(steps: list[dict[str, Any]], conversation: list[dict[str, Any]]) -> str:
    completed = "\n".join(f"- {index + 1}. {step.get('title')}: {step.get('goal')}" for index, step in enumerate(steps))
    return (
        "## 本次引导小结\n"
        "你已经完成了这道题的分步学习流程。\n\n"
        "## 已覆盖步骤\n"
        f"{completed}\n\n"
        "## 下一步\n"
        "请回到右侧输入框整理最终答案或代码片段，然后点击“提交验收”获取评分反馈。"
    )


def _context_message(task_context: dict[str, Any]) -> dict[str, Any]:
    return {"role": "system", "type": "task_context", "taskContext": task_context}


def _conversation_task_context(conversation: list[dict[str, Any]]) -> dict[str, Any]:
    for item in conversation:
        if item.get("type") == "task_context" and isinstance(item.get("taskContext"), dict):
            return item["taskContext"]
    return {}


def _hold_step_reason(state: GuidedAgentState) -> str:
    message = state.get("student_input", "").strip()
    code_draft = state.get("code_draft", "").strip()
    task = state.get("task_context", {})
    question = task.get("question") or {}
    combined = f"{message}\n{code_draft}".strip()

    if _asks_question(message):
        return ""
    if _looks_like_ui_action(message):
        return "你这句话像是在操作流程，不是当前题目的答案内容。"
    if state.get("intent") in STAY_ON_STEP_INTENTS:
        return ""
    if _has_substantive_submission(combined, question):
        return ""
    return "当前输入还没有形成可检查的答案或代码。"


def _asks_question(message: str) -> bool:
    return bool(re.search(r"[?？]|为什么|怎么|如何|是什么|什么是|区别|解释|报错|错误", message))


def _looks_like_ui_action(message: str) -> bool:
    text = message.strip()
    if not text:
        return False
    if len(text) > 16:
        return False
    if re.search(r"[A-Za-z0-9_`{}();=<>]", text):
        return False
    return not _asks_question(text)


def _has_substantive_submission(content: str, question: dict[str, Any]) -> bool:
    compact = content.strip()
    if len(compact) >= 80:
        return True
    stem = str(question.get("stem") or "").lower()
    qtype = str(question.get("type") or "")
    if qtype in {"single_choice", "multi_choice", "true_false"}:
        return bool(re.fullmatch(r"\s*(我的答案[:：]?)?\s*[A-Da-d]{1,4}\s*", compact))
    if "sql" in stem or "建表" in stem:
        return bool(re.search(r"\b(create|select|insert|update|delete|primary|index|varchar|longtext)\b", compact, re.I))
    if "xml" in stem or "mapper" in stem:
        return "<" in compact and ">" in compact
    if "代码" in stem or qtype == "code_fill":
        return bool(re.search(r"[{};=()]|public\s+|return\s+|class\s+|@", compact))
    return len(compact) >= 20


def _append_hold_message(state: GuidedAgentState, reason: str) -> None:
    task = state.get("task_context", {})
    question = task.get("question") or {}
    stem = question.get("stem") or task.get("title") or "当前题目"
    code_draft = state.get("code_draft", "").strip()
    draft_line = "右侧答案区已有内容，我会以右侧内容作为最终验收依据。" if code_draft else "右侧答案区目前还没有足够内容。"
    message = (
        "## 还不能进入下一步\n\n"
        f"{reason}\n\n"
        "## 当前题目\n"
        f"{stem}\n\n"
        "## 你需要补什么\n"
        f"{draft_line} 请在右侧写出当前题目要求的具体答案或代码片段；如果已经写完，请点击页面右上角的“提交验收”按钮，而不是在对话框里输入提交。\n\n"
        "## 当前步骤仍然保持\n"
        "我不会把这句话当成知识问题检索资料，也不会因为一句流程确认就推进步骤。"
    )
    state["held"] = True
    state["citations"] = []
    _append_assistant_message(state, message)


def _response(state: GuidedAgentState, status: str) -> dict[str, Any]:
    steps = state.get("steps", [])
    current = int(state.get("current_step", 0))
    last = next(
        (item for item in reversed(state.get("conversation", [])) if item.get("role") == "assistant"),
        {},
    )
    citations = state.get("citations") or [Citation(**item) for item in last.get("citations", []) if isinstance(item, dict)]
    return {
        "sessionId": state["session_id"],
        "intent": state.get("intent", ""),
        "steps": steps,
        "currentStep": current,
        "totalSteps": len(steps),
        "currentStepTitle": steps[current]["title"] if steps and current < len(steps) else None,
        "message": str(last.get("content") or ""),
        "citations": [citation.model_dump() for citation in citations],
        "status": status,
    }


async def _record_guided_interaction(state: GuidedAgentState, answer: str) -> None:
    _record_guided_interaction_sync(state, answer)


def _record_guided_interaction_sync(state: GuidedAgentState, answer: str) -> None:
    record_interaction(
        kind="guided",
        course_id=state.get("course_line_id", ""),
        lesson_id=state.get("task_id"),
        question=state.get("student_input", ""),
        answer=answer,
        student_id=state.get("student_id"),
    )
