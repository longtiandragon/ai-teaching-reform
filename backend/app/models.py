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
    student_id: str | None = None


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
    student_id: str | None = None


class PracticeFeedback(BaseModel):
    score: int
    strengths: list[str]
    improvements: list[str]
    ai_comment: str
    citations: list[Citation]
    fallback: bool = False


class ClassInfo(BaseModel):
    id: str
    name: str
    course_id: str


class UserInfo(BaseModel):
    id: str
    name: str
    role: Literal["student", "teacher"]
    class_id: str | None = None
    class_name: str | None = None
    student_no: str | None = None


class SessionLoginRequest(BaseModel):
    user_id: str


class SessionBootstrapResponse(BaseModel):
    classes: list[ClassInfo]
    users: list[UserInfo]


class SelfCheckSubmission(BaseModel):
    student_id: str
    course_id: str
    lesson_id: str
    score: int
    correct: int
    total: int
    answers: list[dict[str, Any]] = Field(default_factory=list)


class LearningRecord(BaseModel):
    id: int
    student_id: str
    class_id: str | None = None
    course_id: str
    lesson_id: str
    kind: str
    score: int | None = None
    correct: int | None = None
    total: int | None = None
    code: str | None = None
    notes: str | None = None
    feedback: str | None = None
    answers: list[dict[str, Any]] = Field(default_factory=list)
    created_at: str


class IngestResponse(BaseModel):
    chunks: int
    backend: str
    message: str
    fileId: str | None = None


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


class RubricScore(BaseModel):
    criterion_id: str
    name: str
    type: str
    required: bool = False
    passed: bool
    score: int
    weight: int
    reason: str


class LearningTaskSummary(BaseModel):
    id: str
    module_id: str
    course_line_id: str
    title: str
    type: str
    status: Literal["completed", "active", "locked", "needs_revision"]
    progress: int = 0
    score: int | None = None
    required_artifact_type: str = "text"


class LearningModuleSummary(BaseModel):
    id: str
    course_line_id: str
    title: str
    description: str = ""
    business_context: str = ""
    progress: int = 0
    tasks: list[LearningTaskSummary] = Field(default_factory=list)


class CourseLineSummary(BaseModel):
    id: str
    slug: str
    title: str
    description: str
    target_audience: str = ""
    tech_stack: list[str] = Field(default_factory=list)
    status: str = "active"


class LearningMapResponse(BaseModel):
    courseLineId: str
    title: str
    description: str
    currentModule: dict[str, Any] | None = None
    modules: list[LearningModuleSummary]
    tasks: list[LearningTaskSummary]


class LearningTaskDetail(BaseModel):
    id: str
    module_id: str
    course_line_id: str
    title: str
    type: str
    goal: str
    scenario: str
    instruction: str
    required_artifact_type: str
    difficulty: int = 1
    unlock_policy: dict[str, Any] = Field(default_factory=dict)
    rubrics: list[dict[str, Any]] = Field(default_factory=list)


class AICheckRequest(BaseModel):
    courseLineId: str
    moduleId: str
    taskId: str
    studentId: str
    artifactType: str | None = None
    studentInput: str = Field(min_length=1)
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    chatHistory: list[dict[str, Any]] = Field(default_factory=list)


class AICheckProblem(BaseModel):
    type: str
    message: str
    suggestion: str = ""


class AICheckResponse(BaseModel):
    passed: bool
    score: int
    level: Literal["passed", "needs_revision", "blocked"]
    reply: str
    strengths: list[str] = Field(default_factory=list)
    problems: list[AICheckProblem] = Field(default_factory=list)
    nextActions: list[str] = Field(default_factory=list)
    evidence: list[Citation] = Field(default_factory=list)
    rubricScores: list[RubricScore] = Field(default_factory=list)
    nextTaskUnlocked: bool = False


class AIChatTaskRequest(BaseModel):
    courseLineId: str
    moduleId: str | None = None
    taskId: str | None = None
    studentId: str | None = None
    question: str = Field(min_length=1)
    chatHistory: list[dict[str, Any]] = Field(default_factory=list)


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


# ---------- 引导模式模型 ----------

class GuidedStartRequest(BaseModel):
    courseLineId: str
    moduleId: str
    taskId: str
    studentId: str
    studentInput: str = Field(min_length=1)
    questionId: str | None = None
    codeDraft: str | None = None


class GuidedMessageRequest(BaseModel):
    sessionId: str
    studentId: str
    message: str = Field(min_length=1)
    codeDraft: str | None = None


class GuidedStepResponse(BaseModel):
    title: str
    goal: str
    knowledge_points: list[str] = Field(default_factory=list)


class GuidedSessionResponse(BaseModel):
    sessionId: str
    intent: str = ""
    steps: list[GuidedStepResponse] = Field(default_factory=list)
    currentStep: int = 0
    totalSteps: int = 0
    currentStepTitle: str | None = None
    message: str = ""
    citations: list[Citation] = Field(default_factory=list)
    status: str = "waiting"
