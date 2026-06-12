from typing import Any, Literal

from pydantic import BaseModel, Field


class LessonSummary(BaseModel):
    id: str
    title: str
    duration: str
    status: Literal["done", "active", "locked"]
    tags: list[str]
    source: str | None = None


class CourseSummary(BaseModel):
    id: str
    title: str
    subtitle: str
    progress: int
    lessons: list[LessonSummary]


class PracticeTask(BaseModel):
    title: str
    description: str
    template: str
    checklist: list[str]


class LessonDetail(BaseModel):
    id: str
    course_id: str | None = None
    title: str
    summary: str
    objectives: list[str]
    content: str
    practice: PracticeTask
    source: str | None = None


class Citation(BaseModel):
    title: str
    source: str
    snippet: str
    score: float = 0
    course_id: str | None = None
    lesson_id: str | None = None
    kind: str = "chunk"


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    course_id: str
    lesson_id: str | None = None
    mode: Literal["student", "teacher"] = "student"


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    suggestions: list[str]
    fallback: bool = False


class PracticeSubmission(BaseModel):
    course_id: str
    lesson_id: str
    code: str = Field(min_length=1)
    notes: str = ""


class PracticeFeedback(BaseModel):
    score: int
    strengths: list[str]
    improvements: list[str]
    ai_comment: str
    citations: list[Citation]
    fallback: bool = False


class IngestResponse(BaseModel):
    chunks: int
    backend: str
    message: str


class HealthResponse(BaseModel):
    status: str
    database: bool
    rag_backend: str
    rag_config: dict[str, Any]
    deepseek_configured: bool
    deepseek_live: bool
    model: str


class AgentSkillInfo(BaseModel):
    name: str
    title: str
    description: str
    input_schema: dict
    output_type: str


class AgentSkillRunRequest(BaseModel):
    name: str
    arguments: dict = Field(default_factory=dict)


class AgentSkillRunResponse(BaseModel):
    name: str
    title: str
    result: dict
    citations: list[Citation] = Field(default_factory=list)
    fallback: bool = False


# ---------- 题库模型 ----------

class QuestionOption(BaseModel):
    key: str       # "A" / "B" / "C" / "D"
    text: str      # 选项文本


class Question(BaseModel):
    id: str                           # 唯一ID，如 "q-maven-001"
    course_id: str                    # 所属课程
    lesson_id: str                    # 所属章节
    type: Literal["single_choice", "multi_choice", "true_false", "short_answer", "code_fill"]
    stem: str                         # 题干
    options: list[QuestionOption] | None = None   # 选择题/判断题必有
    answer: str                       # 正确答案：A / AB / true / 简述要点 / 代码片段
    explanation: str | None = None    # 解析/评分要点
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    tags: list[str] = Field(default_factory=list)


class QuestionCreateRequest(BaseModel):
    course_id: str
    lesson_id: str
    type: Literal["single_choice", "multi_choice", "true_false", "short_answer", "code_fill"]
    stem: str = Field(min_length=1)
    options: list[QuestionOption] | None = None
    answer: str
    explanation: str | None = None
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    tags: list[str] = Field(default_factory=list)


class QuestionListResponse(BaseModel):
    questions: list[Question]
    total: int
