"""Lightweight page-content extractor — plain text, no JS rendering."""

from __future__ import annotations

import asyncio
import logging
import re
import time
import urllib.parse
import urllib.robotparser
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)

_DEFAULT_USER_AGENT = "CrucibleBot/1.0 (+https://github.com/crucible)"
_REQUESTS_PER_SECOND = 1.0
_CONNECT_TIMEOUT = 10.0
_READ_TIMEOUT = 20.0
_MAX_CONTENT_LENGTH = 500_000  # 500 KB — skip huge pages


@dataclass
class ScrapedPage:
    url: str
    title: str
    text: str
    status_code: int
    error: str | None = None


class _RateLimiter:
    """Simple per-host token-bucket rate limiter."""

    def __init__(self, rate: float = _REQUESTS_PER_SECOND) -> None:
        self._rate = rate
        self._last: dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def acquire(self, host: str) -> None:
        async with self._lock:
            last = self._last.get(host, 0.0)
            wait = (1.0 / self._rate) - (time.monotonic() - last)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last[host] = time.monotonic()


class PageScraper:
    """
    Fetch and extract plain text from web pages.

    Features:
    - Respects robots.txt (cached per host).
    - Per-host rate limiting (default: 1 req/s).
    - Strips scripts, styles, and HTML tags; returns clean text.
    - Enforces a max content-length to avoid downloading huge pages.
    """

    def __init__(
        self,
        user_agent: str = _DEFAULT_USER_AGENT,
        requests_per_second: float = _REQUESTS_PER_SECOND,
        timeout: float = _READ_TIMEOUT,
        respect_robots: bool = True,
    ) -> None:
        self._ua = user_agent
        self._rate_limiter = _RateLimiter(requests_per_second)
        self._timeout = timeout
        self._respect_robots = respect_robots
        self._robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}

    async def scrape(self, url: str) -> ScrapedPage:
        """Fetch *url* and return a ScrapedPage with extracted text."""
        parsed = urllib.parse.urlparse(url)
        host = parsed.netloc

        if self._respect_robots and not await self._is_allowed(url, parsed):
            return ScrapedPage(
                url=url,
                title="",
                text="",
                status_code=0,
                error="Blocked by robots.txt",
            )

        await self._rate_limiter.acquire(host)

        headers = {"User-Agent": self._ua, "Accept": "text/html"}
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(connect=_CONNECT_TIMEOUT, read=self._timeout, write=5, pool=5),
            follow_redirects=True,
            headers=headers,
        ) as client:
            try:
                async with client.stream("GET", url) as resp:
                    if resp.headers.get("content-type", "").split(";")[0].strip() not in (
                        "text/html", "text/plain", "application/xhtml+xml"
                    ):
                        return ScrapedPage(
                            url=url, title="", text="", status_code=resp.status_code,
                            error="Non-HTML content type"
                        )
                    chunks: list[bytes] = []
                    total = 0
                    async for chunk in resp.aiter_bytes(chunk_size=8192):
                        total += len(chunk)
                        if total > _MAX_CONTENT_LENGTH:
                            break
                        chunks.append(chunk)
                    html = b"".join(chunks).decode("utf-8", errors="replace")
                    status = resp.status_code

            except httpx.HTTPError as exc:
                logger.warning("Scrape failed for %s: %s", url, exc)
                return ScrapedPage(url=url, title="", text="", status_code=0, error=str(exc))

        title, text = _extract_text(html)
        return ScrapedPage(url=url, title=title, text=text, status_code=status)

    async def _is_allowed(
        self, url: str, parsed: urllib.parse.ParseResult
    ) -> bool:
        origin = f"{parsed.scheme}://{parsed.netloc}"
        rp = self._robots_cache.get(origin)
        if rp is None:
            rp = urllib.robotparser.RobotFileParser()
            robots_url = f"{origin}/robots.txt"
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(robots_url, headers={"User-Agent": self._ua})
                    rp.parse(resp.text.splitlines())
            except Exception:
                # If we can't fetch robots.txt, assume allowed
                rp.allow_all = True  # type: ignore[attr-defined]
            self._robots_cache[origin] = rp
        return rp.can_fetch(self._ua, url)


# ---------------------------------------------------------------------------
# HTML text extraction (no external dep required)
# ---------------------------------------------------------------------------

_REMOVE_TAGS = re.compile(
    r"<(script|style|noscript|nav|footer|header|aside)[^>]*>.*?</\1>",
    re.DOTALL | re.IGNORECASE,
)
_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s{2,}")
_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.DOTALL | re.IGNORECASE)
_HTML_ENTITIES = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&#39;": "'", "&nbsp;": " "}


def _decode_entities(text: str) -> str:
    for entity, char in _HTML_ENTITIES.items():
        text = text.replace(entity, char)
    return text


def _extract_text(html: str) -> tuple[str, str]:
    """Return (title, plain_text) from raw HTML."""
    title_m = _TITLE_RE.search(html)
    title = _decode_entities(_TAG_RE.sub("", title_m.group(1))).strip() if title_m else ""

    # Strip noisy blocks first
    cleaned = _REMOVE_TAGS.sub(" ", html)
    # Strip remaining tags
    text = _TAG_RE.sub(" ", cleaned)
    text = _decode_entities(text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return title, text
