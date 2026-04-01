"""crucible.search — live web search integration.

Usage::

    from crucible.search import get_search_engine, SearchResult

    engine = get_search_engine()           # reads CRUCIBLE_SEARCH_ENGINE env var
    results = await engine.search("query")

Environment variables
---------------------
CRUCIBLE_SEARCH_ENGINE   ``duckduckgo`` (default) or ``brave``
CRUCIBLE_BRAVE_API_KEY   Required when using the Brave backend
"""

from __future__ import annotations

import os

from .cache import SearchCache
from .engine import SearchEngine
from .result import SearchResult
from .scraper import PageScraper, ScrapedPage

__all__ = [
    "SearchEngine",
    "SearchResult",
    "SearchCache",
    "PageScraper",
    "ScrapedPage",
    "get_search_engine",
]


def get_search_engine(
    engine: str | None = None,
    brave_api_key: str | None = None,
    cache: SearchCache | None = None,
) -> SearchEngine:
    """
    Factory that returns a configured search engine.

    Parameters
    ----------
    engine:
        ``"duckduckgo"`` or ``"brave"``. Defaults to the value of
        ``CRUCIBLE_SEARCH_ENGINE`` env var, or ``"duckduckgo"``.
    brave_api_key:
        Brave Search API key. Defaults to ``CRUCIBLE_BRAVE_API_KEY`` env var.
    cache:
        Shared ``SearchCache`` instance. A new one is created if not provided.
    """
    backend = (engine or os.environ.get("CRUCIBLE_SEARCH_ENGINE", "duckduckgo")).lower()

    if backend == "brave":
        key = brave_api_key or os.environ.get("CRUCIBLE_BRAVE_API_KEY", "")
        from .brave import BraveSearchEngine
        return BraveSearchEngine(api_key=key, cache=cache)

    from .duckduckgo import DuckDuckGoEngine
    return DuckDuckGoEngine(cache=cache)
