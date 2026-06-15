from __future__ import annotations

import asyncio
import re
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
    user_question: str
    mode: str
    intent: str
    rewritten_query: str
    citations: list[Citation]
    answer: str
    fallback: bool
    next_action: str


TECH_TERMS = {
    "ioc", "di", "aop", "bean", "spring", "springboot", "springboot", "controller", "service", "mapper",
    "mybatis", "mysql", "sql", "rest", "api", "jwt", "token", "session", "vue", "pinia",
    "maven", "java", "jdbc", "crud", "orm", "http", "json", "xml", "html", "css", "javascript",
    "git", "docker", "redis", "nginx", "tomcat", "linux", "windows", "ide", "idea", "vscode",
    "pom", "gradle", "jar", "war", "servlet", "filter", "interceptor", "annotation", "thread",
    "class", "object", "interface", "abstract", "extends", "implements", "override", "static",
    "final", "public", "private", "protected", "return", "void", "string", "integer", "list",
    "map", "set", "array", "exception", "try", "catch", "throw", "finally", "import", "package",
    "事务", "注入", "依赖", "控制反转", "切面", "日志", "接口", "字段", "数据库", "表",
    "登录", "认证", "分页", "查询", "新增", "修改", "删除", "上传", "配置", "异常",
    "前端", "后端", "框架", "组件", "路由", "状态", "请求", "响应", "缓存", "会话",
    "编译", "打包", "部署", "测试", "调试", "运行", "启动", "关闭", "连接", "断开",
}


def create_initial_state(request: ChatRequest) -> TeachingAgentState:
    user_question = extract_user_question(request.question)
    return {
        "course_id": request.course_id,
        "lesson_id": request.lesson_id,
        "question": request.question,
        "user_question": user_question,
        "mode": request.mode,
    }


def extract_user_question(question: str) -> str:
    match = re.search(r"学生问题：(?P<text>.+)$", question, re.S)
    return (match.group("text") if match else question).strip()


def is_low_information_question(question: str) -> bool:
    text = extract_user_question(question).strip().lower()
    if not text:
        return True
    if re.fullmatch(r"[\d\W_]+", text):
        return True
    if re.fullmatch(r"(test|测试|1+|12+|123+|a+|你好|hello|hi)", text, re.I):
        return True

    # long questions (5+ words) pass directly
    word_count = len(re.findall(r"[a-z][a-z0-9_+-]*|[一-鿿]+", text))
    if word_count >= 5:
        return False

    chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)
    latin_tokens = re.findall(r"[a-z][a-z0-9_+-]*", text)
    has_known_term = any(term in text for term in TECH_TERMS)

    if latin_tokens and not chinese_chars and not has_known_term:
        return True
    if len(chinese_chars) < 2 and not has_known_term:
        return True
    return False


async def run_agent_once(request: ChatRequest) -> TeachingAgentState:
    state = create_initial_state(request)
    if is_low_information_question(state["user_question"]):
        raise NoCitationError("请把问题写具体一点。")
    graph = _try_compile_graph()
    if graph is not None:
        _patch_langchain_debug_compat()
        try:
            result = await graph.ainvoke(state)
        except AttributeError as exc:
            if "debug" not in str(exc):
                raise
            result = await _manual_flow(state)
    else:
        result = await _manual_flow(state)
    await _record_result(result)
    return result


async def stream_agent(request: ChatRequest):
    state = create_initial_state(request)
    if is_low_information_question(state["user_question"]):
        raise NoCitationError("请把问题写具体一点。")

    yield "status", {"stage": "intent", "message": "正在判断学习意图..."}
    state = detect_intent(state)

    yield "status", {"stage": "rewrite", "message": "正在整理问题..."}
    state = rewrite_query(state)

    yield "status", {"stage": "retrieving", "message": "正在检索课程资料..."}
    state = await retrieve_context(state)
    if not state.get("citations"):
        raise NoCitationError("没有检索到可用于回答的课程资料。")

    yield "status", {"stage": "generating", "message": "正在组织回答..."}
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
    yield "done", {
        "answer": state["answer"],
        "next_action": state.get("next_action", ""),
        "citations": [citation.model_dump() for citation in state.get("citations", [])],
    }


def detect_intent(state: TeachingAgentState) -> TeachingAgentState:
    question = state["user_question"]
    if any(word in question for word in ["提示", "不会", "卡住", "怎么写"]):
        state["intent"] = "hint"
    elif any(word in question for word in ["为什么", "原理", "区别", "解释", "是什么", "什么是"]):
        state["intent"] = "explain"
    elif any(word in question for word in ["检查", "评价", "改错", "哪里错"]):
        state["intent"] = "diagnose"
    else:
        state["intent"] = "qa"
    return state


def rewrite_query(state: TeachingAgentState) -> TeachingAgentState:
    state["rewritten_query"] = f"{state.get('intent', 'qa')} {state['user_question']}"
    return state


async def retrieve_context(state: TeachingAgentState) -> TeachingAgentState:
    query = state.get("rewritten_query") or state["user_question"]
    citations = await asyncio.to_thread(
        rag_service.search,
        query,
        None,
        state.get("lesson_id"),
        state.get("course_id"),
    )
    if _needs_concept_fallback(state["user_question"], citations):
        extra = await asyncio.to_thread(rag_service.search, query, None, state.get("lesson_id"), None)
        citations = _merge_citations(extra, citations)
    citations = [citation for citation in citations if _concept_relevant(state["user_question"], citation)]
    state["citations"] = citations
    return state


def _needs_concept_fallback(question: str, citations: list[Citation]) -> bool:
    lowered = question.lower()
    if not any(keyword in lowered for keyword in ["ioc", "di", "aop", "bean", "mybatis", "控制反转", "依赖注入"]):
        return False
    joined = " ".join(f"{item.title} {item.snippet}" for item in citations).lower()
    return not any(keyword in joined for keyword in ["控制反转", "依赖注入"])


def _merge_citations(primary: list[Citation], secondary: list[Citation]) -> list[Citation]:
    seen = set()
    merged: list[Citation] = []
    for citation in [*primary, *secondary]:
        key = (citation.kind, citation.source, citation.title, citation.snippet[:40])
        if key in seen:
            continue
        seen.add(key)
        merged.append(citation)
    return merged[:4]


def _concept_relevant(question: str, citation: Citation) -> bool:
    lowered = question.lower()
    if not any(keyword in lowered for keyword in ["ioc", "di", "aop", "bean", "控制反转", "依赖注入"]):
        return True
    text = f"{citation.title} {citation.snippet}".lower()
    return any(keyword in text for keyword in ["ioc", "di", "aop", "bean", "控制反转", "依赖注入", "autowired", "spring 容器"])


async def generate_answer(state: TeachingAgentState) -> TeachingAgentState:
    if not state.get("citations"):
        raise NoCitationError("没有检索到可用于回答的课程资料。")
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
        state["next_action"] = "先补全右侧当前任务需要的关键片段，再提交检查。"
    elif intent == "diagnose":
        state["next_action"] = "把你的代码、报错或运行现象写进补全区，再提交检查。"
    else:
        state["next_action"] = "继续阅读任务说明，并尝试用自己的话复述关键调用链。"
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
        question=state.get("user_question", state.get("question", "")),
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


def _patch_langchain_debug_compat() -> None:
    try:
        import langchain

        if not hasattr(langchain, "debug"):
            langchain.debug = False
    except Exception:
        return
