import json

from backend.app.config import get_settings
from backend.app.models import Citation


class LLMError(RuntimeError):
    status_code = 502


class LLMNotConfiguredError(LLMError):
    status_code = 503


class LLMTimeoutError(LLMError):
    status_code = 504


class DeepSeekClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def configured(self) -> bool:
        return bool(self.settings.deepseek_api_key.strip())

    def _ensure_live(self) -> None:
        if not self.configured:
            raise LLMNotConfiguredError("DeepSeek API key 未配置，不能生成 AI 回答。")
        if not self.settings.deepseek_live:
            raise LLMNotConfiguredError("智能助教未启用，暂时无法生成回复。")

    async def answer(self, question: str, citations: list[Citation], mode: str = "student") -> str:
        self._ensure_live()
        if not citations:
            raise LLMError("知识库没有检索到可引用资料，已拒绝无依据回答。")

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(
                api_key=self.settings.deepseek_api_key,
                base_url=self.settings.deepseek_base_url,
                timeout=self.settings.deepseek_timeout_seconds,
                max_retries=0,
            )
            response = await client.chat.completions.create(
                model=self.settings.deepseek_model,
                messages=self._messages(question, citations, mode),
                temperature=0.25,
            )
            content = response.choices[0].message.content if response.choices else ""
            if not content:
                raise LLMError("DeepSeek 未返回有效内容。")
            return content
        except LLMError:
            raise
        except Exception as exc:
            if exc.__class__.__name__ == "APITimeoutError":
                raise LLMTimeoutError("DeepSeek 调用超时。") from exc
            raise LLMError(f"DeepSeek 调用失败：{exc.__class__.__name__}") from exc

    async def stream_answer(self, question: str, citations: list[Citation], mode: str = "student"):
        self._ensure_live()
        if not citations:
            raise LLMError("知识库没有检索到可引用资料，已拒绝无依据回答。")

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(
                api_key=self.settings.deepseek_api_key,
                base_url=self.settings.deepseek_base_url,
                timeout=self.settings.deepseek_timeout_seconds,
                max_retries=0,
            )
            stream = await client.chat.completions.create(
                model=self.settings.deepseek_model,
                messages=self._messages(question, citations, mode),
                temperature=0.25,
                stream=True,
            )
            emitted = False
            async for event in stream:
                delta = event.choices[0].delta.content if event.choices else ""
                if delta:
                    emitted = True
                    yield delta
            if not emitted:
                raise LLMError("DeepSeek 流式接口未返回有效内容。")
        except LLMError:
            raise
        except Exception as exc:
            if exc.__class__.__name__ == "APITimeoutError":
                raise LLMTimeoutError("DeepSeek 调用超时。") from exc
            raise LLMError(f"DeepSeek 调用失败：{exc.__class__.__name__}") from exc

    async def training_feedback(
        self,
        *,
        task_context: dict,
        student_input: str,
        citations: list[Citation],
        rubric_scores: list[dict],
        rule_score: int,
    ) -> dict:
        self._ensure_live()
        if not citations:
            raise LLMError("知识库没有检索到可引用资料，已拒绝无依据验收。")
        messages = self._training_feedback_messages(task_context, student_input, citations, rubric_scores, rule_score)
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(
                api_key=self.settings.deepseek_api_key,
                base_url=self.settings.deepseek_base_url,
                timeout=self.settings.deepseek_timeout_seconds,
                max_retries=0,
            )
            response = await client.chat.completions.create(
                model=self.settings.deepseek_model,
                messages=messages,
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content if response.choices else ""
            if not content:
                raise LLMError("DeepSeek 未返回有效验收内容。")
            try:
                data = json.loads(content)
            except json.JSONDecodeError as exc:
                raise LLMError("DeepSeek 未按要求返回 JSON。") from exc
            return data
        except LLMError:
            raise
        except Exception as exc:
            if exc.__class__.__name__ == "APITimeoutError":
                raise LLMTimeoutError("DeepSeek 调用超时。") from exc
            raise LLMError(f"DeepSeek 调用失败：{exc.__class__.__name__}") from exc

    def _messages(self, question: str, citations: list[Citation], mode: str) -> list[dict[str, str]]:
        role = "教师" if mode == "teacher" else "学生"
        return [
            {
                "role": "system",
                "content": (
                    f"你是 SpringBoot 与农博后台管理系统课程的 AI 助教，当前回答对象是{role}。"
                    "必须只依据用户提供的引用资料回答；如果引用资料不足，要明确说资料不足，不能编造。"
                    "回答使用 Markdown，先给结论，再给依据和下一步。"
                ),
            },
            {
                "role": "user",
                "content": f"问题：{question}\n\n引用资料：\n{self._context(citations)}",
            },
        ]

    def _context(self, citations: list[Citation]) -> str:
        return "\n\n".join(
            [
                f"[{index + 1}] {citation.title} ({citation.source}, {citation.kind})\n{citation.snippet}"
                for index, citation in enumerate(citations)
            ]
        )

    def _training_feedback_messages(
        self,
        task_context: dict,
        student_input: str,
        citations: list[Citation],
        rubric_scores: list[dict],
        rule_score: int,
    ) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": (
                    "你是面向软件工程课程的 AI 实训助教。你的任务不是替学生完成完整项目，"
                    "而是根据当前任务目标、评分标准、课程资料和学生提交内容给出分步反馈。"
                    "规则：1. 只围绕当前任务回答；2. 不一次性生成完整项目；"
                    "3. 学生未充分思考前不直接给完整代码；4. 优先采用提问、提示、局部示例、检查反馈；"
                    "5. 如果学生要求整包代码，要拒绝并拆成当前任务下一步；"
                    "6. 必须结合引用资料和 rubric 命中情况；7. 只返回 JSON，不输出额外文本。"
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "currentTask": task_context,
                        "studentInput": student_input,
                        "ruleScore": rule_score,
                        "rubricScores": rubric_scores,
                        "evidence": [
                            {
                                "title": citation.title,
                                "source": citation.source,
                                "kind": citation.kind,
                                "snippet": citation.snippet,
                            }
                            for citation in citations
                        ],
                        "requiredJsonShape": {
                            "reply": "给学生的反馈，指出是否达标、依据和下一步",
                            "score": "0-100 的 AI 评价分",
                            "strengths": ["已经做得好的点"],
                            "problems": [{"type": "问题类型", "message": "问题描述", "suggestion": "修改建议"}],
                            "nextActions": ["下一步行动"],
                        },
                    },
                    ensure_ascii=False,
                ),
            },
        ]


deepseek_client = DeepSeekClient()
