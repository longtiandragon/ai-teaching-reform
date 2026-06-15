from fastapi.testclient import TestClient
from uuid import uuid4

from backend.app.data.courses import NONGBO_COURSE_ID, SPRINGBOOT_COURSE_ID
from backend.app.main import app
from backend.app.models import Citation
from backend.app.services.llm import deepseek_client
from backend.app.services.rag import rag_service
from backend.app.services.web_search import WebSearchNotConfiguredError, web_search_service


client = TestClient(app)
deepseek_client.settings.deepseek_api_key = ""
deepseek_client.settings.deepseek_live = False


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model"]


def test_courses_are_real_two_track_courses() -> None:
    response = client.get("/api/courses")
    assert response.status_code == 200
    courses = response.json()["courses"]
    assert [course["id"] for course in courses] == [SPRINGBOOT_COURSE_ID, NONGBO_COURSE_ID]
    assert len(courses[0]["lessons"]) == 12
    assert len(courses[1]["lessons"]) == 12
    assert courses[0]["lessons"][0]["source"].startswith("docs/course-materials/")


def test_springboot_lesson_comes_from_course_materials() -> None:
    courses = client.get("/api/courses").json()["courses"]
    lesson_id = courses[0]["lessons"][0]["id"]
    lesson = client.get(f"/api/courses/{SPRINGBOOT_COURSE_ID}/lessons/{lesson_id}").json()["lesson"]
    assert lesson["course_id"] == SPRINGBOOT_COURSE_ID
    assert "docs/course-materials/" in lesson["source"]
    assert lesson["practice"]["checklist"]


def test_nongbo_lesson_uses_real_project_style() -> None:
    response = client.get(f"/api/courses/{NONGBO_COURSE_ID}/lessons/nongbo-login-auth")
    assert response.status_code == 200
    lesson = response.json()["lesson"]
    template = lesson["practice"]["template"]
    assert lesson["course_id"] == NONGBO_COURSE_ID
    assert "com.movie.nbspringproduct" in template
    assert "Result" in template
    assert "Service" in template or "service" in template


def test_ingest_indexes_real_sources_and_search_is_course_scoped() -> None:
    ingest = client.post("/api/kb/ingest")
    assert ingest.status_code == 200
    assert ingest.json()["chunks"] >= 24

    spring = client.post(
        "/api/agent/run",
        json={
            "name": "course_knowledge_search",
            "arguments": {
                "course_id": SPRINGBOOT_COURSE_ID,
                "query": "Maven 依赖管理",
                "limit": 3,
            },
        },
    )
    assert spring.status_code == 200
    spring_citations = spring.json()["citations"]
    assert spring_citations
    assert all(item["course_id"] in (SPRINGBOOT_COURSE_ID, None) for item in spring_citations)

    nongbo = client.post(
        "/api/agent/run",
        json={
            "name": "course_knowledge_search",
            "arguments": {
                "course_id": NONGBO_COURSE_ID,
                "query": "AuthController 登录 Result",
                "limit": 3,
            },
        },
    )
    assert nongbo.status_code == 200
    nongbo_citations = nongbo.json()["citations"]
    assert nongbo_citations
    assert all(item["course_id"] in (NONGBO_COURSE_ID, None) for item in nongbo_citations)


def test_chat_fails_without_live_deepseek_instead_of_fallback() -> None:
    client.post("/api/kb/ingest")
    response = client.post(
        "/api/chat",
        json={
            "course_id": SPRINGBOOT_COURSE_ID,
            "lesson_id": "springboot-03-maven-basic",
            "question": "Maven 坐标是什么？",
        },
    )
    assert response.status_code == 503
    assert "DeepSeek" in response.json()["detail"]


def test_practice_feedback_fails_without_live_deepseek_instead_of_fake_score() -> None:
    client.post("/api/kb/ingest")
    response = client.post(
        "/api/practice/submit",
        json={
            "course_id": NONGBO_COURSE_ID,
            "lesson_id": "nongbo-login-auth",
            "code": "return Result.success(sysUserService.login(loginDTO));",
            "notes": "沿用 AuthController、Result<T> 和 ISysUserService 登录流程。",
        },
    )
    assert response.status_code == 503
    assert "DeepSeek" in response.json()["detail"]


def test_learning_map_exposes_product_tasks() -> None:
    response = client.get(f"/api/course-lines/{NONGBO_COURSE_ID}/learning-map?student_id=stu-001")
    assert response.status_code == 200
    data = response.json()
    assert data["courseLineId"] == NONGBO_COURSE_ID
    assert data["tasks"]
    assert data["tasks"][0]["title"] == "业务需求梳理"
    assert data["tasks"][0]["status"] in {"active", "completed", "needs_revision"}


def test_task_detail_includes_rubrics() -> None:
    response = client.get("/api/tasks/task-requirement-understanding")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "业务需求梳理"
    assert data["rubrics"]
    assert any(rubric["required"] for rubric in data["rubrics"])


def test_ai_check_fails_without_live_deepseek_after_real_rag() -> None:
    client.post("/api/kb/ingest")
    response = client.post(
        "/api/ai/check",
        json={
            "courseLineId": NONGBO_COURSE_ID,
            "moduleId": "nongbo-m1-requirements",
            "taskId": "task-requirement-understanding",
            "studentId": "stu-001",
            "artifactType": "text",
            "studentInput": "农科讲堂需要课程列表、课程详情、搜索、推荐课程、专家关联和在线学习。",
            "attachments": [],
            "chatHistory": [],
        },
    )
    assert response.status_code == 503
    assert "DeepSeek" in response.json()["detail"]


def _create_project5_question() -> dict:
    response = client.post(
        "/api/questions",
        json={
            "course_id": NONGBO_COURSE_ID,
            "lesson_id": "nongbo-project5-guided-test",
            "type": "short_answer",
            "stem": f"Explain Vue Axios integration for project 5. {uuid4().hex}",
            "options": None,
            "answer": "Use Axios request/response interceptors, token headers, CORS, table pagination, and form dialogs.",
            "explanation": "Project 5 focuses on complete frontend/backend integration.",
            "difficulty": "medium",
            "tags": ["Vue", "Axios", "project5"],
        },
    )
    assert response.status_code == 200
    return response.json()


def _publish_to_project5(question_id: str) -> None:
    response = client.post(
        "/api/teacher/questions/publish",
        json={
            "questionId": question_id,
            "taskId": "task-frontend-integration",
            "courseLineId": NONGBO_COURSE_ID,
            "publishedBy": "teacher-20240036",
        },
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True


def _upload_project5_material() -> str:
    filename = f"project5-guided-{uuid4().hex}.md"
    content = (
        "Project 5 Vue frontend integration notes.\n"
        "request.ts should wrap Axios with request and response interceptors.\n"
        "Attach Token in headers, handle CORS, and normalize API response data.\n"
        "A list page should include Element Plus form search, el-table, pagination, and create dialog.\n"
    )
    response = client.post(
        "/api/kb/upload",
        data={"courseLineId": NONGBO_COURSE_ID, "taskId": "task-frontend-integration"},
        files={"file": (filename, content.encode("utf-8"), "text/markdown")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["chunks"] >= 1
    assert data["fileId"]
    return data["fileId"]


def test_published_tasks_endpoint_and_student_questions_include_teacher_question() -> None:
    question = _create_project5_question()
    _publish_to_project5(question["id"])

    published_tasks = client.get(f"/api/questions/{question['id']}/published-tasks")
    assert published_tasks.status_code == 200
    assert {
        "task_id": "task-frontend-integration",
        "course_line_id": NONGBO_COURSE_ID,
    } in published_tasks.json()["tasks"]

    student_view = client.get("/api/published-questions/task-frontend-integration")
    assert student_view.status_code == 200
    body = student_view.json()
    assert body["total"] >= 1
    assert any(item["id"] == question["id"] for item in body["questions"])


def test_upload_material_can_be_associated_to_project5_task() -> None:
    file_id = _upload_project5_material()

    task_files = client.get("/api/teacher/kb/task-files/task-frontend-integration")
    assert task_files.status_code == 200
    assert any(item["id"] == file_id for item in task_files.json()["files"])

    dissociate = client.request(
        "DELETE",
        "/api/teacher/kb/associate",
        json={"file_id": file_id, "task_id": "task-frontend-integration"},
    )
    assert dissociate.status_code == 200
    assert dissociate.json()["ok"] is True


def test_guided_start_and_message_use_uploaded_material_without_full_answer(monkeypatch) -> None:
    question = _create_project5_question()
    _publish_to_project5(question["id"])
    _upload_project5_material()

    async def fake_answer(prompt: str, citations: list[Citation], mode: str = "student") -> str:
        assert citations
        assert "完整" not in prompt or "不一次性" in prompt
        return (
            "## 本步目标\n"
            "先定位 request.ts 和列表页职责，不提供完整答案。\n"
            "## 资料依据\n"
            "依据任务资料中的 Axios、Token、CORS 和 Element Plus 列表页说明。\n"
            "## 局部示例与逐行解析\n"
            "`const service = axios.create()` 只建立请求实例。\n"
            "## 你现在要完成的小任务\n"
            "请先写出 request.ts 的拦截器要点。"
        )

    monkeypatch.setattr(deepseek_client, "answer", fake_answer)

    response = client.post(
        "/api/guided/start",
        json={
            "courseLineId": NONGBO_COURSE_ID,
            "moduleId": "nongbo-m5-fullstack",
            "taskId": "task-frontend-integration",
            "studentId": "stu-001",
            "studentInput": "帮我生成完整答案",
            "questionId": question["id"],
            "codeDraft": "",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sessionId"]
    assert data["intent"] == "request_answer"
    assert data["steps"]
    assert data["totalSteps"] == len(data["steps"])
    assert data["citations"]
    assert data["currentStepTitle"]
    assert "不提供完整答案" in data["message"]

    follow_up = client.post(
        "/api/guided/message",
        json={
            "sessionId": data["sessionId"],
            "studentId": "stu-001",
            "message": "我先写 request.ts 的拦截器。",
            "codeDraft": "const service = axios.create({ baseURL: '/api' })",
        },
    )
    assert follow_up.status_code == 200
    assert follow_up.json()["currentStep"] == 1


def test_guided_concept_question_stays_on_current_step_and_answers_directly(monkeypatch) -> None:
    question = _create_project5_question()
    _publish_to_project5(question["id"])
    _upload_project5_material()

    async def fake_search(query: str, limit: int | None = None) -> list[Citation]:
        return [
            Citation(
                title="数据库概念",
                source="https://example.com/database",
                snippet="数据库是按照一定结构组织、存储和管理数据的集合。",
                score=0.8,
                kind="web-search",
            )
        ]

    async def fake_answer(prompt: str, citations: list[Citation], mode: str = "student") -> str:
        if "什么是数据库" in prompt:
            assert "学生正在追问基础概念" in prompt
            return "## 本步目标\n先回答：数据库是按结构组织、存储和管理数据的集合。"
        return "## 本步目标\n开始读题。"

    monkeypatch.setattr(web_search_service, "search", fake_search)
    monkeypatch.setattr(deepseek_client, "answer", fake_answer)

    start = client.post(
        "/api/guided/start",
        json={
            "courseLineId": NONGBO_COURSE_ID,
            "moduleId": "nongbo-m5-fullstack",
            "taskId": "task-frontend-integration",
            "studentId": "stu-001",
            "studentInput": "请引导我做题",
            "questionId": question["id"],
        },
    )
    assert start.status_code == 200
    session_id = start.json()["sessionId"]

    follow_up = client.post(
        "/api/guided/message",
        json={
            "sessionId": session_id,
            "studentId": "stu-001",
            "message": "什么是数据库",
        },
    )
    assert follow_up.status_code == 200
    data = follow_up.json()
    assert data["currentStep"] == 0
    assert "数据库是" in data["message"]
    assert any(item["kind"] == "web-search" for item in data["citations"])


def test_guided_start_fails_when_no_local_material_and_web_search_disabled(monkeypatch) -> None:
    monkeypatch.setattr(rag_service, "search", lambda *args, **kwargs: [])

    async def unavailable_search(query: str, limit: int | None = None) -> list[Citation]:
        raise WebSearchNotConfiguredError("web search disabled")

    monkeypatch.setattr(web_search_service, "search", unavailable_search)

    response = client.post(
        "/api/guided/start",
        json={
            "courseLineId": NONGBO_COURSE_ID,
            "moduleId": "nongbo-m5-fullstack",
            "taskId": "task-frontend-integration",
            "studentId": "stu-001",
            "studentInput": "请引导我做题",
        },
    )
    assert response.status_code == 422
    assert "web search disabled" in response.json()["detail"]


def test_guided_start_uses_web_search_citation_when_local_material_is_missing(monkeypatch) -> None:
    monkeypatch.setattr(rag_service, "search", lambda *args, **kwargs: [])

    async def fake_search(query: str, limit: int | None = None) -> list[Citation]:
        return [
            Citation(
                title="Axios interceptors guide",
                source="https://example.com/axios-interceptors",
                snippet="Axios supports request and response interceptors for tokens and errors.",
                score=0.9,
                kind="web-search",
            )
        ]

    async def fake_answer(prompt: str, citations: list[Citation], mode: str = "student") -> str:
        assert citations[0].kind == "web-search"
        return "## 本步目标\n使用外部网页引用做分步引导，不给完整答案。"

    monkeypatch.setattr(web_search_service, "search", fake_search)
    monkeypatch.setattr(deepseek_client, "answer", fake_answer)

    response = client.post(
        "/api/guided/start",
        json={
            "courseLineId": NONGBO_COURSE_ID,
            "moduleId": "nongbo-m5-fullstack",
            "taskId": "task-frontend-integration",
            "studentId": "stu-001",
            "studentInput": "请帮我规划这道题",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["citations"][0]["kind"] == "web-search"
