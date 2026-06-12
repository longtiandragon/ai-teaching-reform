import asyncio

from backend.app.data.courses import NONGBO_COURSE_ID, get_lesson
from backend.app.models import Citation, PracticeFeedback
from backend.app.services.agent_flow import NoCitationError
from backend.app.services.llm import deepseek_client
from backend.app.services.rag import rag_service


async def evaluate_practice(course_id: str, lesson_id: str, code: str, notes: str = "") -> PracticeFeedback:
    lesson = get_lesson(course_id, lesson_id)
    citations = await asyncio.to_thread(
        rag_service.search,
        f"{lesson.title} {lesson.practice.title} {notes} {code[:500]}",
        4,
        lesson_id,
        course_id,
    )
    if not citations:
        raise NoCitationError("练习评价没有检索到可引用资料，已停止评价。")

    strengths, improvements = _check_against_real_requirements(course_id, lesson.practice.checklist, code, notes)
    score = _score(strengths, improvements)
    ai_comment = await deepseek_client.answer(
        "\n".join(
            [
                f"请基于引用资料评价学生在《{lesson.title}》中的练习提交。",
                "必须说明依据，不要编造项目中不存在的代码。",
                f"真实验收清单：{lesson.practice.checklist}",
                f"已命中的要求：{strengths}",
                f"仍需改进：{improvements}",
                f"学生代码/说明：\n{code}\n{notes}",
            ]
        ),
        citations,
    )
    return PracticeFeedback(
        score=score,
        strengths=strengths,
        improvements=improvements,
        ai_comment=ai_comment,
        citations=citations,
        fallback=False,
    )


def _check_against_real_requirements(course_id: str, checklist: list[str], code: str, notes: str) -> tuple[list[str], list[str]]:
    text = f"{code}\n{notes}"
    strengths: list[str] = []
    improvements: list[str] = []
    for item in checklist:
        tokens = [token for token in _important_tokens(item) if len(token) >= 2]
        if tokens and any(token in text for token in tokens):
            strengths.append(item)
        else:
            improvements.append(item)

    if course_id == NONGBO_COURSE_ID:
        style_checks = [
            ("使用 Result<T> 统一返回结构", "Result" in text),
            ("沿用 /dev-api/yjnb 或真实控制器路径", "/dev-api" in text or "@RequestMapping" in text),
            ("保留 Service 调用边界", "Service" in text or "service" in text),
            ("体现 MyBatis-Plus 或 Mapper/Entity 结构", "Mapper" in text or "Entity" in text or "BaseMapper" in text),
        ]
        for label, ok in style_checks:
            (strengths if ok else improvements).append(label)

    return _dedupe(strengths), _dedupe(improvements)


def _score(strengths: list[str], improvements: list[str]) -> int:
    total = len(strengths) + len(improvements)
    if total == 0:
        return 0
    return round(len(strengths) / total * 100)


def _important_tokens(text: str) -> list[str]:
    separators = " /，。、；：:,.()（）<>`"
    tokens = [text]
    for separator in separators:
        tokens = [part for token in tokens for part in token.split(separator)]
    return [token.strip() for token in tokens if token.strip()]


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
