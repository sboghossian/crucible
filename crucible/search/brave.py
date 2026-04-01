"""Brave Search API integration — requires CRUCIBLE_BRAVE_API_KEY."""

from __future__ import annotations

import logging
from datetime import datetime

import httpx

from .cache import SearchCache
from .engine import SearchEngine
from .result import SearchResult

logger = logging.getLogger(__name__)

_BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search"


class BraveSearchEngine(SearchEngine):
    """
    Search engine backed by the Brave Search API.

    Requires an API key set via the ``api_key`` constructor parameter or the
    ``CRUCIBLE_BRAVE_API_KEY`` environment variable.
    """

    name = "brave"

    def __init__(
        self,
        api_key: str,
        cache: SearchCache | None = None,
        timeout: float = 15.0,
    ) -> None:
        if not api_key:
            raise ValueError("Brave Search requires a non-empty api_key")
        self._api_key = api_key
        self._cache = cache or SearchCache()
        self._timeout = timeout

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        cache_key = f"brave:{query}:{max_results}"
        cached = await self._cache.get(cache_key)
        if cached is not None:
            logger.debug("Brave cache hit for %r", query)
            return cached

        results = await self._fetch(query, max_results)
        await self._cache.set(cache_key, results)
        logger.debug("Brave returned %d results for %r", len(results), query)
        return results

    async def _fetch(self, query: str, count: int) -> list[SearchResult]:
        headers = {
            "X-Subscription-Token": self._api_key,
            "Accept": "application/json",
        }
        params = {"q": query, "count": min(count, 20)}

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                resp = await client.get(_BRAVE_API_URL, headers=headers, params=params)
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPError as exc:
                logger.warning("Brave Search request failed: %s", exc)
                return []

        web = data.get("web", {}).get("results", [])
        results: list[SearchResult] = []
        for item in web:
            title = item.get("title", "")
            url = item.get("url", "")
            snippet = item.get("description", "")
            if title and url:
                results.append(
                    SearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        source=self.name,
                        timestamp=datetime.utcnow(),
                    )
                )
        return results
