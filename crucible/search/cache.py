"""LRU cache with TTL for search results — avoids hammering external APIs."""

from __future__ import annotations

import asyncio
import time
from collections import OrderedDict

from .result import SearchResult


class SearchCache:
    """
    Thread-safe async LRU cache with per-entry TTL.

    Eviction policy:
    - LRU: when max_size is exceeded, the least-recently-used entry is dropped.
    - TTL: entries older than ttl_seconds are treated as missing on next access.
    """

    def __init__(self, max_size: int = 100, ttl_seconds: float = 3600.0) -> None:
        self._cache: OrderedDict[str, tuple[list[SearchResult], float]] = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0

    async def get(self, key: str) -> list[SearchResult] | None:
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None
            results, ts = entry
            if time.monotonic() - ts > self._ttl:
                del self._cache[key]
                self._misses += 1
                return None
            self._cache.move_to_end(key)
            self._hits += 1
            return results

    async def set(self, key: str, results: list[SearchResult]) -> None:
        async with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = (results, time.monotonic())
            while len(self._cache) > self._max_size:
                self._cache.popitem(last=False)

    async def invalidate(self, key: str) -> None:
        async with self._lock:
            self._cache.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()

    def size(self) -> int:
        return len(self._cache)

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total else 0.0
