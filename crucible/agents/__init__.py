"""Crucible agents."""

from .course_builder import CourseBuilderAgent
from .debate_council import DebateCouncilAgent
from .forecaster import ForecasterAgent
from .learning import LearningAgent
from .pattern_analyst import PatternAnalystAgent
from .publisher import PublisherAgent
from .research import ResearchAgent
from .scanner import ScannerAgent
from .visualizer import VisualizerAgent

__all__ = [
    "CourseBuilderAgent",
    "DebateCouncilAgent",
    "ForecasterAgent",
    "LearningAgent",
    "PatternAnalystAgent",
    "PublisherAgent",
    "ResearchAgent",
    "ScannerAgent",
    "VisualizerAgent",
]
