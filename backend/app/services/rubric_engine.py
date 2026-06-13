from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from backend.app.models import Citation, RubricScore


@dataclass
class RubricEvaluation:
    scores: list[RubricScore]
    rule_score: int
    critical_failed: bool


class RubricEngine:
    def evaluate(self, student_input: str, rubrics: list[dict[str, Any]], evidence: list[Citation]) -> RubricEvaluation:
        scores = [self._evaluate_one(student_input, rubric, evidence) for rubric in rubrics]
        rule_score = self._weighted_score(scores)
        critical_failed = any(score.required and not score.passed for score in scores)
        return RubricEvaluation(scores=scores, rule_score=rule_score, critical_failed=critical_failed)

    def _evaluate_one(self, student_input: str, rubric: dict[str, Any], evidence: list[Citation]) -> RubricScore:
        criterion_type = rubric.get("type") or rubric.get("criterion_type", "keyword")
        config = rubric.get("config") or {}
        if criterion_type == "keyword":
            return self._keyword_score(student_input, rubric, config)
        if criterion_type == "regex":
            return self._regex_score(student_input, rubric, config)
        if criterion_type == "concept":
            return self._concept_score(student_input, rubric, config)
        if criterion_type == "rag_grounded":
            return self._rag_grounded_score(rubric, config, evidence)
        if criterion_type in {"code_pattern", "sql_design", "api_design"}:
            return self._keyword_score(student_input, rubric, config)
        if criterion_type == "anti_shortcut":
            return self._anti_shortcut_score(student_input, rubric, config)
        return self._base_score(rubric, False, 0, f"暂不支持的评分类型：{criterion_type}")

    def _keyword_score(self, student_input: str, rubric: dict[str, Any], config: dict[str, Any]) -> RubricScore:
        keywords = [str(item) for item in config.get("keywords", []) if str(item).strip()]
        min_hit = int(config.get("minHit", max(1, len(keywords))))
        hits = [keyword for keyword in keywords if keyword.lower() in student_input.lower()]
        ratio = min(1.0, len(hits) / max(1, min_hit))
        passed = len(hits) >= min_hit
        return self._base_score(rubric, passed, round(ratio * 100), f"命中 {len(hits)}/{min_hit} 个关键词：{', '.join(hits[:8]) or '无'}")

    def _regex_score(self, student_input: str, rubric: dict[str, Any], config: dict[str, Any]) -> RubricScore:
        patterns = [str(item) for item in config.get("patterns", []) if str(item).strip()]
        min_hit = int(config.get("minHit", max(1, len(patterns))))
        hits = []
        for pattern in patterns:
            try:
                if re.search(pattern, student_input, re.I | re.S):
                    hits.append(pattern)
            except re.error:
                continue
        ratio = min(1.0, len(hits) / max(1, min_hit))
        return self._base_score(rubric, len(hits) >= min_hit, round(ratio * 100), f"匹配 {len(hits)}/{min_hit} 条结构规则。")

    def _concept_score(self, student_input: str, rubric: dict[str, Any], config: dict[str, Any]) -> RubricScore:
        concepts = [str(item) for item in config.get("concepts", []) if str(item).strip()]
        min_hit = int(config.get("minHit", max(1, min(2, len(concepts)))))
        normalized = _normalize(student_input)
        hits = [concept for concept in concepts if _normalize(concept) in normalized]
        ratio = min(1.0, len(hits) / max(1, min_hit))
        return self._base_score(rubric, len(hits) >= min_hit, round(ratio * 100), f"覆盖 {len(hits)}/{min_hit} 个概念：{', '.join(hits[:6]) or '无'}")

    def _rag_grounded_score(self, rubric: dict[str, Any], config: dict[str, Any], evidence: list[Citation]) -> RubricScore:
        min_evidence = int(config.get("minEvidence", 1))
        count = len([item for item in evidence if item.snippet.strip()])
        ratio = min(1.0, count / max(1, min_evidence))
        return self._base_score(rubric, count >= min_evidence, round(ratio * 100), f"检索到 {count} 条可引用资料。")

    def _anti_shortcut_score(self, student_input: str, rubric: dict[str, Any], config: dict[str, Any]) -> RubricScore:
        patterns = [str(item) for item in config.get("forbiddenPatterns", []) if str(item).strip()]
        lowered = student_input.lower()
        hits = [pattern for pattern in patterns if pattern.lower() in lowered]
        passed = not hits
        return self._base_score(rubric, passed, 100 if passed else 0, "未发现整包代写倾向。" if passed else f"发现不符合闯关要求的表达：{', '.join(hits)}")

    def _base_score(self, rubric: dict[str, Any], passed: bool, score: int, reason: str) -> RubricScore:
        return RubricScore(
            criterion_id=rubric.get("id", rubric.get("name", "criterion")),
            name=rubric.get("name", "评分项"),
            type=rubric.get("type") or rubric.get("criterion_type", "keyword"),
            required=bool(rubric.get("required", False)),
            passed=passed,
            score=max(0, min(100, int(score))),
            weight=int(rubric.get("weight", 10)),
            reason=reason,
        )

    def _weighted_score(self, scores: list[RubricScore]) -> int:
        total_weight = sum(max(0, score.weight) for score in scores)
        if total_weight <= 0:
            return 0
        return round(sum(score.score * score.weight for score in scores) / total_weight)


def _normalize(value: str) -> str:
    return re.sub(r"\s+", "", value.lower())


rubric_engine = RubricEngine()
