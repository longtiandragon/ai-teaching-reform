import json
import sys
from dataclasses import dataclass
from typing import Any
from urllib import request
from urllib.error import HTTPError, URLError


BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8001"
SPRINGBOOT_COURSE_ID = "springboot-course-12"
NONGBO_COURSE_ID = "nongbo-admin-project"


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


@dataclass
class ApiResult:
    status: int
    data: Any


def call(method: str, path: str, payload: dict[str, Any] | None = None, timeout: int = 40, retries: int = 2) -> ApiResult:
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    last_error: Exception | None = None
    for _ in range(retries + 1):
        req = request.Request(f"{BASE_URL}{path}", data=body, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=timeout) as response:
                content = response.read().decode("utf-8")
                return ApiResult(response.status, json.loads(content) if content else {})
        except HTTPError as exc:
            content = exc.read().decode("utf-8", errors="ignore")
            try:
                data = json.loads(content) if content else {}
            except json.JSONDecodeError:
                data = {"detail": content}
            return ApiResult(exc.code, data)
        except (URLError, TimeoutError) as exc:
            last_error = exc
    if last_error:
        raise last_error
    raise RuntimeError("request failed without an exception")


def check(name: str, fn) -> CheckResult:
    try:
        detail = fn()
        return CheckResult(name=name, ok=True, detail=detail)
    except (AssertionError, URLError, TimeoutError) as exc:
        return CheckResult(name=name, ok=False, detail=str(exc))


def main() -> int:
    results = [
        check("knowledge base ingest", lambda: validate_ingest(call("POST", "/api/kb/ingest"))),
        check("health", lambda: validate_health(call("GET", "/api/health"))),
        check("courses", lambda: validate_courses(call("GET", "/api/courses"))),
        check(
            "springboot citations",
            lambda: validate_search(
                call(
                    "POST",
                    "/api/agent/run",
                    {
                        "name": "course_knowledge_search",
                        "arguments": {"course_id": SPRINGBOOT_COURSE_ID, "query": "Maven 依赖管理", "limit": 3},
                    },
                ),
                SPRINGBOOT_COURSE_ID,
            ),
        ),
        check(
            "nongbo citations",
            lambda: validate_search(
                call(
                    "POST",
                    "/api/agent/run",
                    {
                        "name": "course_knowledge_search",
                        "arguments": {"course_id": NONGBO_COURSE_ID, "query": "AuthController Result 登录", "limit": 3},
                    },
                ),
                NONGBO_COURSE_ID,
            ),
        ),
        check(
            "strict chat path",
            lambda: validate_strict_ai(
                call(
                    "POST",
                    "/api/chat",
                    {
                        "course_id": SPRINGBOOT_COURSE_ID,
                        "lesson_id": "springboot-03-maven-basic",
                        "question": "Maven 坐标是什么？",
                    },
                )
            ),
        ),
        check(
            "strict practice path",
            lambda: validate_strict_practice(
                call(
                    "POST",
                    "/api/practice/submit",
                    {
                        "course_id": NONGBO_COURSE_ID,
                        "lesson_id": "nongbo-login-auth",
                        "code": "return Result.success(userService.getOne(wrapper));",
                        "notes": "沿用 AuthController、Result<T> 和 IxxxService 调用。",
                    },
                )
            ),
        ),
        check("teacher analytics", lambda: validate_analytics(call("GET", "/api/teacher/analytics"))),
    ]

    for result in results:
        mark = "PASS" if result.ok else "FAIL"
        print(f"[{mark}] {result.name}: {result.detail}")

    return 0 if all(result.ok for result in results) else 1


def validate_health(result: ApiResult) -> str:
    assert result.status == 200
    data = result.data
    assert data["status"] == "ok"
    assert data["database"] is True
    return f"rag={data['rag_backend']}, chunks={data['rag_config']['chunks']}, live={data['deepseek_live']}"


def validate_courses(result: ApiResult) -> str:
    assert result.status == 200
    courses = result.data["courses"]
    assert [course["id"] for course in courses] == [SPRINGBOOT_COURSE_ID, NONGBO_COURSE_ID]
    assert len(courses[0]["lessons"]) == 12
    assert len(courses[1]["lessons"]) == 12
    return "2 real courses / 24 lessons"


def validate_ingest(result: ApiResult) -> str:
    assert result.status == 200
    assert result.data["chunks"] >= 24
    return f"{result.data['chunks']} chunks via {result.data['backend']}"


def validate_search(result: ApiResult, course_id: str) -> str:
    assert result.status == 200
    citations = result.data["citations"]
    assert citations
    assert all(citation["course_id"] in (course_id, None) for citation in citations)
    return f"{len(citations)} scoped citations"


def validate_strict_ai(result: ApiResult) -> str:
    if result.status == 200:
        assert result.data["answer"]
        assert result.data["citations"]
        assert result.data["fallback"] is False
        return f"{len(result.data['citations'])} citations, live answer"
    assert result.status in {422, 502, 503, 504}
    assert result.data.get("detail")
    return f"strict failure {result.status}: {result.data['detail']}"


def validate_strict_practice(result: ApiResult) -> str:
    if result.status == 200:
        assert result.data["citations"]
        assert result.data["fallback"] is False
        return f"score={result.data['score']}"
    assert result.status in {422, 502, 503, 504}
    assert result.data.get("detail")
    return f"strict failure {result.status}: {result.data['detail']}"


def validate_analytics(result: ApiResult) -> str:
    assert result.status == 200
    data = result.data
    assert "summary" in data
    assert "knowledgeCoverage" in data
    assert data["summary"]["students"] == 0
    return f"chunks={data['summary'].get('kbChunks', 0)}, interactions={len(data['recentInteractions'])}"


if __name__ == "__main__":
    raise SystemExit(main())
