from __future__ import annotations

import asyncio
from typing import Any

from backend.app.models import AICheckProblem, AICheckRequest, AICheckResponse, Citation
from backend.app.services.agent_flow import NoCitationError
from backend.app.services.course_runtime import next_task_id, task_detail_from_ids
from backend.app.services.database import record_interaction, record_learning_event, record_task_submission
from backend.app.services.llm import deepseek_client
from backend.app.services.rag import rag_service
from backend.app.services.rubric_engine import rubric_engine


async def check_learning_task(request: AICheckRequest) -> AICheckResponse:
    task = task_detail_from_ids(request.courseLineId, request.taskId)
    citations = await asyncio.to_thread(
        rag_service.search,
        " ".join([task.title, task.goal, task.scenario, task.instruction, request.studentInput[:600]]),
        5,
        None,
        request.courseLineId,
        request.taskId,
    )
    # RAG 无结果时不拒绝，降级为纯 AI 评分
    if not citations:
        citations = []

    rubric_eval = rubric_engine.evaluate(request.studentInput, task.rubrics, citations)
    task_context = {
        "courseLineId": request.courseLineId,
        "moduleId": request.moduleId,
        "taskId": request.taskId,
        "title": task.title,
        "type": task.type,
        "goal": task.goal,
        "scenario": task.scenario,
        "instruction": task.instruction,
        "requiredArtifactType": task.required_artifact_type,
        "unlockPolicy": task.unlock_policy,
    }
    rubric_scores_payload = [score.model_dump() for score in rubric_eval.scores]
    llm_feedback = await deepseek_client.training_feedback(
        task_context=task_context,
        student_input=request.studentInput,
        citations=citations,
        rubric_scores=rubric_scores_payload,
        rule_score=rubric_eval.rule_score,
    )
    ai_score = _bounded_int(llm_feedback.get("score"), rubric_eval.rule_score)
    final_score = round(rubric_eval.rule_score * 0.6 + ai_score * 0.4)
    min_score = int(task.unlock_policy.get("minScore", 70))
    require_critical = bool(task.unlock_policy.get("requireCriticalCriteria", True))
    passed = final_score >= min_score and not (require_critical and rubric_eval.critical_failed)
    level = "passed" if passed else "needs_revision"
    next_id = next_task_id(request.courseLineId, request.taskId)
    next_unlocked = bool(passed and next_id)

    response = AICheckResponse(
        passed=passed,
        score=final_score,
        level=level,
        reply=str(llm_feedback.get("reply") or _default_reply(passed, final_score)),
        strengths=[str(item) for item in llm_feedback.get("strengths", []) if str(item).strip()],
        problems=[_problem(item) for item in llm_feedback.get("problems", []) if isinstance(item, dict)],
        nextActions=[str(item) for item in llm_feedback.get("nextActions", []) if str(item).strip()],
        evidence=citations,
        rubricScores=rubric_eval.scores,
        nextTaskUnlocked=next_unlocked,
    )
    await asyncio.to_thread(
        record_task_submission,
        student_id=request.studentId,
        course_line_id=request.courseLineId,
        module_id=request.moduleId,
        task_id=request.taskId,
        artifact_type=request.artifactType,
        student_input=request.studentInput,
        score=final_score,
        passed=passed,
        level=level,
        reply=response.reply,
        rubric_scores=rubric_scores_payload,
        evidence=[citation.model_dump() for citation in citations],
        question_id=request.questionId,
        next_task_id=next_id,
    )
    await asyncio.to_thread(
        record_interaction,
        kind="ai_check",
        course_id=request.courseLineId,
        lesson_id=request.taskId,
        question=request.studentInput,
        answer=response.reply,
        score=final_score,
        student_id=request.studentId,
    )
    await asyncio.to_thread(
        record_learning_event,
        student_id=request.studentId,
        course_id=request.courseLineId,
        lesson_id=request.taskId,
        kind="ai_check",
        score=final_score,
        code=request.studentInput,
        feedback=response.reply,
        answers=rubric_scores_payload,
    )
    return response


def _problem(item: dict[str, Any]) -> AICheckProblem:
    return AICheckProblem(
        type=str(item.get("type") or "rubric_issue"),
        message=str(item.get("message") or item.get("reason") or "该项还需要补充。"),
        suggestion=str(item.get("suggestion") or ""),
    )


def _bounded_int(value: Any, fallback: int) -> int:
    try:
        return max(0, min(100, int(value)))
    except (TypeError, ValueError):
        return fallback


def _default_reply(passed: bool, score: int) -> str:
    if passed:
        return f"本关综合评分 {score} 分，已经达到解锁要求。"
    return f"本关综合评分 {score} 分，暂未达到解锁要求，请根据评分项继续修改。"
