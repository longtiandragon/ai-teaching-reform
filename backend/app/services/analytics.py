from __future__ import annotations

import re
from collections import Counter
from datetime import UTC, datetime

from backend.app.data.courses import get_courses
from backend.app.services.database import interaction_rows, latest_submission_rows, learning_rows, list_classes, list_users
from backend.app.services.rag import rag_service


def teacher_analytics(student_id: str | None = None) -> dict:
    interactions = [dict(row) for row in interaction_rows()]
    records = [dict(row) for row in learning_rows()]
    submissions = [dict(row) for row in latest_submission_rows()]
    classes = [dict(row) for row in list_classes()]
    users = [dict(row) for row in list_users()]
    students = [user for user in users if user["role"] == "student"]

    # 按学生筛选
    if student_id:
        interactions = [r for r in interactions if r.get("student_id") == student_id]
        records = [r for r in records if r.get("student_id") == student_id]
        submissions = [r for r in submissions if r.get("student_id") == student_id]
    rag_status = rag_service.status()
    questions = [row["question"] or "" for row in interactions if row["kind"] == "chat"]
    completed_pairs = {(row["student_id"], row["course_id"], row["lesson_id"]) for row in records}
    expected_pairs = max(1, sum(len(course.lessons) for course in get_courses()) * max(1, len(students)))
    interventions = _interventions(students, records)

    return {
        "summary": {
            "students": len(students),
            "activeToday": _active_today([*interactions, *records]),
            "completionRate": round(len(completed_pairs) / expected_pairs * 100),
            "aiQuestions": len(questions),
            "kbCoverage": _course_coverage_percent(rag_status),
            "interventionTasks": len(interventions),
            "kbChunks": rag_status.get("chunks", 0),
            "taskSubmissions": len(submissions),
            "taskPassRate": _task_pass_rate(submissions),
        },
        "classes": _class_overview(classes, students, records),
        "studentProgress": _student_progress(students, records),
        "lessonProgress": _lesson_progress(records),
        "hotQuestions": _hot_questions(questions),
        "weakPoints": _weak_points(records),
        "interventions": interventions,
        "knowledgeCoverage": _knowledge_coverage(rag_status),
        "recentInteractions": _recent_activity(interactions, records)[:8],
        "taskSubmissions": _task_submissions(submissions),
        "taskWeakPoints": _task_weak_points(submissions),
    }


def _active_today(rows: list[dict]) -> int:
    today = datetime.now(UTC).date()
    student_ids = set()
    count = 0
    for row in rows:
        try:
            created = datetime.fromisoformat(row["created_at"]).date()
        except (TypeError, ValueError):
            continue
        if created == today:
            if row.get("student_id"):
                student_ids.add(row["student_id"])
            else:
                count += 1
    return len(student_ids) or count


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
    # 课程课时标题
    lesson_titles = {
        (course.id, lesson.id): lesson.title
        for course in get_courses()
        for lesson in course.lessons
    }
    # 任务标题（从 learning_tasks 表）
    task_titles = _task_title_map()
    # 合并查找
    def _get_title(key):
        return lesson_titles.get(key) or task_titles.get(key[1]) or key[1] or ""
    return [
        {
            "lesson": _get_title(key),
            "courseId": key[0] or "",
            "completed": round(count / max_count * 100),
            "interactions": count,
        }
        for key, count in counts.most_common(24)
    ]


def _task_title_map() -> dict[str, str]:
    """从 learning_tasks 表获取 task_id -> title 映射。"""
    try:
        from backend.app.services.database import get_conn
        with get_conn() as conn:
            rows = conn.execute("SELECT id, title FROM learning_tasks").fetchall()
            return {row["id"]: row["title"] for row in rows}
    except Exception:
        return {}


def _hot_questions(questions: list[str]) -> list[dict]:
    words: Counter[str] = Counter()
    for question in questions:
        for token in re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z][A-Za-z0-9_+-]{2,}", question):
            if token.lower() in {"spring", "springboot", "boot", "java"}:
                continue
            words[token] += 1
    return [{"keyword": key, "count": count} for key, count in words.most_common(8)]


def _weak_points(records: list[dict]) -> list[dict]:
    low_scores = [row for row in records if row.get("score") is not None and int(row["score"]) < 70]
    if not low_scores:
        return []
    lesson_titles = {
        (course.id, lesson.id): lesson.title
        for course in get_courses()
        for lesson in course.lessons
    }
    task_titles = _task_title_map()
    counts = Counter((row["course_id"], row["lesson_id"]) for row in low_scores)
    def _get_title(key):
        return lesson_titles.get(key) or task_titles.get(key[1]) or key[1] or "未标记"
    return [
        {
            "name": _get_title(key),
            "courseId": key[0] or "",
            "value": min(100, count * 20),
        }
        for key, count in counts.most_common(12)
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


def _class_overview(classes: list[dict], students: list[dict], records: list[dict]) -> list[dict]:
    result = []
    for cls in classes:
        class_students = [student for student in students if student.get("class_id") == cls["id"]]
        class_records = [row for row in records if row.get("class_id") == cls["id"]]
        completed = {(row["student_id"], row["lesson_id"]) for row in class_records}
        lesson_count = next((len(course.lessons) for course in get_courses() if course.id == cls["course_id"]), 0)
        expected = max(1, len(class_students) * max(1, lesson_count))
        scores = [int(row["score"]) for row in class_records if row.get("score") is not None]
        result.append(
            {
                "id": cls["id"],
                "name": cls["name"],
                "courseId": cls["course_id"],
                "students": len(class_students),
                "records": len(class_records),
                "completionRate": round(len(completed) / expected * 100),
                "averageScore": round(sum(scores) / len(scores)) if scores else 0,
            }
        )
    return result


def _student_progress(students: list[dict], records: list[dict]) -> list[dict]:
    classes = {cls["id"]: dict(cls) for cls in list_classes()}
    courses = {course.id: course for course in get_courses()}
    result = []
    for student in students:
        owned = [row for row in records if row["student_id"] == student["id"]]
        class_course_id = classes.get(student.get("class_id"), {}).get("course_id")
        course_id = owned[0]["course_id"] if owned else class_course_id or "nongbo-admin-project"
        lesson_total = len(courses.get(course_id, get_courses()[0]).lessons)
        completed_lessons = {row["lesson_id"] for row in owned}
        scores = [int(row["score"]) for row in owned if row.get("score") is not None]
        last = owned[0] if owned else None
        result.append(
            {
                "studentId": student["id"],
                "studentName": student["name"],
                "studentNo": student.get("student_no"),
                "classId": student.get("class_id"),
                "courseId": course_id,
                "completed": len(completed_lessons),
                "total": lesson_total,
                "completionRate": round(len(completed_lessons) / max(1, lesson_total) * 100),
                "averageScore": round(sum(scores) / len(scores)) if scores else 0,
                "lastLessonId": last.get("lesson_id") if last else "",
                "lastActiveAt": last.get("created_at") if last else "",
            }
        )
    return sorted(result, key=lambda item: (item["completionRate"], item["averageScore"]))


def _interventions(students: list[dict], records: list[dict]) -> list[dict]:
    items = []
    for student in _student_progress(students, records):
        if student["completed"] == 0:
            items.append({"level": "high", "title": f"{student['studentName']} 尚未开始", "action": "课前提醒登录并完成第一关自检。"})
        elif student["averageScore"] and student["averageScore"] < 70:
            items.append({"level": "medium", "title": f"{student['studentName']} 练习低于 70 分", "action": "查看其最近提交，安排针对性讲解。"})
    return items[:6]


def _recent_activity(interactions: list[dict], records: list[dict]) -> list[dict]:
    normalized_records = [
        {
            "kind": row["kind"],
            "courseId": row["course_id"],
            "lessonId": row["lesson_id"],
            "studentId": row["student_id"],
            "studentName": row.get("student_name"),
            "className": row.get("class_name"),
            "question": row.get("notes") or row.get("feedback") or row["kind"],
            "score": row.get("score"),
            "createdAt": row["created_at"],
        }
        for row in records
    ]
    normalized_interactions = [
        {
            "kind": row["kind"],
            "courseId": row["course_id"],
            "lessonId": row["lesson_id"],
            "studentId": row.get("student_id"),
            "studentName": None,
            "className": None,
            "question": row.get("question"),
            "score": row.get("score"),
            "createdAt": row["created_at"],
        }
        for row in interactions
    ]
    return sorted([*normalized_interactions, *normalized_records], key=lambda item: item.get("createdAt") or "", reverse=True)


def _task_pass_rate(submissions: list[dict]) -> int:
    if not submissions:
        return 0
    passed = sum(1 for item in submissions if int(item.get("passed") or 0) == 1)
    return round(passed / len(submissions) * 100)


def _task_submissions(submissions: list[dict]) -> list[dict]:
    return [
        {
            "studentId": row["student_id"],
            "studentName": row.get("student_name"),
            "studentNo": row.get("student_no"),
            "className": row.get("class_name"),
            "courseLineId": row["course_line_id"],
            "moduleId": row["module_id"],
            "taskId": row["task_id"],
            "score": row["score"],
            "passed": bool(row["passed"]),
            "level": row["level"],
            "reply": row["reply"],
            "createdAt": row["created_at"],
        }
        for row in submissions[:30]
    ]


def _task_weak_points(submissions: list[dict]) -> list[dict]:
    low = [row for row in submissions if int(row.get("score") or 0) < 70]
    counts = Counter(row["task_id"] for row in low)
    return [{"name": task_id, "value": count} for task_id, count in counts.most_common(8)]
