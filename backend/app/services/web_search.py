from __future__ import annotations

from backend.app.config import get_settings
from backend.app.models import Citation


class WebSearchError(RuntimeError):
    pass


class WebSearchNotConfiguredError(WebSearchError):
    pass


class WebSearchService:
    async def search(self, query: str, limit: int | None = None) -> list[Citation]:
        settings = get_settings()
        if not settings.web_search_enabled:
            raise WebSearchNotConfiguredError("联网搜索未启用，请在后端 .env 中配置 WEB_SEARCH_ENABLED=true。")
        if settings.web_search_provider.lower() != "tavily":
            raise WebSearchNotConfiguredError("当前仅支持 Tavily 搜索提供方。")
        if not settings.web_search_api_key.strip():
            raise WebSearchNotConfiguredError("Tavily API Key 未配置，请在后端 .env 中设置 WEB_SEARCH_API_KEY。")

        try:
            import httpx

            async with httpx.AsyncClient(timeout=settings.web_search_timeout_seconds) as client:
                result = await client.post(
                    "https://api.tavily.com/search",
                    headers={
                        "Authorization": f"Bearer {settings.web_search_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "query": query[:380],
                        "search_depth": "basic",
                        "max_results": limit or settings.web_search_top_k,
                        "include_answer": False,
                        "include_raw_content": False,
                    },
                )
                result.raise_for_status()
                payload = result.json()
        except WebSearchError:
            raise
        except Exception as exc:
            raise WebSearchError(f"Tavily 联网搜索失败：{exc.__class__.__name__}") from exc

        citations: list[Citation] = []
        for item in payload.get("results", [])[: limit or settings.web_search_top_k]:
            title = str(item.get("title") or item.get("url") or "外部网页资料").strip()
            source = str(item.get("url") or "tavily-search").strip()
            snippet = str(item.get("content") or item.get("description") or "").strip()
            if not snippet:
                continue
            citations.append(
                Citation(
                    title=title,
                    source=source,
                    snippet=snippet[: get_settings().rag_snippet_size],
                    score=float(item.get("score") or 0),
                    course_id=None,
                    lesson_id=None,
                    kind="web-search",
                )
            )
        return citations


web_search_service = WebSearchService()
