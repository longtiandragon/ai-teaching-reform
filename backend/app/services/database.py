import sqlite3
import json
from collections.abc import Iterable
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from backend.app.config import get_settings


def init_db() -> None:
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(settings.db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                course_id TEXT NOT NULL,
                lesson_id TEXT,
                question TEXT,
                answer TEXT,
                score INTEGER,
                created_at TEXT NOT NULL
            )
            """
        )
        _ensure_column(conn, "interactions", "student_id", "TEXT")
        _ensure_column(conn, "interactions", "class_id", "TEXT")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS classes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                course_id TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                class_id TEXT,
                student_no TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS learning_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                class_id TEXT,
                course_id TEXT NOT NULL,
                lesson_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                score INTEGER,
                correct INTEGER,
                total INTEGER,
                code TEXT,
                notes TEXT,
                feedback TEXT,
                answers_json TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS course_lines (
                id TEXT PRIMARY KEY,
                slug TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                target_audience TEXT,
                tech_stack_json TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS learning_modules (
                id TEXT PRIMARY KEY,
                course_line_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                business_context TEXT,
                sort_order INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS learning_tasks (
                id TEXT PRIMARY KEY,
                module_id TEXT NOT NULL,
                course_line_id TEXT NOT NULL,
                title TEXT NOT NULL,
                task_type TEXT NOT NULL,
                goal TEXT NOT NULL,
                scenario TEXT,
                instruction TEXT NOT NULL,
                required_artifact_type TEXT NOT NULL,
                difficulty INTEGER NOT NULL,
                sort_order INTEGER NOT NULL,
                unlock_policy_json TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS task_rubrics (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                criterion_type TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                weight INTEGER NOT NULL,
                required INTEGER NOT NULL,
                rule_config_json TEXT NOT NULL,
                sort_order INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS student_task_progress (
                student_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                course_line_id TEXT NOT NULL,
                module_id TEXT NOT NULL,
                status TEXT NOT NULL,
                progress INTEGER NOT NULL,
                score INTEGER,
                updated_at TEXT NOT NULL,
                PRIMARY KEY(student_id, task_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS task_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                course_line_id TEXT NOT NULL,
                module_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                artifact_type TEXT,
                student_input TEXT NOT NULL,
                score INTEGER NOT NULL,
                passed INTEGER NOT NULL,
                level TEXT NOT NULL,
                reply TEXT NOT NULL,
                rubric_scores_json TEXT NOT NULL,
                evidence_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS guided_sessions (
                id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                course_line_id TEXT NOT NULL,
                status TEXT NOT NULL,
                steps_json TEXT NOT NULL,
                conversation_json TEXT NOT NULL,
                current_step INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS teacher_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                content TEXT NOT NULL,
                analysis_json TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS published_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                course_line_id TEXT NOT NULL,
                published_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(question_id, task_id)
            )
            """
        )
        _seed_initial_accounts(conn)
        conn.commit()


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, column_type: str) -> None:
    columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")


def _seed_initial_accounts(conn: sqlite3.Connection) -> None:
    classes = [
        ("class-24-soft", "24软件本", "nongbo-admin-project"),
        ("class-24-apply-2", "24计应2班", "springboot-course-12"),
    ]
    users = [
        ("stu-240101", "陈明", "student", "class-24-soft", "240101"),
        ("stu-240102", "李欣", "student", "class-24-soft", "240102"),
        ("stu-240103", "王睿", "student", "class-24-soft", "240103"),
        ("stu-240201", "赵晴", "student", "class-24-soft", "240201"),
        ("stu-240200048", "新同学", "student", "class-24-apply-2", "240200048"),
        ("teacher-001", "孙老师", "teacher", "class-24-soft", "T2024001"),
        ("teacher-002", "王老师", "teacher", "class-24-apply-2", "T2024002"),
        ("teacher-003", "孙老师", "teacher", "class-24-soft", "20240036"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO classes(id, name, course_id) VALUES (?, ?, ?)",
        classes,
    )
    conn.executemany(
        "INSERT OR IGNORE INTO users(id, name, role, class_id, student_no) VALUES (?, ?, ?, ?, ?)",
        users,
    )


@contextmanager
def get_conn() -> Iterable[sqlite3.Connection]:
    settings = get_settings()
    init_db()
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def db_exists() -> bool:
    path: Path = get_settings().db_path
    return path.exists()


def record_interaction(
    *,
    kind: str,
    course_id: str,
    lesson_id: str | None = None,
    question: str | None = None,
    answer: str | None = None,
    score: int | None = None,
    student_id: str | None = None,
    class_id: str | None = None,
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO interactions(kind, course_id, lesson_id, question, answer, score, created_at, student_id, class_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (kind, course_id, lesson_id, question, answer, score, datetime.now(UTC).isoformat(), student_id, class_id),
        )
        conn.commit()


def interaction_rows() -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM interactions ORDER BY created_at DESC LIMIT 50").fetchall()


def list_classes() -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM classes ORDER BY name").fetchall()


def list_users(role: str | None = None) -> list[sqlite3.Row]:
    with get_conn() as conn:
        if role:
            return conn.execute("SELECT * FROM users WHERE role = ? ORDER BY class_id, student_no, name", (role,)).fetchall()
        return conn.execute("SELECT * FROM users ORDER BY role, class_id, student_no, name").fetchall()


def get_user(user_id: str) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def record_learning_event(
    *,
    student_id: str,
    course_id: str,
    lesson_id: str,
    kind: str,
    score: int | None = None,
    correct: int | None = None,
    total: int | None = None,
    code: str | None = None,
    notes: str | None = None,
    feedback: str | None = None,
    answers: list[dict] | None = None,
) -> None:
    user = get_user(student_id)
    class_id = user["class_id"] if user else None
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO learning_records(
                student_id, class_id, course_id, lesson_id, kind, score, correct, total,
                code, notes, feedback, answers_json, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student_id,
                class_id,
                course_id,
                lesson_id,
                kind,
                score,
                correct,
                total,
                code,
                notes,
                feedback,
                json.dumps(answers or [], ensure_ascii=False),
                datetime.now(UTC).isoformat(),
            ),
        )
        conn.commit()


def learning_rows(limit: int = 500) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT lr.*, u.name AS student_name, u.student_no, c.name AS class_name
            FROM learning_records lr
            LEFT JOIN users u ON u.id = lr.student_id
            LEFT JOIN classes c ON c.id = lr.class_id
            ORDER BY lr.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


def student_records(student_id: str, course_id: str | None = None) -> list[sqlite3.Row]:
    with get_conn() as conn:
        if course_id:
            return conn.execute(
                """
                SELECT * FROM learning_records
                WHERE student_id = ? AND course_id = ?
                ORDER BY created_at DESC
                LIMIT 100
                """,
                (student_id, course_id),
            ).fetchall()
        return conn.execute(
            """
            SELECT * FROM learning_records
            WHERE student_id = ?
            ORDER BY created_at DESC
            LIMIT 100
            """,
            (student_id,),
        ).fetchall()


def upsert_course_runtime_seed(seed: dict) -> None:
    now = datetime.now(UTC).isoformat()
    with get_conn() as conn:
        line = seed["courseLine"]
        conn.execute(
            """
            INSERT INTO course_lines(id, slug, title, description, target_audience, tech_stack_json, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                slug=excluded.slug,
                title=excluded.title,
                description=excluded.description,
                target_audience=excluded.target_audience,
                tech_stack_json=excluded.tech_stack_json,
                status=excluded.status,
                updated_at=excluded.updated_at
            """,
            (
                line["slug"],
                line["slug"],
                line["title"],
                line.get("description", ""),
                line.get("targetAudience", ""),
                json.dumps(line.get("techStack", []), ensure_ascii=False),
                line.get("status", "active"),
                now,
                now,
            ),
        )
        for module_index, module in enumerate(seed.get("modules", []), start=1):
            module_id = module["slug"]
            conn.execute(
                """
                INSERT INTO learning_modules(id, course_line_id, title, description, business_context, sort_order)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    course_line_id=excluded.course_line_id,
                    title=excluded.title,
                    description=excluded.description,
                    business_context=excluded.business_context,
                    sort_order=excluded.sort_order
                """,
                (
                    module_id,
                    line["slug"],
                    module["title"],
                    module.get("description", ""),
                    module.get("businessContext", ""),
                    module_index,
                ),
            )
            for task_index, task in enumerate(module.get("tasks", []), start=1):
                task_id = task["slug"]
                conn.execute(
                    """
                    INSERT INTO learning_tasks(
                        id, module_id, course_line_id, title, task_type, goal, scenario, instruction,
                        required_artifact_type, difficulty, sort_order, unlock_policy_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        module_id=excluded.module_id,
                        course_line_id=excluded.course_line_id,
                        title=excluded.title,
                        task_type=excluded.task_type,
                        goal=excluded.goal,
                        scenario=excluded.scenario,
                        instruction=excluded.instruction,
                        required_artifact_type=excluded.required_artifact_type,
                        difficulty=excluded.difficulty,
                        sort_order=excluded.sort_order,
                        unlock_policy_json=excluded.unlock_policy_json
                    """,
                    (
                        task_id,
                        module_id,
                        line["slug"],
                        task["title"],
                        task.get("type", "analysis"),
                        task.get("goal", ""),
                        task.get("scenario", ""),
                        task.get("instruction", ""),
                        task.get("requiredArtifactType", "text"),
                        int(task.get("difficulty", 1)),
                        task_index,
                        json.dumps(task.get("unlockPolicy", {"minScore": 70, "requireCriticalCriteria": True}), ensure_ascii=False),
                    ),
                )
                for rubric_index, rubric in enumerate(task.get("rubrics", []), start=1):
                    rubric_id = rubric.get("id") or f"{task_id}:{rubric.get('type', 'criterion')}:{rubric_index}"
                    conn.execute(
                        """
                        INSERT INTO task_rubrics(
                            id, task_id, criterion_type, name, description, weight, required, rule_config_json, sort_order
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            task_id=excluded.task_id,
                            criterion_type=excluded.criterion_type,
                            name=excluded.name,
                            description=excluded.description,
                            weight=excluded.weight,
                            required=excluded.required,
                            rule_config_json=excluded.rule_config_json,
                            sort_order=excluded.sort_order
                        """,
                        (
                            rubric_id,
                            task_id,
                            rubric.get("type", "keyword"),
                            rubric["name"],
                            rubric.get("description", ""),
                            int(rubric.get("weight", 10)),
                            1 if rubric.get("required", False) else 0,
                            json.dumps(rubric.get("config", {}), ensure_ascii=False),
                            rubric_index,
                        ),
                    )
        conn.commit()


def course_line_rows() -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM course_lines ORDER BY created_at, title").fetchall()


def get_course_line_row(course_line_id: str) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM course_lines WHERE id = ? OR slug = ?", (course_line_id, course_line_id)).fetchone()


def module_rows(course_line_id: str) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM learning_modules WHERE course_line_id = ? ORDER BY sort_order, title",
            (course_line_id,),
        ).fetchall()


def task_rows(course_line_id: str | None = None, module_id: str | None = None) -> list[sqlite3.Row]:
    query = "SELECT * FROM learning_tasks"
    params: list[str] = []
    clauses = []
    if course_line_id:
        clauses.append("course_line_id = ?")
        params.append(course_line_id)
    if module_id:
        clauses.append("module_id = ?")
        params.append(module_id)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY course_line_id, module_id, sort_order"
    with get_conn() as conn:
        return conn.execute(query, params).fetchall()


def get_task_row(task_id: str) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM learning_tasks WHERE id = ?", (task_id,)).fetchone()


def rubric_rows(task_id: str) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM task_rubrics WHERE task_id = ? ORDER BY sort_order", (task_id,)).fetchall()


def progress_rows(student_id: str, course_line_id: str) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT * FROM student_task_progress
            WHERE student_id = ? AND course_line_id = ?
            """,
            (student_id, course_line_id),
        ).fetchall()


def latest_submission_rows(limit: int = 200) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT ts.*, u.name AS student_name, u.student_no, c.name AS class_name
            FROM task_submissions ts
            LEFT JOIN users u ON u.id = ts.student_id
            LEFT JOIN classes c ON c.id = u.class_id
            ORDER BY ts.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


def record_task_submission(
    *,
    student_id: str,
    course_line_id: str,
    module_id: str,
    task_id: str,
    artifact_type: str | None,
    student_input: str,
    score: int,
    passed: bool,
    level: str,
    reply: str,
    rubric_scores: list[dict],
    evidence: list[dict],
    next_task_id: str | None = None,
) -> None:
    now = datetime.now(UTC).isoformat()
    status = "completed" if passed else "needs_revision"
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO task_submissions(
                student_id, course_line_id, module_id, task_id, artifact_type, student_input, score,
                passed, level, reply, rubric_scores_json, evidence_json, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student_id,
                course_line_id,
                module_id,
                task_id,
                artifact_type,
                student_input,
                score,
                1 if passed else 0,
                level,
                reply,
                json.dumps(rubric_scores, ensure_ascii=False),
                json.dumps(evidence, ensure_ascii=False),
                now,
            ),
        )
        conn.execute(
            """
            INSERT INTO student_task_progress(student_id, task_id, course_line_id, module_id, status, progress, score, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(student_id, task_id) DO UPDATE SET
                status=excluded.status,
                progress=excluded.progress,
                score=excluded.score,
                updated_at=excluded.updated_at
            """,
            (student_id, task_id, course_line_id, module_id, status, 100 if passed else max(10, min(score, 95)), score, now),
        )
        if passed and next_task_id:
            next_task = conn.execute("SELECT * FROM learning_tasks WHERE id = ?", (next_task_id,)).fetchone()
            if next_task:
                conn.execute(
                    """
                    INSERT INTO student_task_progress(student_id, task_id, course_line_id, module_id, status, progress, score, updated_at)
                    VALUES (?, ?, ?, ?, 'active', 0, NULL, ?)
                    ON CONFLICT(student_id, task_id) DO NOTHING
                    """,
                    (student_id, next_task_id, next_task["course_line_id"], next_task["module_id"], now),
                )
        conn.commit()


# ─── Guided Sessions ───────────────────────────────────────────────────


def save_guided_session(
    *,
    session_id: str,
    student_id: str,
    task_id: str,
    course_line_id: str,
    steps: list[dict],
    conversation: list[dict],
    current_step: int,
    status: str,
) -> None:
    now = datetime.now(UTC).isoformat()
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO guided_sessions(id, student_id, task_id, course_line_id, status,
                steps_json, conversation_json, current_step, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id, student_id, task_id, course_line_id, status,
                json.dumps(steps, ensure_ascii=False),
                json.dumps(conversation, ensure_ascii=False),
                current_step, now, now,
            ),
        )
        conn.commit()


def get_guided_session(session_id: str) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM guided_sessions WHERE id = ?", (session_id,)
        ).fetchone()


def update_guided_session(
    *,
    session_id: str,
    conversation: list[dict],
    current_step: int,
    status: str,
) -> None:
    now = datetime.now(UTC).isoformat()
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE guided_sessions
            SET conversation_json = ?, current_step = ?, status = ?, updated_at = ?
            WHERE id = ?
            """,
            (json.dumps(conversation, ensure_ascii=False), current_step, status, now, session_id),
        )
        conn.commit()


def list_guided_sessions(student_id: str | None = None, task_id: str | None = None) -> list[sqlite3.Row]:
    with get_conn() as conn:
        query = "SELECT * FROM guided_sessions WHERE 1=1"
        params: list[str] = []
        if student_id:
            query += " AND student_id = ?"
            params.append(student_id)
        if task_id:
            query += " AND task_id = ?"
            params.append(task_id)
        query += " ORDER BY created_at DESC LIMIT 50"
        return conn.execute(query, params).fetchall()


# ─── Teacher Feedback ────────────────────────────────────────────────


def save_feedback(teacher_id: str, student_id: str, content: str, analysis_json: str | None = None) -> int:
    now = datetime.now(UTC).isoformat()
    with get_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO teacher_feedback(teacher_id, student_id, content, analysis_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (teacher_id, student_id, content, analysis_json, now),
        )
        conn.commit()
        return cursor.lastrowid


def get_student_feedback(student_id: str) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            """SELECT tf.*, u.name as teacher_name
               FROM teacher_feedback tf
               LEFT JOIN users u ON u.id = tf.teacher_id
               WHERE tf.student_id = ?
               ORDER BY tf.created_at DESC""",
            (student_id,),
        ).fetchall()


def list_students_by_class(class_id: str | None = None) -> list[sqlite3.Row]:
    with get_conn() as conn:
        if class_id:
            return conn.execute(
                "SELECT * FROM users WHERE role = 'student' AND class_id = ? ORDER BY student_no, name",
                (class_id,),
            ).fetchall()
        return conn.execute(
            "SELECT * FROM users WHERE role = 'student' ORDER BY class_id, student_no, name"
        ).fetchall()


# ─── Published Questions ────────────────────────────────────────────


def publish_question(question_id: str, task_id: str, course_line_id: str, published_by: str) -> int:
    """Publish a question to a task."""
    now = datetime.now(UTC).isoformat()
    with get_conn() as conn:
        cursor = conn.execute(
            """
            INSERT INTO published_questions(question_id, task_id, course_line_id, published_by, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(question_id, task_id) DO UPDATE SET
                course_line_id=excluded.course_line_id,
                published_by=excluded.published_by,
                created_at=excluded.created_at
            """,
            (question_id, task_id, course_line_id, published_by, now),
        )
        conn.commit()
        return cursor.lastrowid


def unpublish_question(question_id: str, task_id: str) -> bool:
    """Remove a published question from a task."""
    with get_conn() as conn:
        cursor = conn.execute(
            "DELETE FROM published_questions WHERE question_id = ? AND task_id = ?",
            (question_id, task_id),
        )
        conn.commit()
        return cursor.rowcount > 0


def get_published_questions(task_id: str) -> list[sqlite3.Row]:
    """Get all published questions for a task."""
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM published_questions WHERE task_id = ? ORDER BY created_at",
            (task_id,),
        ).fetchall()


def get_published_questions_by_course(course_line_id: str) -> list[sqlite3.Row]:
    """Get all published questions grouped by task for a course line."""
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM published_questions WHERE course_line_id = ? ORDER BY task_id, created_at",
            (course_line_id,),
        ).fetchall()


def get_published_question(question_id: str, task_id: str) -> sqlite3.Row | None:
    """Get a single published question entry."""
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM published_questions WHERE question_id = ? AND task_id = ?",
            (question_id, task_id),
        ).fetchone()


def get_all_published_for_question(question_id: str) -> list[sqlite3.Row]:
    """Get all tasks a question is published to."""
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM published_questions WHERE question_id = ?",
            (question_id,),
        ).fetchall()


def get_all_feedback() -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            """SELECT tf.*, u.name as teacher_name, s.name as student_name, s.student_no
               FROM teacher_feedback tf
               LEFT JOIN users u ON u.id = tf.teacher_id
               LEFT JOIN users s ON s.id = tf.student_id
               ORDER BY tf.created_at DESC
               LIMIT 200"""
        ).fetchall()
