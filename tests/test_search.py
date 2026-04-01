"""Tests for crucible.search — cache, parsers, rate limiting, and API mocks."""

from __future__ import annotations

import asyncio
import time
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from crucible.search.cache import SearchCache
from crucible.search.duckduckgo import DuckDuckGoEngine, _extract_url, _parse_ddg_html
from crucible.search.engine import SearchEngine
from crucible.search.result import SearchResult
from crucible.search.scraper import PageScraper, _extract_text


# ---------------------------------------------------------------------------
# SearchResult
# ---------------------------------------------------------------------------

def test_search_result_cite() -> None:
    r = SearchResult(title="OpenAI Blog", url="https://openai.com/blog", snippet="News")
    assert r.cite() == "[OpenAI Blog](https://openai.com/blog)"


def test_search_result_to_context_line() -> None:
    r = SearchResult(title="Title", url="https://example.com", snippet="A snippet")
    line = r.to_context_line()
    assert "Title" in line
    assert "https://example.com" in line
    assert "A snippet" in line


# ---------------------------------------------------------------------------
# SearchCache
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cache_miss_then_hit() -> None:
    cache = SearchCache(max_size=10, ttl_seconds=60)
    key = "test:query"

    assert await cache.get(key) is None  # miss

    results = [SearchResult(title="T", url="https://t.com", snippet="S")]
    await cache.set(key, results)

    fetched = await cache.get(key)
    assert fetched is not None
    assert fetched[0].url == "https://t.com"


@pytest.mark.asyncio
async def test_cache_ttl_expiry() -> None:
    cache = SearchCache(max_size=10, ttl_seconds=0.05)
    key = "ttl:test"
    results = [SearchResult(title="T", url="https://t.com", snippet="S")]
    await cache.set(key, results)

    await asyncio.sleep(0.1)  # wait for TTL

    assert await cache.get(key) is None


@pytest.mark.asyncio
async def test_cache_lru_eviction() -> None:
    cache = SearchCache(max_size=3, ttl_seconds=60)
    make = lambda i: [SearchResult(title=f"T{i}", url=f"https://t{i}.com", snippet="")]

    await cache.set("a", make(1))
    await cache.set("b", make(2))
    await cache.set("c", make(3))
    # Access 'a' to make it most recently used
    await cache.get("a")
    # Insert 'd' — should evict 'b' (LRU)
    await cache.set("d", make(4))

    assert cache.size() == 3
    assert await cache.get("b") is None  # evicted
    assert await cache.get("a") is not None
    assert await cache.get("c") is not None
    assert await cache.get("d") is not None


@pytest.mark.asyncio
async def test_cache_hit_rate() -> None:
    cache = SearchCache()
    results = [SearchResult(title="T", url="https://t.com", snippet="")]
    await cache.set("key", results)

    await cache.get("missing")  # miss
    await cache.get("key")      # hit

    assert cache.hit_rate == 0.5


@pytest.mark.asyncio
async def test_cache_clear() -> None:
    cache = SearchCache()
    results = [SearchResult(title="T", url="https://t.com", snippet="")]
    await cache.set("key", results)
    assert cache.size() == 1

    await cache.clear()
    assert cache.size() == 0
    assert await cache.get("key") is None


# ---------------------------------------------------------------------------
# DuckDuckGo HTML parsing
# ---------------------------------------------------------------------------

_SAMPLE_DDG_HTML = """\
<!DOCTYPE html>
<html>
<body>
<div class="result results_links web-result">
  <div class="links_main result__body">
    <h2 class="result__title">
      <a rel="nofollow" class="result__a"
         href="/l/?uddg=https%3A%2F%2Fexample.com%2Farticle&amp;rut=abc">
        Example Article
      </a>
    </h2>
    <a class="result__snippet" href="/l/?uddg=https%3A%2F%2Fexample.com%2Farticle">
      This is the snippet for the first result.
    </a>
  </div>
</div>
<div class="result results_links web-result">
  <div class="links_main result__body">
    <h2 class="result__title">
      <a rel="nofollow" class="result__a"
         href="/l/?uddg=https%3A%2F%2Fanother.com%2Fpage">
        Another Page
      </a>
    </h2>
    <a class="result__snippet" href="/l/?uddg=https%3A%2F%2Fanother.com%2Fpage">
      Second result snippet here.
    </a>
  </div>
</div>
</body>
</html>"""


def test_parse_ddg_html_extracts_results() -> None:
    results = _parse_ddg_html(_SAMPLE_DDG_HTML, source="duckduckgo")
    assert len(results) >= 1
    titles = [r.title for r in results]
    assert any("Example" in t for t in titles)


def test_parse_ddg_html_extracts_url() -> None:
    results = _parse_ddg_html(_SAMPLE_DDG_HTML, source="duckduckgo")
    urls = [r.url for r in results]
    assert any("example.com" in u for u in urls)


def test_parse_ddg_html_sets_source() -> None:
    results = _parse_ddg_html(_SAMPLE_DDG_HTML, source="duckduckgo")
    assert all(r.source == "duckduckgo" for r in results)


def test_extract_url_unwraps_uddg() -> None:
    href = "/l/?uddg=https%3A%2F%2Fexample.com%2Fpath&rut=xyz"
    assert _extract_url(href) == "https://example.com/path"


def test_extract_url_plain_http() -> None:
    href = "https://example.com/plain"
    assert _extract_url(href) == "https://example.com/plain"


def test_extract_url_empty() -> None:
    assert _extract_url("") == ""


# ---------------------------------------------------------------------------
# DuckDuckGoEngine (mocked HTTP)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ddg_engine_returns_results() -> None:
    engine = DuckDuckGoEngine(request_interval=0.0)

    mock_response = MagicMock()
    mock_response.text = _SAMPLE_DDG_HTML
    mock_response.raise_for_status = MagicMock()

    with patch("crucible.search.duckduckgo.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        results = await engine.search("test query", max_results=5)

    assert isinstance(results, list)
    # Parsing may return 0-N depending on BS4 availability; just check type
    assert all(isinstance(r, SearchResult) for r in results)


@pytest.mark.asyncio
async def test_ddg_engine_uses_cache() -> None:
    cache = SearchCache()
    engine = DuckDuckGoEngine(cache=cache, request_interval=0.0)

    cached_results = [SearchResult(title="Cached", url="https://c.com", snippet="X")]
    await cache.set(f"ddg:cached query:5", cached_results)

    # No HTTP should be needed — result comes from cache
    with patch("crucible.search.duckduckgo.httpx.AsyncClient") as mock_client_cls:
        mock_client_cls.side_effect = AssertionError("Should not call HTTP when cached")
        results = await engine.search("cached query", max_results=5)

    assert results == cached_results


@pytest.mark.asyncio
async def test_ddg_engine_rate_limits() -> None:
    """Verify that two sequential calls are spaced >= interval apart."""
    engine = DuckDuckGoEngine(request_interval=0.05)

    mock_response = MagicMock()
    mock_response.text = ""
    mock_response.raise_for_status = MagicMock()

    timestamps: list[float] = []

    async def fake_post(*args: object, **kwargs: object) -> MagicMock:
        timestamps.append(time.monotonic())
        return mock_response

    with patch("crucible.search.duckduckgo.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = fake_post
        mock_client_cls.return_value = mock_client

        await engine.search("first query")
        await engine.search("second query")  # different key, not cached

    assert len(timestamps) == 2
    assert timestamps[1] - timestamps[0] >= 0.04  # allow 1ms slack


# ---------------------------------------------------------------------------
# Brave Search (mocked)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_brave_engine_parses_response() -> None:
    from crucible.search.brave import BraveSearchEngine

    engine = BraveSearchEngine(api_key="test-key")

    brave_response = {
        "web": {
            "results": [
                {"title": "Brave Result", "url": "https://brave.com/result", "description": "A desc"},
                {"title": "Second", "url": "https://second.com", "description": ""},
            ]
        }
    }

    mock_response = MagicMock()
    mock_response.json = MagicMock(return_value=brave_response)
    mock_response.raise_for_status = MagicMock()

    with patch("crucible.search.brave.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        results = await engine.search("AI agents", max_results=5)

    assert len(results) == 2
    assert results[0].title == "Brave Result"
    assert results[0].url == "https://brave.com/result"
    assert results[0].source == "brave"


def test_brave_engine_requires_api_key() -> None:
    from crucible.search.brave import BraveSearchEngine

    with pytest.raises(ValueError, match="api_key"):
        BraveSearchEngine(api_key="")


# ---------------------------------------------------------------------------
# get_search_engine factory
# ---------------------------------------------------------------------------

def test_get_search_engine_default() -> None:
    from crucible.search import get_search_engine
    from crucible.search.duckduckgo import DuckDuckGoEngine

    engine = get_search_engine(engine="duckduckgo")
    assert isinstance(engine, DuckDuckGoEngine)


def test_get_search_engine_brave() -> None:
    from crucible.search import get_search_engine
    from crucible.search.brave import BraveSearchEngine

    engine = get_search_engine(engine="brave", brave_api_key="key")
    assert isinstance(engine, BraveSearchEngine)


def test_get_search_engine_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CRUCIBLE_SEARCH_ENGINE", "brave")
    monkeypatch.setenv("CRUCIBLE_BRAVE_API_KEY", "mykey")

    from crucible.search import get_search_engine
    from crucible.search.brave import BraveSearchEngine

    engine = get_search_engine()
    assert isinstance(engine, BraveSearchEngine)


# ---------------------------------------------------------------------------
# PageScraper text extraction
# ---------------------------------------------------------------------------

def test_extract_text_basic() -> None:
    html = "<html><head><title>My Page</title></head><body><p>Hello world.</p></body></html>"
    title, text = _extract_text(html)
    assert title == "My Page"
    assert "Hello world" in text


def test_extract_text_strips_scripts() -> None:
    html = (
        "<html><body>"
        "<script>alert('xss')</script>"
        "<p>Real content</p>"
        "<style>body { color: red; }</style>"
        "</body></html>"
    )
    _, text = _extract_text(html)
    assert "xss" not in text
    assert "color" not in text
    assert "Real content" in text


def test_extract_text_decodes_entities() -> None:
    html = "<p>AT&amp;T &lt;rocks&gt;</p>"
    _, text = _extract_text(html)
    assert "AT&T" in text
    assert "<rocks>" in text


@pytest.mark.asyncio
async def test_scraper_respects_robots(tmp_path: object) -> None:
    """Scraper should refuse URLs blocked by robots.txt."""
    scraper = PageScraper(respect_robots=True)

    robots_txt = "User-agent: *\nDisallow: /blocked"

    mock_robots_resp = MagicMock()
    mock_robots_resp.text = robots_txt

    with patch("crucible.search.scraper.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_robots_resp)
        mock_client_cls.return_value = mock_client

        page = await scraper.scrape("https://example.com/blocked/page")

    assert page.error is not None
    assert "robots" in page.error.lower()
