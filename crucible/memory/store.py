"""Persistent learning memory — stores and retrieves learnings across sessions."""

from __future__ import annotations

import json
import asyncio
import aiofiles  # type: ignore[import]
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    id: str
    agent_name: str
    topic: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = 0
    last_accessed: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        d = self.model_dump()
        d["created_at"] = self.created_at.isoformat()
        d["last_accessed"] = self.last_accessed.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryEntry":
        data = dict(data)
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("last_accessed"), str):
            data["last_accessed"] = datetime.fromisoformat(data["last_accessed"])
        return cls(**data)


class MemoryStore:
    """
    File-backed persistent memory store for cross-session learning.

    Entries are stored as newline-delimited JSON for simplicity and
    human readability. No external database required.
    """

    def __init__(self, store_path: str | Path = ".crucible_memory.jsonl") -> None:
        self._path = Path(store_path)
        self._entries: dict[str, MemoryEntry] = {}
        self._lock = asyncio.Lock()
        self._loaded = False

    async def load(self) -> None:
        """Load entries from disk."""
        async with self._lock:
            if not self._path.exists():
                self._loaded = True
                return
            async with aiofiles.open(self._path, "r") as f:
                async for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            entry = MemoryEntry.from_dict(data)
                            self._entries[entry.id] = entry
                        except (json.JSONDecodeError, Exception):
                            pass
            self._loaded = True

    async def save(self, entry: MemoryEntry) -> None:
        """Persist a new entry."""
        if not self._loaded:
            await self.load()

        async with self._lock:
            self._entries[entry.id] = entry
            async with aiofiles.open(self._path, "a") as f:
                await f.write(json.dumps(entry.to_dict()) + "\n")

    async def search(
        self,
        query: str,
        agent_name: str | None = None,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """Simple keyword search over memory entries."""
        if not self._loaded:
            await self.load()

        query_lower = query.lower()
        results: list[MemoryEntry] = []

        async with self._lock:
            for entry in self._entries.values():
                if agent_name and entry.agent_name != agent_name:
                    continue
                if (
                    query_lower in entry.content.lower()
                    or query_lower in entry.topic.lower()
                ):
                    results.append(entry)

        # Sort by access count (most accessed = most useful), then recency
        results.sort(key=lambda e: (-e.access_count, -e.created_at.timestamp()))

        # Update access counts
        async with self._lock:
            for entry in results[:limit]:
                entry.access_count += 1
                entry.last_accessed = datetime.utcnow()

        return results[:limit]

    async def all_entries(self) -> list[MemoryEntry]:
        if not self._loaded:
            await self.load()
        async with self._lock:
            return sorted(self._entries.values(), key=lambda e: -e.created_at.timestamp())

    async def clear(self) -> None:
        async with self._lock:
            self._entries.clear()
            if self._path.exists():
                self._path.unlink()

    def __len__(self) -> int:
        return len(self._entries)
