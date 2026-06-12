from __future__ import annotations

import re
from collections import Counter
from datetime import UTC, datetime

from backend.app.data.courses import get_courses
from backend.app.services.database import interaction_rows
from backend.app.services.rag import rag_service


def teacher_analytics() -> dict:
    rows = [dict(row) for row in interaction_rows()]
    rag_status = rag_service.status()
    questions = [row["question"] or "" for row in rows if row["kind"] == "chat"]
    practice_rows = [row for row in rows if row["kind"] == "practice"]

    return {
        "summary": {
            "students": 0,
            "activeToday": _active_today(rows),
            "completionRate": 0,
            "aiQuestions": len(questions),
            "kbCoverage": _course_coverage_percent(rag_status),
            "interventionTasks": 0,
            "kbChunks": rag_status.get("chunks", 0),
        },
        "lessonProgress": _lesson_progress(rows),
        "hotQuestions": _hot_questions(questions),
        "weakPoints": _weak_points(practice_rows),
        "interventions": [],
        "knowledgeCoverage": _knowledge_coverage(rag_status),
        "recentInteractions": [
            {
                "kind": row["kind"],
                "courseId": row["course_id"],
                "lessonId": row["lesson_id"],
                "question": row["question"],
                "score": row["score"],
                "createdAt": row["created_at"],
            }
            for row in rows[:8]
        ],
    }


def _active_today(rows: list[dict]) -> int:
    today = datetime.now(UTC).date()
    count = 0
    for row in rows:
        try:
            created = datetime.fromisoformat(row["created_at"]).date()
        except (TypeError, ValueError):
            continue
        if created == today:
            count += 1
    return count


def _course_coverage_percent(rag_status: dict) -> int:
    courses = get_courses()
    course_counts = rag_status.get("course_counts") or {}
    if not courses:
        return 0
    covered = sum(1 for course in courses if int(course_counts.get(course.id, 0)) > 0)
    return round(covered / len(courses) * 100)


def _lesson_progress(rows: list[dict]) -> list[dict]:
    counts = Counter((row["course_id"], row["lesson_id"]) for row in rows if row.get("lesson_id"))
    if not counts:
        return []
    max_count = max(counts.values())
    lesson_titles = {
        (course.id, lesson.id): lesson.title
        for course in get_courses()
        for lesson in course.lessons
    }
    return [
        {
            "lesson": lesson_titles.get(key, key[1] or ""),
            "completed": round(count / max_count * 100),
            "interactions": count,
        }
        for key, count in counts.most_common(12)
    ]


def _hot_questions(questions: list[str]) -> list[dict]:
    words: Counter[str] = Counter()
    for question in questions:
        for token in re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z][A-Za-z0-9_+-]{2,}", question):
            if token.lower() in {"spring", "springboot", "boot", "java"}:
                continue
            words[token] += 1
    return [{"keyword": key, "count": count} for key, count in words.most_common(8)]


def _weak_points(practice_rows: list[dict]) -> list[dict]:
    low_scores = [row for row in practice_rows if row.get("score") is not None and int(row["score"]) < 70]
    if not low_scores:
        return []
    counts = Counter(row["lesson_id"] or "未标记章节" for row in low_scores)
    return [
        {"name": lesson_id, "value": min(100, count * 20)}
        for lesson_id, count in counts.most_common(8)
    ]


def _knowledge_coverage(rag_status: dict) -> list[dict]:
    kind_counts = rag_status.get("kind_counts") or {}
    total = sum(int(value) for value in kind_counts.values())
    if total <= 0:
        return []
    return [
        {"name": name, "covered": round(int(count) / total * 100), "chunks": int(count)}
        for name, count in sorted(kind_counts.items(), key=lambda item: int(item[1]), reverse=True)
    ]
