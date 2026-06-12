import sqlite3
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
        conn.commit()


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
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO interactions(kind, course_id, lesson_id, question, answer, score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (kind, course_id, lesson_id, question, answer, score, datetime.now(UTC).isoformat()),
        )
        conn.commit()


def interaction_rows() -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM interactions ORDER BY created_at DESC LIMIT 50").fetchall()
