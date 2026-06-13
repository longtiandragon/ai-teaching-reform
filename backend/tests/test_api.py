from fastapi.testclient import TestClient

from backend.app.data.courses import NONGBO_COURSE_ID, SPRINGBOOT_COURSE_ID
from backend.app.main import app
from backend.app.services.llm import deepseek_client


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
    response = client.get(f"/api/course-lines/{NONGBO_COURSE_ID}/learning-map?student_id=stu-240101")
    assert response.status_code == 200
    data = response.json()
    assert data["courseLineId"] == NONGBO_COURSE_ID
    assert data["tasks"]
    assert data["tasks"][0]["title"] == "需求理解"
    assert data["tasks"][0]["status"] in {"active", "completed", "needs_revision"}


def test_task_detail_includes_rubrics() -> None:
    response = client.get("/api/tasks/task-course-table-design")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "数据库设计"
    assert data["rubrics"]
    assert any(rubric["required"] for rubric in data["rubrics"])


def test_ai_check_fails_without_live_deepseek_after_real_rag() -> None:
    client.post("/api/kb/ingest")
    response = client.post(
        "/api/ai/check",
        json={
            "courseLineId": NONGBO_COURSE_ID,
            "moduleId": "nongbo-lecture-course-management",
            "taskId": "task-requirement-understanding",
            "studentId": "stu-240101",
            "artifactType": "text",
            "studentInput": "农科讲堂需要课程列表、课程详情、搜索、推荐课程、专家关联和在线学习。",
            "attachments": [],
            "chatHistory": [],
        },
    )
    assert response.status_code == 503
    assert "DeepSeek" in response.json()["detail"]
