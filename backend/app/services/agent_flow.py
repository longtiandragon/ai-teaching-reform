from __future__ import annotations

import asyncio
from typing import Any, TypedDict

from backend.app.models import ChatRequest, Citation
from backend.app.services.database import record_interaction
from backend.app.services.llm import deepseek_client
from backend.app.services.rag import rag_service


class NoCitationError(RuntimeError):
    pass


class TeachingAgentState(TypedDict, total=False):
    course_id: str
    lesson_id: str | None
    question: str
    mode: str
    intent: str
    rewritten_query: str
    citations: list[Citation]
    answer: str
    fallback: bool
    next_action: str


def create_initial_state(request: ChatRequest) -> TeachingAgentState:
    return {
        "course_id": request.course_id,
        "lesson_id": request.lesson_id,
        "question": request.question,
        "mode": request.mode,
    }


async def run_agent_once(request: ChatRequest) -> TeachingAgentState:
    state = create_initial_state(request)
    graph = _try_compile_graph()
    if graph is not None:
        result = await graph.ainvoke(state)
    else:
        result = await _manual_flow(state)
    await _record_result(result)
    return result


async def stream_agent(request: ChatRequest):
    state = create_initial_state(request)
    yield "status", {"stage": "intent", "message": "正在判断学习意图..."}
    state = detect_intent(state)

    yield "status", {"stage": "rewrite", "message": "正在结合当前关卡改写问题..."}
    state = rewrite_query(state)

    yield "status", {"stage": "retrieving", "message": "正在检索课程知识库..."}
    state = await retrieve_context(state)
    if not state.get("citations"):
        raise NoCitationError("知识库没有检索到可引用资料，已停止生成。")
    yield "citations", {"citations": [citation.model_dump() for citation in state.get("citations", [])]}

    yield "status", {"stage": "generating", "message": "DeepSeek 正在基于引用生成回答..."}
    parts: list[str] = []
    async for delta in deepseek_client.stream_answer(
        state["question"],
        state.get("citations", []),
        state.get("mode", "student"),
    ):
        parts.append(delta)
        yield "delta", {"text": delta}

    state["answer"] = "".join(parts)
    state["fallback"] = False
    state = plan_next_action(state)
    await _record_result(state)
    yield "done", {"answer": state["answer"], "next_action": state.get("next_action", "")}


def detect_intent(state: TeachingAgentState) -> TeachingAgentState:
    question = state["question"]
    if any(word in question for word in ["提示", "不会", "卡住", "怎么写"]):
        state["intent"] = "hint"
    elif any(word in question for word in ["为什么", "原理", "区别", "解释"]):
        state["intent"] = "explain"
    elif any(word in question for word in ["检查", "评价", "改错", "哪里错"]):
        state["intent"] = "diagnose"
    else:
        state["intent"] = "qa"
    return state


def rewrite_query(state: TeachingAgentState) -> TeachingAgentState:
    lesson_hint = state.get("lesson_id") or "current-lesson"
    intent = state.get("intent", "qa")
    state["rewritten_query"] = f"{lesson_hint} {intent} {state['question']}"
    return state


async def retrieve_context(state: TeachingAgentState) -> TeachingAgentState:
    citations = await asyncio.to_thread(
        rag_service.search,
        state.get("rewritten_query") or state["question"],
        None,
        state.get("lesson_id"),
        state.get("course_id"),
    )
    state["citations"] = citations
    return state


async def generate_answer(state: TeachingAgentState) -> TeachingAgentState:
    if not state.get("citations"):
        raise NoCitationError("知识库没有检索到可引用资料，已停止生成。")
    answer = await deepseek_client.answer(
        state["question"],
        state.get("citations", []),
        state.get("mode", "student"),
    )
    state["answer"] = answer
    state["fallback"] = False
    return state


def plan_next_action(state: TeachingAgentState) -> TeachingAgentState:
    intent = state.get("intent")
    if intent == "hint":
        state["next_action"] = "先补全右侧代码编辑器中的 TODO，再提交练习反馈。"
    elif intent == "diagnose":
        state["next_action"] = "把你的代码和错误现象写入右侧编辑器，提交后生成诊断。"
    else:
        state["next_action"] = "继续阅读任务说明，尝试用自己的话复述关键调用链。"
    return state


async def _manual_flow(state: TeachingAgentState) -> TeachingAgentState:
    state = detect_intent(state)
    state = rewrite_query(state)
    state = await retrieve_context(state)
    state = await generate_answer(state)
    state = plan_next_action(state)
    return state


async def _record_result(state: TeachingAgentState) -> None:
    await asyncio.to_thread(
        record_interaction,
        kind="chat",
        course_id=state.get("course_id", ""),
        lesson_id=state.get("lesson_id"),
        question=state.get("question", ""),
        answer=state.get("answer", ""),
    )


def _try_compile_graph():
    try:
        from langgraph.graph import END, StateGraph

        graph = StateGraph(TeachingAgentState)
        graph.add_node("detect_intent", detect_intent)
        graph.add_node("rewrite_query", rewrite_query)
        graph.add_node("retrieve_context", retrieve_context)
        graph.add_node("generate_answer", generate_answer)
        graph.add_node("plan_next_action", plan_next_action)
        graph.set_entry_point("detect_intent")
        graph.add_edge("detect_intent", "rewrite_query")
        graph.add_edge("rewrite_query", "retrieve_context")
        graph.add_edge("retrieve_context", "generate_answer")
        graph.add_edge("generate_answer", "plan_next_action")
        graph.add_edge("plan_next_action", END)
        return graph.compile()
    except Exception:
        return None
