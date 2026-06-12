from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from backend.app.data.courses import COURSE_ID, get_lesson
from backend.app.models import AgentSkillInfo, AgentSkillRunResponse, Citation
from backend.app.services.analytics import teacher_analytics
from backend.app.services.practice import evaluate_practice
from backend.app.services.rag import rag_service


SkillHandler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


@dataclass(frozen=True)
class AgentSkill:
    name: str
    title: str
    description: str
    input_schema: dict[str, Any]
    output_type: str
    handler: SkillHandler

    def info(self) -> AgentSkillInfo:
        return AgentSkillInfo(
            name=self.name,
            title=self.title,
            description=self.description,
            input_schema=self.input_schema,
            output_type=self.output_type,
        )


async def search_course_knowledge(arguments: dict[str, Any]) -> dict[str, Any]:
    query = str(arguments.get("query") or "")
    course_id = str(arguments.get("course_id") or COURSE_ID)
    lesson_id = arguments.get("lesson_id")
    limit = int(arguments.get("limit") or 4)
    citations = rag_service.search(query, limit=limit, lesson_id=lesson_id, course_id=course_id)
    return {
        "summary": f"已基于课程知识库检索到 {len(citations)} 条引用。",
        "citations": [citation.model_dump() for citation in citations],
        "rag": rag_service.status(),
    }


async def diagnose_practice(arguments: dict[str, Any]) -> dict[str, Any]:
    course_id = str(arguments.get("course_id") or COURSE_ID)
    lesson_id = str(arguments.get("lesson_id") or get_lesson(course_id).id)
    code = str(arguments.get("code") or "未提供代码")
    notes = str(arguments.get("notes") or "未提供说明")
    feedback = await evaluate_practice(course_id, lesson_id, code, notes)
    return feedback.model_dump()


async def teacher_snapshot(arguments: dict[str, Any]) -> dict[str, Any]:
    analytics = teacher_analytics()
    return {
        "summary": analytics["summary"],
        "weakPoints": analytics["weakPoints"][:5],
        "hotQuestions": analytics["hotQuestions"][:5],
        "interventions": analytics["interventions"][:4],
    }


async def lesson_brief(arguments: dict[str, Any]) -> dict[str, Any]:
    course_id = str(arguments.get("course_id") or COURSE_ID)
    lesson = get_lesson(course_id, arguments.get("lesson_id"))
    return {
        "lesson": lesson.model_dump(),
        "recommended_prompts": [
            f"用调用链解释「{lesson.title}」",
            "列出本节最容易混淆的两个概念",
            "生成一道课堂追问题，并给出评分标准",
        ],
    }


SKILLS: dict[str, AgentSkill] = {
    "course_knowledge_search": AgentSkill(
        name="course_knowledge_search",
        title="课程知识检索",
        description="基于当前章节、结构化知识点卡片、向量检索和关键词兜底返回课程引用。",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "学生或教师提出的问题"},
                "course_id": {"type": "string", "description": "课程 ID"},
                "lesson_id": {"type": "string", "description": "当前章节 ID，可用于章节加权"},
                "limit": {"type": "integer", "default": 4},
            },
            "required": ["query"],
        },
        output_type="citations",
        handler=search_course_knowledge,
    ),
    "practice_diagnose": AgentSkill(
        name="practice_diagnose",
        title="练习诊断",
        description="对学生代码片段、选择题说明和反思文本进行规则反馈与 AI 建议。",
        input_schema={
            "type": "object",
            "properties": {
                "lesson_id": {"type": "string"},
                "course_id": {"type": "string"},
                "code": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": ["lesson_id", "code"],
        },
        output_type="practice_feedback",
        handler=diagnose_practice,
    ),
    "teacher_snapshot": AgentSkill(
        name="teacher_snapshot",
        title="学情快照",
        description="汇总活跃度、热点问题、薄弱点和教师干预建议。",
        input_schema={"type": "object", "properties": {}},
        output_type="analytics",
        handler=teacher_snapshot,
    ),
    "lesson_brief": AgentSkill(
        name="lesson_brief",
        title="章节教案摘要",
        description="返回当前章节目标、任务、代码片段和推荐追问，可作为 AI 助教上下文。",
        input_schema={
            "type": "object",
            "properties": {"course_id": {"type": "string"}, "lesson_id": {"type": "string"}},
        },
        output_type="lesson",
        handler=lesson_brief,
    ),
}


def list_skills() -> list[AgentSkillInfo]:
    return [skill.info() for skill in SKILLS.values()]


async def run_skill(name: str, arguments: dict[str, Any]) -> AgentSkillRunResponse:
    skill = SKILLS.get(name)
    if skill is None:
        raise KeyError(name)
    result = await skill.handler(arguments)
    citations = [Citation(**item) for item in result.get("citations", []) if isinstance(item, dict)]
    return AgentSkillRunResponse(
        name=skill.name,
        title=skill.title,
        result=result,
        citations=citations,
        fallback=bool(result.get("fallback", False)),
    )
