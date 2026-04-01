"""Abstract base class for all search engine implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .result import SearchResult


class SearchEngine(ABC):
    """Contract that every search backend must satisfy."""

    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        """Execute a search and return up to *max_results* results."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier used in logging and result.source."""
        ...
