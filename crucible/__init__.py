"""
Crucible — A multi-agent research framework with adversarial debate councils.

Every decision goes through the 4-persona Debate Council.
No shortcuts. No consensus by default. The best argument wins.
"""

from .core.orchestrator import Orchestrator
from .core.agent import AgentConfig, AgentResult, BaseAgent
from .core.state import SharedState, RunState
from .core.events import EventBus, Event, EventType
from .debate import DebateProtocol, format_summary

__version__ = "0.1.0"

__all__ = [
    "Orchestrator",
    "AgentConfig",
    "AgentResult",
    "BaseAgent",
    "SharedState",
    "RunState",
    "EventBus",
    "Event",
    "EventType",
    "DebateProtocol",
    "format_summary",
]
