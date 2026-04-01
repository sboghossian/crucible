"""Shared state management with typed pydantic access."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, TypeVar, Type
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class ScanResult(BaseModel):
    repo_path: str
    languages: dict[str, int] = Field(default_factory=dict)
    file_count: int = 0
    total_lines: int = 0
    dependencies: list[str] = Field(default_factory=list)
    structure: dict[str, Any] = Field(default_factory=dict)
    git_stats: dict[str, Any] = Field(default_factory=dict)
    summary: str = ""


class ResearchResult(BaseModel):
    query: str
    findings: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    synthesis: str = ""


class PatternResult(BaseModel):
    patterns: list[dict[str, Any]] = Field(default_factory=list)
    anti_patterns: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class DebateResult(BaseModel):
    topic: str
    winner: str = ""
    winner_score: float = 0.0
    decision: str = ""
    rounds: list[dict[str, Any]] = Field(default_factory=list)
    scores: dict[str, float] = Field(default_factory=dict)
    dissenting_views: list[str] = Field(default_factory=list)


class ForecastResult(BaseModel):
    horizon: str = "6 months"
    predictions: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.0
    key_risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)


class LearningRecord(BaseModel):
    agent_name: str
    observation: str
    pattern: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RunState(BaseModel):
    run_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None
    status: str = "running"
    subject: str = ""
    scan: ScanResult | None = None
    research: ResearchResult | None = None
    patterns: PatternResult | None = None
    debate: DebateResult | None = None
    forecast: ForecastResult | None = None
    learning_records: list[LearningRecord] = Field(default_factory=list)
    visualizations: list[dict[str, Any]] = Field(default_factory=list)
    course: dict[str, Any] = Field(default_factory=dict)
    github_report: dict[str, Any] = Field(default_factory=dict)
    errors: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SharedState:
    """Thread-safe shared state container for all agents in a run."""

    def __init__(self, run_id: str, subject: str = "") -> None:
        self._state = RunState(run_id=run_id, subject=subject)
        self._lock = asyncio.Lock()

    async def get(self) -> RunState:
        async with self._lock:
            return self._state.model_copy(deep=True)

    async def update(self, **kwargs: Any) -> None:
        async with self._lock:
            for key, value in kwargs.items():
                if hasattr(self._state, key):
                    setattr(self._state, key, value)
                else:
                    raise KeyError(f"RunState has no field '{key}'")

    async def set_typed(self, field: str, model: BaseModel) -> None:
        async with self._lock:
            if hasattr(self._state, field):
                setattr(self._state, field, model)
            else:
                raise KeyError(f"RunState has no field '{field}'")

    async def append_error(self, agent: str, error: str) -> None:
        async with self._lock:
            self._state.errors.append(
                {"agent": agent, "error": error, "timestamp": datetime.utcnow().isoformat()}
            )

    async def append_learning(self, record: LearningRecord) -> None:
        async with self._lock:
            self._state.learning_records.append(record)

    async def snapshot(self) -> dict[str, Any]:
        async with self._lock:
            return self._state.model_dump()
