"""DuckDuckGo search via their HTML endpoint — no API key required."""

from __future__ import annotations

import asyncio
import logging
import urllib.parse
from datetime import datetime

import httpx

from .cache import SearchCache
from .engine import SearchEngine
from .result import SearchResult

logger = logging.getLogger(__name__)

_DDG_URL = "https://html.duckduckgo.com/html/"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; CrucibleBot/1.0; +https://github.com/crucible)"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}
# Polite rate limit — one request per second
_REQUEST_INTERVAL = 1.0


def _parse_ddg_html(html: str, source: str) -> list[SearchResult]:
    """Extract results from DDG HTML response using BeautifulSoup or regex fallback."""
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        results: list[SearchResult] = []

        for div in soup.find_all("div", class_="result"):
            title_tag = div.find("a", class_="result__a")
            snippet_tag = div.find("a", class_="result__snippet") or div.find(
                "div", class_="result__snippet"
            )
            if title_tag is None:
                continue
            title = title_tag.get_text(strip=True)
            raw_href = title_tag.get("href", "")
            url = _extract_url(raw_href) or raw_href
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
            if title and url:
                results.append(
                    SearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        source=source,
                        timestamp=datetime.utcnow(),
                    )
                )
        return results

    except ImportError:
        return _parse_ddg_html_regex(html, source)


def _parse_ddg_html_regex(html: str, source: str) -> list[SearchResult]:
    """Fallback regex-based parser when BeautifulSoup is not installed."""
    import re

    results: list[SearchResult] = []
    # Match result anchors: class="result__a" href="..."
    link_pattern = re.compile(
        r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL
    )
    snippet_pattern = re.compile(
        r'class="result__snippet"[^>]*>(.*?)</a>', re.DOTALL
    )
    tag_re = re.compile(r"<[^>]+>")

    links = link_pattern.findall(html)
    snippets = snippet_pattern.findall(html)

    for i, (href, raw_title) in enumerate(links):
        title = tag_re.sub("", raw_title).strip()
        url = _extract_url(href) or href
        snippet = tag_re.sub("", snippets[i]).strip() if i < len(snippets) else ""
        if title and url:
            results.append(
                SearchResult(
                    title=title,
                    url=url,
                    snippet=snippet,
                    source=source,
                    timestamp=datetime.utcnow(),
                )
            )
    return results


def _extract_url(href: str) -> str:
    """Unwrap DDG redirect URLs to get the actual destination."""
    if not href:
        return ""
    # DDG encodes the target in the `uddg` query param
    parsed = urllib.parse.urlparse(href)
    params = urllib.parse.parse_qs(parsed.query)
    uddg = params.get("uddg", [""])[0]
    if uddg:
        return urllib.parse.unquote(uddg)
    # Already a plain URL
    if href.startswith("http"):
        return href
    return ""


class DuckDuckGoEngine(SearchEngine):
    """Search engine backed by DuckDuckGo HTML — zero configuration."""

    name = "duckduckgo"

    def __init__(
        self,
        cache: SearchCache | None = None,
        request_interval: float = _REQUEST_INTERVAL,
        timeout: float = 15.0,
    ) -> None:
        self._cache = cache or SearchCache()
        self._interval = request_interval
        self._timeout = timeout
        self._last_request: float = 0.0
        self._lock = asyncio.Lock()

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        cache_key = f"ddg:{query}:{max_results}"
        cached = await self._cache.get(cache_key)
        if cached is not None:
            logger.debug("DDG cache hit for %r", query)
            return cached

        html = await self._fetch(query)
        results = _parse_ddg_html(html, source=self.name)[:max_results]

        await self._cache.set(cache_key, results)
        logger.debug("DDG returned %d results for %r", len(results), query)
        return results

    async def _fetch(self, query: str) -> str:
        async with self._lock:
            # Enforce rate limit
            now = asyncio.get_event_loop().time()
            elapsed = now - self._last_request
            if elapsed < self._interval:
                await asyncio.sleep(self._interval - elapsed)
            self._last_request = asyncio.get_event_loop().time()

        params = {"q": query, "b": "", "kl": "us-en"}
        async with httpx.AsyncClient(
            headers=_HEADERS, timeout=self._timeout, follow_redirects=True
        ) as client:
            try:
                resp = await client.post(_DDG_URL, data=params)
                resp.raise_for_status()
                return resp.text
            except httpx.HTTPError as exc:
                logger.warning("DuckDuckGo request failed: %s", exc)
                return ""
