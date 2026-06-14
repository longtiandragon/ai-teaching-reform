"""Teacher AI analysis service -- calls DeepSeek to analyze student/class performance."""

import json

from backend.app.config import get_settings
from backend.app.services.database import (
    get_user,
    interaction_rows,
    latest_submission_rows,
    list_students_by_class,
    student_records,
)


async def _call_deepseek_json(prompt: str) -> dict:
    """Call DeepSeek and return parsed JSON. Uses response_format=json_object."""
    settings = get_settings()
    if not settings.deepseek_api_key.strip():
        return {"error": "DeepSeek API key 未配置"}

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            timeout=settings.deepseek_timeout_seconds,
            max_retries=0,
        )
        response = await client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一个教学分析助手，专门分析学生的学习数据并给出结构化反馈。"
                        "你必须只返回 JSON，不输出额外文本。"
                        "所有分析和建议必须基于提供的数据，不要编造。"
                        "如果数据不足，在 summary 中说明数据有限。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content if response.choices else ""
        if not content:
            return {"error": "DeepSeek 未返回有效内容"}
        return json.loads(content)
    except json.JSONDecodeError:
        return {"error": "DeepSeek 返回的不是有效 JSON", "raw": content[:300]}
    except Exception as exc:
        return {"error": f"DeepSeek 调用失败：{exc.__class__.__name__}", "detail": str(exc)[:200]}


def _format_submissions(submissions: list) -> str:
    lines = []
    for s in submissions[:15]:
        lines.append(
            f"- 任务: {s.get('task_id', '?')}, 得分: {s.get('score', '?')}, "
            f"等级: {s.get('level', '?')}, 通过: {'是' if s.get('passed') else '否'}"
        )
    return "\n".join(lines) if lines else "无提交记录"


def _format_interactions(interactions: list) -> str:
    lines = []
    for i in interactions[:15]:
        q = (i.get("question") or "")[:100]
        lines.append(f"- [{i.get('kind', '?')}] {q}")
    return "\n".join(lines) if lines else "无聊天记录"


def _format_records(records: list) -> str:
    lines = []
    for r in records[:15]:
        lines.append(
            f"- 课程: {r.get('course_id', '?')}, 章节: {r.get('lesson_id', '?')}, "
            f"类型: {r.get('kind', '?')}, 得分: {r.get('score', '?')}"
        )
    return "\n".join(lines) if lines else "无学习记录"


async def analyze_student_performance(student_id: str) -> dict:
    """Analyze a single student's learning performance using AI."""
    # 1. Get student info
    user = get_user(student_id)
    student_name = dict(user)["name"] if user else student_id

    # 2. Get student records
    records = [dict(row) for row in student_records(student_id)]

    # 3. Get task submissions
    all_submissions = [dict(row) for row in latest_submission_rows(200)]
    student_submissions = [s for s in all_submissions if s.get("student_id") == student_id]

    # 4. Get interactions (chat history)
    all_interactions = [dict(row) for row in interaction_rows()]
    student_interactions = [i for i in all_interactions if i.get("student_id") == student_id]

    # 5. Build analysis prompt
    prompt = f"""请根据以下学生的学习数据，分析其学习情况并给出结构化反馈。

学生: {student_name} (ID: {student_id})
学习记录数: {len(records)}
提交记录数: {len(student_submissions)}
聊天记录数: {len(student_interactions)}

学习记录:
{_format_records(records)}

任务提交记录:
{_format_submissions(student_submissions)}

聊天记录:
{_format_interactions(student_interactions)}

请用以下 JSON 格式返回分析结果:
{{
  "studentName": "{student_name}",
  "strengths": ["优势1", "优势2"],
  "weaknesses": ["不足1", "不足2"],
  "improvementPlan": ["改进建议1", "改进建议2"],
  "recommendedTasks": ["推荐任务1", "推荐任务2"],
  "summary": "一句话总结该学生的学习状况"
}}"""

    result = await _call_deepseek_json(prompt)

    # Fallback if error
    if "error" in result:
        return {
            "studentName": student_name,
            "strengths": [],
            "weaknesses": [result["error"]],
            "improvementPlan": ["请检查 AI 配置后重试"],
            "recommendedTasks": [],
            "summary": f"分析失败: {result['error']}",
        }

    # Ensure required fields
    result.setdefault("studentName", student_name)
    result.setdefault("strengths", [])
    result.setdefault("weaknesses", [])
    result.setdefault("improvementPlan", [])
    result.setdefault("recommendedTasks", [])
    result.setdefault("summary", "")
    return result


async def analyze_class_performance(class_id: str) -> dict:
    """Analyze class-wide performance patterns."""
    # 1. Get all students in this class
    students = [dict(row) for row in list_students_by_class(class_id)]
    if not students:
        return {
            "className": class_id,
            "commonWeaknesses": ["该班级暂无学生"],
            "topStudents": [],
            "strugglingStudents": [],
            "recommendations": ["请先添加学生到该班级"],
        }

    # 2. Gather aggregated data
    all_submissions = [dict(row) for row in latest_submission_rows(500)]
    all_interactions = [dict(row) for row in interaction_rows()]
    all_records = []

    student_summaries = []
    for student in students:
        sid = student["id"]
        records = [dict(row) for row in student_records(sid)]
        all_records.extend(records)
        subs = [s for s in all_submissions if s.get("student_id") == sid]
        inter = [i for i in all_interactions if i.get("student_id") == sid]
        scores = [int(r["score"]) for r in records if r.get("score") is not None]
        avg_score = round(sum(scores) / len(scores)) if scores else 0
        student_summaries.append({
            "id": sid,
            "name": student["name"],
            "recordCount": len(records),
            "submissionCount": len(subs),
            "interactionCount": len(inter),
            "averageScore": avg_score,
        })

    # 3. Build prompt with aggregated data
    summary_lines = []
    for s in student_summaries:
        summary_lines.append(
            f"- {s['name']}: 记录{s['recordCount']}条, 提交{s['submissionCount']}次, "
            f"聊天{s['interactionCount']}次, 平均分{s['averageScore']}"
        )

    prompt = f"""请分析以下班级的整体学习情况。

班级: {class_id}
学生人数: {len(students)}

学生概况:
{chr(10).join(summary_lines)}

总体提交数: {len(all_submissions)}
总体聊天数: {len(all_interactions)}

请用以下 JSON 格式返回分析结果:
{{
  "className": "{class_id}",
  "commonWeaknesses": ["全班共同薄弱点1", "全班共同薄弱点2"],
  "topStudents": [{{"id": "学生ID", "name": "学生名", "score": 平均分}}],
  "strugglingStudents": [{{"id": "学生ID", "name": "学生名", "issues": ["问题1", "问题2"]}}],
  "recommendations": ["教学建议1", "教学建议2"],
  "summary": "一句话总结全班学习状况"
}}"""

    result = await _call_deepseek_json(prompt)

    if "error" in result:
        # Fallback: build from raw data
        sorted_students = sorted(student_summaries, key=lambda s: s["averageScore"], reverse=True)
        top = [s for s in sorted_students[:3] if s["averageScore"] > 0]
        struggling = [s for s in sorted_students if s["averageScore"] < 70 and s["averageScore"] > 0]
        return {
            "className": class_id,
            "commonWeaknesses": [result["error"]],
            "topStudents": [{"id": s["id"], "name": s["name"], "score": s["averageScore"]} for s in top],
            "strugglingStudents": [{"id": s["id"], "name": s["name"], "issues": ["平均分低于70"]} for s in struggling],
            "recommendations": ["请检查 AI 配置后重试"],
            "summary": f"分析失败: {result['error']}",
        }

    result.setdefault("className", class_id)
    result.setdefault("commonWeaknesses", [])
    result.setdefault("topStudents", [])
    result.setdefault("strugglingStudents", [])
    result.setdefault("recommendations", [])
    result.setdefault("summary", "")
    return result
