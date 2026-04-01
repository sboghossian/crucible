"""SearchResult dataclass — the unit of data returned by any search engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str = "unknown"
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def cite(self) -> str:
        """Return a Markdown citation string."""
        return f"[{self.title}]({self.url})"

    def to_context_line(self) -> str:
        """One-liner suitable for injecting into an LLM prompt."""
        return f"- {self.cite()}: {self.snippet}"
