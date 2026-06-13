from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from fastapi import HTTPException

from backend.app.data.course_runtime_seed import course_runtime_seeds
from backend.app.models import (
    CourseLineSummary,
    LearningMapResponse,
    LearningModuleSummary,
    LearningTaskDetail,
    LearningTaskSummary,
)
from backend.app.services.database import (
    course_line_rows,
    get_course_line_row,
    get_task_row,
    module_rows,
    progress_rows,
    rubric_rows,
    task_rows,
    upsert_course_runtime_seed,
)


def sync_course_runtime_seed() -> None:
    for seed in course_runtime_seeds():
        upsert_course_runtime_seed(seed)


def list_course_lines() -> list[CourseLineSummary]:
    sync_course_runtime_seed()
    return [_course_line_from_row(row) for row in course_line_rows()]


def get_course_line(course_line_id: str) -> CourseLineSummary:
    sync_course_runtime_seed()
    row = get_course_line_row(course_line_id)
    if row is None:
        raise HTTPException(status_code=404, detail="course line not found")
    return _course_line_from_row(row)


def get_learning_map(course_line_id: str, student_id: str | None = None) -> LearningMapResponse:
    line = get_course_line(course_line_id)
    modules = module_rows(line.id)
    tasks = task_rows(line.id)
    progress = {
        row["task_id"]: dict(row)
        for row in progress_rows(student_id, line.id)
    } if student_id else {}
    first_unfinished_seen = False
    previous_completed = True
    task_summaries: list[LearningTaskSummary] = []
    tasks_by_module: dict[str, list[LearningTaskSummary]] = defaultdict(list)

    for task in tasks:
        row_progress = progress.get(task["id"])
        if student_id is None:
            status = "active"
            score = None
            task_progress = 0
        elif row_progress:
            status = row_progress["status"]
            score = row_progress["score"]
            task_progress = row_progress["progress"]
        elif previous_completed and not first_unfinished_seen:
            status = "active"
            score = None
            task_progress = 0
            first_unfinished_seen = True
        else:
            status = "locked"
            score = None
            task_progress = 0
        previous_completed = status == "completed"
        summary = LearningTaskSummary(
            id=task["id"],
            module_id=task["module_id"],
            course_line_id=task["course_line_id"],
            title=task["title"],
            type=task["task_type"],
            status=status,
            progress=int(task_progress or 0),
            score=score,
            required_artifact_type=task["required_artifact_type"],
        )
        task_summaries.append(summary)
        tasks_by_module[task["module_id"]].append(summary)

    module_summaries = []
    for module in modules:
        module_tasks = tasks_by_module.get(module["id"], [])
        completed = sum(1 for task in module_tasks if task.status == "completed")
        module_progress = round(completed / max(1, len(module_tasks)) * 100)
        module_summaries.append(
            LearningModuleSummary(
                id=module["id"],
                course_line_id=module["course_line_id"],
                title=module["title"],
                description=module["description"] or "",
                business_context=module["business_context"] or "",
                progress=module_progress,
                tasks=module_tasks,
            )
        )

    active_task = next((task for task in task_summaries if task.status == "active"), task_summaries[0] if task_summaries else None)
    current_module = None
    if active_task:
        module = next((item for item in module_summaries if item.id == active_task.module_id), None)
        if module:
            current_module = {"id": module.id, "title": module.title}

    return LearningMapResponse(
        courseLineId=line.id,
        title=line.title,
        description=line.description,
        currentModule=current_module,
        modules=module_summaries,
        tasks=task_summaries,
    )


def get_task_detail(task_id: str) -> LearningTaskDetail:
    sync_course_runtime_seed()
    task = get_task_row(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return _task_detail_from_row(task)


def task_detail_from_ids(course_line_id: str, task_id: str) -> LearningTaskDetail:
    detail = get_task_detail(task_id)
    if detail.course_line_id != course_line_id:
        raise HTTPException(status_code=404, detail="task not found in course line")
    return detail


def next_task_id(course_line_id: str, task_id: str) -> str | None:
    tasks = task_rows(course_line_id)
    for index, row in enumerate(tasks):
        if row["id"] == task_id and index + 1 < len(tasks):
            return tasks[index + 1]["id"]
    return None


def _course_line_from_row(row) -> CourseLineSummary:
    return CourseLineSummary(
        id=row["id"],
        slug=row["slug"],
        title=row["title"],
        description=row["description"],
        target_audience=row["target_audience"] or "",
        tech_stack=_loads(row["tech_stack_json"], []),
        status=row["status"],
    )


def _task_detail_from_row(row) -> LearningTaskDetail:
    rubrics = []
    for rubric in rubric_rows(row["id"]):
        rubrics.append(
            {
                "id": rubric["id"],
                "taskId": rubric["task_id"],
                "type": rubric["criterion_type"],
                "name": rubric["name"],
                "description": rubric["description"] or "",
                "weight": rubric["weight"],
                "required": bool(rubric["required"]),
                "config": _loads(rubric["rule_config_json"], {}),
            }
        )
    return LearningTaskDetail(
        id=row["id"],
        module_id=row["module_id"],
        course_line_id=row["course_line_id"],
        title=row["title"],
        type=row["task_type"],
        goal=row["goal"],
        scenario=row["scenario"] or "",
        instruction=row["instruction"],
        required_artifact_type=row["required_artifact_type"],
        difficulty=row["difficulty"],
        unlock_policy=_loads(row["unlock_policy_json"], {"minScore": 70, "requireCriticalCriteria": True}),
        rubrics=rubrics,
    )


def _loads(value: str | None, fallback: Any) -> Any:
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback
