import asyncio
import json
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.app.config import get_settings
from backend.app.data.courses import get_courses, get_lesson
from backend.app.models import (
    ChatRequest,
    ChatResponse,
    AIChatTaskRequest,
    AICheckRequest,
    AICheckResponse,
    AgentSkillRunRequest,
    AgentSkillRunResponse,
    CourseLineSummary,
    HealthResponse,
    IngestResponse,
    LearningMapResponse,
    LearningRecord,
    LearningTaskDetail,
    PracticeFeedback,
    PracticeSubmission,
    SelfCheckSubmission,
    SessionBootstrapResponse,
    SessionLoginRequest,
    UserInfo,
)
from backend.app.services.analytics import teacher_analytics
from backend.app.services.agent_tools import list_skills, run_skill
from backend.app.services.agent_flow import NoCitationError, run_agent_once, stream_agent
from backend.app.services.ai_check import check_learning_task
from backend.app.services.course_runtime import (
    get_course_line,
    get_learning_map,
    get_task_detail,
    list_course_lines,
    sync_course_runtime_seed,
)
from backend.app.services.database import (
    db_exists,
    get_user,
    init_db,
    list_classes,
    list_users,
    record_interaction,
    record_learning_event,
    student_records,
)
from backend.app.services.llm import LLMError, deepseek_client
from backend.app.services.practice import evaluate_practice
from backend.app.services.rag import rag_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    sync_course_runtime_seed()
    rag_service.ingest_seed()
    yield


app = FastAPI(title="Web Training Platform", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        database=db_exists(),
        rag_backend=rag_service.backend_name,
        rag_config=rag_service.status(),
        deepseek_configured=deepseek_client.configured,
        deepseek_live=settings.deepseek_live,
        model=settings.deepseek_model,
    )


@app.get("/api/courses")
async def courses() -> dict:
    return {"courses": get_courses()}


@app.get("/api/courses/{course_id}/lessons/{lesson_id}")
async def lesson(course_id: str, lesson_id: str) -> dict:
    return {"lesson": get_lesson(course_id, lesson_id)}


@app.get("/api/course-lines", response_model=list[CourseLineSummary])
async def course_lines() -> list[CourseLineSummary]:
    return await asyncio.to_thread(list_course_lines)


@app.get("/api/course-lines/{course_line_id}", response_model=CourseLineSummary)
async def course_line(course_line_id: str) -> CourseLineSummary:
    return await asyncio.to_thread(get_course_line, course_line_id)


@app.get("/api/course-lines/{course_line_id}/learning-map", response_model=LearningMapResponse)
async def learning_map(course_line_id: str, student_id: str | None = None) -> LearningMapResponse:
    return await asyncio.to_thread(get_learning_map, course_line_id, student_id)


@app.get("/api/tasks/{task_id}", response_model=LearningTaskDetail)
async def task_detail(task_id: str) -> LearningTaskDetail:
    return await asyncio.to_thread(get_task_detail, task_id)


@app.get("/api/session/bootstrap", response_model=SessionBootstrapResponse)
async def session_bootstrap() -> SessionBootstrapResponse:
    classes = [dict(row) for row in await asyncio.to_thread(list_classes)]
    class_names = {item["id"]: item["name"] for item in classes}
    users = []
    for row in await asyncio.to_thread(list_users):
        item = dict(row)
        item["class_name"] = class_names.get(item.get("class_id"))
        users.append(item)
    return SessionBootstrapResponse(classes=classes, users=users)


@app.post("/api/session/login", response_model=UserInfo)
async def session_login(request: SessionLoginRequest) -> UserInfo:
    row = await asyncio.to_thread(get_user, request.user_id)
    if not row:
        raise HTTPException(status_code=404, detail="user not found")
    item = dict(row)
    classes = {row["id"]: row["name"] for row in await asyncio.to_thread(list_classes)}
    item["class_name"] = classes.get(item.get("class_id"))
    return UserInfo(**item)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        result = await run_agent_once(request)
    except NoCitationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except LLMError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return ChatResponse(
        answer=result.get("answer", ""),
        citations=result.get("citations", []),
        suggestions=[result.get("next_action", "")] if result.get("next_action") else [],
        fallback=result.get("fallback", False),
    )


@app.post("/api/ai/chat", response_model=ChatResponse)
async def ai_chat(request: AIChatTaskRequest) -> ChatResponse:
    chat_request = ChatRequest(
        course_id=request.courseLineId,
        lesson_id=request.taskId,
        question=request.question,
        mode="student",
        student_id=request.studentId,
    )
    return await chat(chat_request)


@app.post("/api/ai/hint", response_model=ChatResponse)
async def ai_hint(request: AIChatTaskRequest) -> ChatResponse:
    request.question = f"请只围绕当前任务给一到两步提示，不要直接给完整答案。问题：{request.question}"
    return await ai_chat(request)


@app.post("/api/ai/reflect", response_model=ChatResponse)
async def ai_reflect(request: AIChatTaskRequest) -> ChatResponse:
    request.question = f"请帮助学生基于当前任务生成学习复盘，不要编造资料。学生内容：{request.question}"
    return await ai_chat(request)


@app.post("/api/ai/check", response_model=AICheckResponse)
async def ai_check(request: AICheckRequest) -> AICheckResponse:
    try:
        return await check_learning_task(request)
    except NoCitationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except LLMError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    async def event_stream():
        try:
            async for event, data in stream_agent(request):
                yield _sse(event, data)
        except NoCitationError as exc:
            yield _sse("error", {"message": str(exc), "status": 422})
        except LLMError as exc:
            yield _sse("error", {"message": str(exc), "status": exc.status_code})
        except Exception as exc:
            yield _sse("error", {"message": "AI 调用失败。", "detail": str(exc), "status": 500})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/practice/submit", response_model=PracticeFeedback)
async def practice_submit(request: PracticeSubmission) -> PracticeFeedback:
    try:
        feedback = await evaluate_practice(request.course_id, request.lesson_id, request.code, request.notes)
    except NoCitationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except LLMError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    await asyncio.to_thread(
        record_interaction,
        kind="practice",
        course_id=request.course_id,
        lesson_id=request.lesson_id,
        question=request.notes or "practice submission",
        answer=feedback.ai_comment,
        score=feedback.score,
        student_id=request.student_id,
    )
    if request.student_id:
        await asyncio.to_thread(
            record_learning_event,
            student_id=request.student_id,
            course_id=request.course_id,
            lesson_id=request.lesson_id,
            kind="ai_practice",
            score=feedback.score,
            code=request.code,
            notes=request.notes,
            feedback=feedback.ai_comment,
        )
    return feedback


@app.post("/api/learning/self-check")
async def learning_self_check(request: SelfCheckSubmission) -> dict:
    await asyncio.to_thread(
        record_learning_event,
        student_id=request.student_id,
        course_id=request.course_id,
        lesson_id=request.lesson_id,
        kind="self_check",
        score=request.score,
        correct=request.correct,
        total=request.total,
        answers=request.answers,
    )
    return {"ok": True}


@app.get("/api/students/{student_id}/records")
async def student_learning_records(student_id: str, course_id: str | None = None) -> dict[str, list[LearningRecord]]:
    rows = await asyncio.to_thread(student_records, student_id, course_id)
    return {"records": [_learning_record_from_row(row) for row in rows]}


@app.post("/api/kb/ingest", response_model=IngestResponse)
async def ingest() -> IngestResponse:
    chunks = await asyncio.to_thread(rag_service.ingest_seed)
    return IngestResponse(chunks=chunks, backend=rag_service.backend_name, message="真实课程资料知识库已就绪")


@app.post("/api/kb/upload", response_model=IngestResponse)
async def kb_upload(file: UploadFile = File(...)) -> IngestResponse:
    settings = get_settings()
    safe_name = Path(file.filename or "upload.md").name
    suffix = Path(safe_name).suffix.lower()
    content_bytes = await file.read()
    if len(content_bytes) > settings.upload_max_bytes:
        raise HTTPException(status_code=413, detail=f"file too large, max {settings.upload_max_bytes} bytes")
    target = settings.upload_dir / safe_name
    await asyncio.to_thread(target.write_bytes, content_bytes)

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader

            content = await asyncio.to_thread(_extract_pdf_text, target)
        except Exception as exc:
            raise HTTPException(status_code=400, detail="PDF parsing failed") from exc
    else:
        content = content_bytes.decode("utf-8", errors="ignore")

    chunks = await asyncio.to_thread(rag_service.add_document, target.name, content)
    return IngestResponse(chunks=chunks, backend=rag_service.backend_name, message="uploaded document indexed")


# ---------- 题库 API ----------

from backend.app.data.questions import SEED_QUESTIONS, questions_by_lesson, questions_by_course
from backend.app.models import Question, QuestionCreateRequest, QuestionListResponse

TEACHER_QUESTIONS: dict[str, Question] = {}  # 教师手动添加的题目


def _all_questions(course_id: str) -> list[Question]:
    """合并种子题 + 教师添加的题"""
    seed = questions_by_course(course_id)
    teacher = [q for q in TEACHER_QUESTIONS.values() if q.course_id == course_id]
    return seed + teacher


@app.get("/api/questions", response_model=QuestionListResponse)
async def get_questions(course_id: str, lesson_id: str | None = None) -> QuestionListResponse:
    all_qs = _all_questions(course_id)
    if lesson_id:
        all_qs = [q for q in all_qs if q.lesson_id == lesson_id]
    return QuestionListResponse(questions=all_qs, total=len(all_qs))


@app.post("/api/questions", response_model=Question)
async def create_question(request: QuestionCreateRequest) -> Question:
    import uuid
    qid = f"teacher-{uuid.uuid4().hex[:8]}"
    q = Question(id=qid, **request.model_dump())
    TEACHER_QUESTIONS[qid] = q
    return q


@app.put("/api/questions/{question_id}", response_model=Question)
async def update_question(question_id: str, request: QuestionCreateRequest) -> Question:
    if question_id not in TEACHER_QUESTIONS:
        raise HTTPException(status_code=404, detail="question not found (seed questions are read-only)")
    q = Question(id=question_id, **request.model_dump())
    TEACHER_QUESTIONS[question_id] = q
    return q


@app.delete("/api/questions/{question_id}")
async def delete_question(question_id: str) -> dict:
    if question_id not in TEACHER_QUESTIONS:
        raise HTTPException(status_code=404, detail="question not found or seed questions cannot be deleted")
    del TEACHER_QUESTIONS[question_id]
    return {"deleted": question_id}


@app.get("/api/agent/skills")
async def agent_skills() -> dict:
    return {"skills": list_skills()}


@app.post("/api/agent/run", response_model=AgentSkillRunResponse)
async def agent_run(request: AgentSkillRunRequest) -> AgentSkillRunResponse:
    try:
        return await run_skill(request.name, request.arguments)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="skill not found") from exc
    except NoCitationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except LLMError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@app.get("/api/teacher/analytics")
async def analytics() -> dict:
    return await asyncio.to_thread(teacher_analytics)


@app.get("/api/teacher/course-lines/{course_line_id}/analytics")
async def course_line_analytics(course_line_id: str) -> dict:
    analytics_data = await asyncio.to_thread(teacher_analytics)
    analytics_data["courseLine"] = (await asyncio.to_thread(get_course_line, course_line_id)).model_dump()
    return analytics_data


def _extract_pdf_text(target: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(target))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _learning_record_from_row(row) -> LearningRecord:
    item = dict(row)
    try:
        item["answers"] = json.loads(item.pop("answers_json") or "[]")
    except json.JSONDecodeError:
        item["answers"] = []
    return LearningRecord(**item)
