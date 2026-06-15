"""知识库文件管理 — CRUD + 任务关联。"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from backend.app.config import get_settings
from backend.app.services.database import get_conn


def init_kb_tables() -> None:
    """初始化知识库元数据表。"""
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS kb_files (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                course_line_id TEXT,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                uploaded_by TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS kb_task_links (
                file_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                PRIMARY KEY(file_id, task_id)
            )
            """
        )
        conn.commit()


def list_files(course_line_id: str | None = None) -> list[dict]:
    """列出知识库文件。"""
    init_kb_tables()
    with get_conn() as conn:
        if course_line_id:
            rows = conn.execute(
                "SELECT * FROM kb_files WHERE course_line_id = ? ORDER BY created_at DESC",
                (course_line_id,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM kb_files ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]


def get_file(file_id: str) -> dict | None:
    """获取单个文件信息。"""
    init_kb_tables()
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM kb_files WHERE id = ?", (file_id,)).fetchone()
        return dict(row) if row else None


def delete_file(file_id: str) -> bool:
    """删除文件及其关联。"""
    init_kb_tables()
    with get_conn() as conn:
        conn.execute("DELETE FROM kb_task_links WHERE file_id = ?", (file_id,))
        result = conn.execute("DELETE FROM kb_files WHERE id = ?", (file_id,))
        conn.commit()
        return result.rowcount > 0


def register_file(
    filename: str,
    file_type: str,
    chunk_count: int,
    course_line_id: str | None = None,
    uploaded_by: str | None = None,
    file_id: str | None = None,
) -> str:
    """注册已上传的文件到元数据表。"""
    init_kb_tables()
    file_id = file_id or f"kb-{uuid.uuid4().hex[:12]}"
    now = datetime.now(UTC).isoformat()
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO kb_files(id, filename, file_type, course_line_id, chunk_count, uploaded_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                filename=excluded.filename,
                file_type=excluded.file_type,
                course_line_id=excluded.course_line_id,
                chunk_count=excluded.chunk_count,
                uploaded_by=excluded.uploaded_by
            """,
            (file_id, filename, file_type, course_line_id, chunk_count, uploaded_by, now),
        )
        conn.commit()
    return file_id


def update_file_chunk_count(file_id: str, chunk_count: int) -> None:
    init_kb_tables()
    with get_conn() as conn:
        conn.execute("UPDATE kb_files SET chunk_count = ? WHERE id = ?", (chunk_count, file_id))
        conn.commit()


def associate_task(file_id: str, task_id: str) -> bool:
    """将文件关联到学习任务。"""
    init_kb_tables()
    with get_conn() as conn:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO kb_task_links(file_id, task_id) VALUES (?, ?)",
                (file_id, task_id),
            )
            conn.commit()
            return True
        except Exception:
            return False


def dissociate_task(file_id: str, task_id: str) -> bool:
    """取消文件与任务的关联。"""
    init_kb_tables()
    with get_conn() as conn:
        result = conn.execute(
            "DELETE FROM kb_task_links WHERE file_id = ? AND task_id = ?",
            (file_id, task_id),
        )
        conn.commit()
        return result.rowcount > 0


def get_task_files(task_id: str) -> list[dict]:
    """获取任务关联的所有文件。"""
    init_kb_tables()
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT f.* FROM kb_files f
            JOIN kb_task_links l ON l.file_id = f.id
            WHERE l.task_id = ?
            ORDER BY f.created_at DESC
            """,
            (task_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_file_tasks(file_id: str) -> list[str]:
    """获取文件关联的所有任务 ID。"""
    init_kb_tables()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT task_id FROM kb_task_links WHERE file_id = ?",
            (file_id,),
        ).fetchall()
        return [row["task_id"] for row in rows]
