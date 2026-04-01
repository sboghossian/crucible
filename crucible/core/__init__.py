"""Crucible core — orchestrator, base agent, shared state, event bus."""

from .agent import AgentConfig, AgentResult, BaseAgent
from .events import Event, EventBus, EventType
from .orchestrator import Orchestrator
from .state import (
    DebateResult,
    ForecastResult,
    LearningRecord,
    PatternResult,
    ResearchResult,
    RunState,
    ScanResult,
    SharedState,
)

__all__ = [
    "AgentConfig",
    "AgentResult",
    "BaseAgent",
    "Event",
    "EventBus",
    "EventType",
    "Orchestrator",
    "DebateResult",
    "ForecastResult",
    "LearningRecord",
    "PatternResult",
    "ResearchResult",
    "RunState",
    "ScanResult",
    "SharedState",
]
