"""Main supervisor agent — coordinates all agents and routes every decision through the Debate Council."""

from __future__ import annotations

import asyncio
import uuid
import logging
from datetime import datetime
from typing import Any

import anthropic

from .agent import AgentConfig, AgentResult, BaseAgent
from .events import Event, EventBus, EventType
from .state import DebateResult, SharedState
from ..debate.personas import Persona
from ..debate.protocol import DebateProtocol
from ..debate.resolver import format_summary, resolve, to_debate_result
from ..memory.sqlite_store import SQLiteMemoryStore

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Coordinates all Crucible agents for a research run.

    Every fork-in-the-road decision is routed through `decide()`, which
    runs the full 3-round adversarial Debate Council before returning a
    resolution. No decision is made unilaterally.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-opus-4-6",
        debate_model: str = "claude-opus-4-6",
        max_tokens: int = 4096,
        db_path: str = ".crucible_memory.db",
    ) -> None:
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model
        self._debate_protocol = DebateProtocol(
            client=self._client,
            model=debate_model,
            max_tokens=1024,
        )
        self._config = AgentConfig(model=model, max_tokens=max_tokens)
        self._agents: list[BaseAgent] = []
        self._bus: EventBus | None = None
        self._state: SharedState | None = None
        self._memory = SQLiteMemoryStore(db_path=db_path)
        # Plugin registrations — populated via register_plugin() / load_plugins_from()
        self._plugin_classes: dict[str, type[BaseAgent]] = {}

    # ------------------------------------------------------------------ #
    # Plugin API                                                          #
    # ------------------------------------------------------------------ #

    def register_plugin(self, cls: type[BaseAgent], name: str | None = None) -> None:
        """Register a single plugin agent class with this orchestrator."""
        plugin_name = name or getattr(cls, "name", cls.__name__)
        self._plugin_classes[plugin_name] = cls
        logger.debug("Orchestrator registered plugin: %s", plugin_name)

    def load_plugins_from(self, directory: str) -> None:
        """
        Discover and register all plugins from a directory.

        This delegates to PluginLoader which imports .py files, triggering
        @agent_plugin decorators. After loading, all newly registered plugins
        from the global PluginRegistry are synced into this orchestrator.
        """
        from ..plugins.loader import PluginLoader
        from ..plugins.registry import PluginRegistry

        before = {r.name for r in PluginRegistry.instance().list_plugins()}
        loader = PluginLoader()
        loader.load_from_directory(directory)
        after = {r.name for r in PluginRegistry.instance().list_plugins()}
        new_names = after - before

        for name in new_names:
            reg = PluginRegistry.instance().get(name)
            if reg is not None:
                self._plugin_classes[name] = reg.cls

    def load_plugin_module(self, dotted_path: str) -> None:
        """Register a plugin from a dotted module path, e.g. 'my_pkg.MyAgent'."""
        from ..plugins.loader import PluginLoader
        from ..plugins.registry import PluginRegistry

        before = {r.name for r in PluginRegistry.instance().list_plugins()}
        loader = PluginLoader()
        loader.load_from_module(dotted_path)
        after = {r.name for r in PluginRegistry.instance().list_plugins()}

        for name in after - before:
            reg = PluginRegistry.instance().get(name)
            if reg is not None:
                self._plugin_classes[name] = reg.cls

    def sync_plugins_from_registry(self) -> None:
        """Pull all currently registered global plugins into this orchestrator."""
        from ..plugins.registry import PluginRegistry
        for reg in PluginRegistry.instance().list_plugins():
            self._plugin_classes[reg.name] = reg.cls

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    async def run(
        self,
        subject: str,
        repo_path: str | None = None,
        research_query: str | None = None,
        run_agents: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a full research run on `subject`.

        Args:
            subject: What we are researching (project name, question, etc.)
            repo_path: Optional path to a git repo for the Scanner agent.
            research_query: Optional web research query. Defaults to subject.
            run_agents: Subset of agent names to run. Defaults to all.

        Returns:
            Full state snapshot as a dict.
        """
        run_id = str(uuid.uuid4())[:8]
        self._state = SharedState(run_id=run_id, subject=subject)
        self._bus = EventBus()

        await self._bus.publish(Event(
            type=EventType.ORCHESTRATOR_STARTED,
            source="orchestrator",
            payload={"subject": subject, "run_id": run_id},
            run_id=run_id,
        ))

        # Register the learning agent as a wildcard listener before anything runs
        from ..agents.learning import LearningAgent
        learning_agent = LearningAgent(
            client=self._client,
            state=self._state,
            bus=self._bus,
            config=self._config,
        )
        self._bus.subscribe_all(learning_agent.on_event)

        builtin_agents = [
            "scanner", "research", "pattern_analyst", "debate",
            "forecast", "visualizer", "course_builder", "publisher",
        ]
        agents_to_run = set(run_agents or (builtin_agents + list(self._plugin_classes)))

        # Phase 1: Data gathering (parallel where possible)
        phase1_tasks = []
        if "scanner" in agents_to_run and repo_path:
            phase1_tasks.append(self._run_scanner(repo_path))
        if "research" in agents_to_run:
            phase1_tasks.append(self._run_research(research_query or subject))

        if phase1_tasks:
            await asyncio.gather(*phase1_tasks, return_exceptions=True)

        # Phase 2: Analysis (depends on phase 1)
        if "pattern_analyst" in agents_to_run:
            await self._run_pattern_analyst(subject)

        # Phase 3: Debate — the crown jewel
        if "debate" in agents_to_run:
            # Decide the primary research recommendation via debate
            state = await self._state.get()
            debate_context = self._build_debate_context(state)
            await self.decide(
                topic=f"What is the most important insight or recommendation for: {subject}",
                context=debate_context,
                options=[
                    "Focus on technical architecture improvements",
                    "Focus on developer experience and adoption",
                    "Focus on long-term strategic positioning",
                    "Focus on immediate practical quick-wins",
                ],
            )

        # Phase 4: Forward-looking (parallel)
        phase4_tasks = []
        if "forecast" in agents_to_run:
            phase4_tasks.append(self._run_forecast(subject))
        if "visualizer" in agents_to_run:
            phase4_tasks.append(self._run_visualizer(subject))
        if phase4_tasks:
            await asyncio.gather(*phase4_tasks, return_exceptions=True)

        # Phase 5: Output
        if "course_builder" in agents_to_run:
            await self._run_course_builder(subject)
        if "publisher" in agents_to_run:
            await self._run_publisher(subject)

        # Phase 6: Plugin agents
        from ..plugins.hooks import HookRegistry
        hook_registry = HookRegistry.instance()
        await hook_registry.fire("before_run", subject=subject, run_id=run_id)
        plugin_tasks = []
        for name, cls in self._plugin_classes.items():
            if name in agents_to_run:
                plugin_tasks.append(self._run_plugin_agent(cls, name, subject=subject))
        if plugin_tasks:
            await asyncio.gather(*plugin_tasks, return_exceptions=True)
        await hook_registry.fire("after_run", subject=subject, run_id=run_id)

        await self._state.update(
            status="complete",
            finished_at=datetime.utcnow(),
        )

        await self._bus.publish(Event(
            type=EventType.ORCHESTRATOR_COMPLETED,
            source="orchestrator",
            payload={"run_id": run_id},
            run_id=run_id,
        ))

        return await self._state.snapshot()

    async def decide(
        self,
        topic: str,
        context: str = "",
        options: list[str] | None = None,
        verbose: bool = False,
    ) -> DebateResult:
        """
        Route any decision through the full 3-round Debate Council.

        This is the primary decision-making API. Every fork in the road —
        naming, prioritization, architecture, interpretation, KPIs, next steps —
        goes through here.

        Args:
            topic: The decision or question to debate.
            context: Background information for the debaters.
            options: Candidate answers/options. Can be empty for open debates.
            verbose: If True, log the full transcript.

        Returns:
            DebateResult stored in shared state.
        """
        if self._state is None or self._bus is None:
            raise RuntimeError("Orchestrator.run() must be called before decide()")

        run_state = await self._state.get()

        logger.info("Debate Council convened: %s", topic)

        await self._bus.publish(Event(
            type=EventType.DEBATE_ROUND_STARTED,
            source="orchestrator",
            payload={"topic": topic, "options": options or []},
            run_id=run_state.run_id,
        ))

        transcript = await self._debate_protocol.run(
            topic=topic,
            context=context,
            options=options or [],
        )
        result = to_debate_result(transcript)

        await self._state.set_typed("debate", result)

        resolution = resolve(transcript)
        summary = format_summary(resolution, verbose=verbose)
        logger.info("\n%s", summary)

        # Persist debate and decision to SQLite
        debate_id = str(uuid.uuid4())
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self._memory.save_debate(
                debate_id=debate_id,
                topic=topic,
                rounds=result.rounds,
                winner=result.winner,
                scores=result.scores,
            ),
        )
        if result.decision:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._memory.save_decision(
                    debate_id=debate_id,
                    decision=result.decision,
                    rationale=summary,
                    confidence=result.winner_score / 10.0,
                ),
            )

        await self._bus.publish(Event(
            type=EventType.DEBATE_COMPLETED,
            source="orchestrator",
            payload={
                "topic": topic,
                "winner": result.winner,
                "winner_score": result.winner_score,
                "summary": summary,
            },
            run_id=run_state.run_id,
        ))

        return result

    # ------------------------------------------------------------------ #
    # Standalone debate (no full run required)                            #
    # ------------------------------------------------------------------ #

    async def standalone_debate(
        self,
        topic: str,
        context: str = "",
        options: list[str] | None = None,
        verbose: bool = True,
        personas: list[Persona] | None = None,
    ) -> DebateResult:
        """
        Run a debate without a full research run.
        Creates ephemeral state for a single decision.

        Args:
            personas: Optional custom persona list. Defaults to the built-in 4.
        """
        run_id = str(uuid.uuid4())[:8]
        self._state = SharedState(run_id=run_id, subject=topic)
        self._bus = EventBus()
        if personas is not None:
            self._debate_protocol = DebateProtocol(
                client=self._client,
                model=self._debate_protocol._model,
                max_tokens=self._debate_protocol._max_tokens,
                personas=personas,
            )
        return await self.decide(
            topic=topic,
            context=context,
            options=options,
            verbose=verbose,
        )

    # ------------------------------------------------------------------ #
    # Private agent runners                                               #
    # ------------------------------------------------------------------ #

    async def _run_scanner(self, repo_path: str) -> AgentResult:
        from ..agents.scanner import ScannerAgent
        agent = ScannerAgent(
            client=self._client,
            state=self._state,  # type: ignore[arg-type]
            bus=self._bus,  # type: ignore[arg-type]
            config=self._config,
        )
        return await agent.execute(repo_path=repo_path)

    async def _run_research(self, query: str) -> AgentResult:
        from ..agents.research import ResearchAgent
        agent = ResearchAgent(
            client=self._client,
            state=self._state,  # type: ignore[arg-type]
            bus=self._bus,  # type: ignore[arg-type]
            config=self._config,
        )
        return await agent.execute(query=query)

    async def _run_pattern_analyst(self, subject: str) -> AgentResult:
        from ..agents.pattern_analyst import PatternAnalystAgent
        agent = PatternAnalystAgent(
            client=self._client,
            state=self._state,  # type: ignore[arg-type]
            bus=self._bus,  # type: ignore[arg-type]
            config=self._config,
        )
        return await agent.execute(subject=subject)

    async def _run_forecast(self, subject: str) -> AgentResult:
        from ..agents.forecaster import ForecasterAgent
        agent = ForecasterAgent(
            client=self._client,
            state=self._state,  # type: ignore[arg-type]
            bus=self._bus,  # type: ignore[arg-type]
            config=self._config,
        )
        return await agent.execute(subject=subject)

    async def _run_visualizer(self, subject: str) -> AgentResult:
        from ..agents.visualizer import VisualizerAgent
        agent = VisualizerAgent(
            client=self._client,
            state=self._state,  # type: ignore[arg-type]
            bus=self._bus,  # type: ignore[arg-type]
            config=self._config,
        )
        return await agent.execute(subject=subject)

    async def _run_course_builder(self, subject: str) -> AgentResult:
        from ..agents.course_builder import CourseBuilderAgent
        agent = CourseBuilderAgent(
            client=self._client,
            state=self._state,  # type: ignore[arg-type]
            bus=self._bus,  # type: ignore[arg-type]
            config=self._config,
        )
        return await agent.execute(subject=subject)

    async def _run_publisher(self, subject: str) -> AgentResult:
        from ..agents.publisher import PublisherAgent
        agent = PublisherAgent(
            client=self._client,
            state=self._state,  # type: ignore[arg-type]
            bus=self._bus,  # type: ignore[arg-type]
            config=self._config,
        )
        return await agent.execute(subject=subject)

    async def _run_plugin_agent(self, cls: type[BaseAgent], name: str, **kwargs: Any) -> AgentResult:
        agent = cls(
            client=self._client,
            state=self._state,  # type: ignore[arg-type]
            bus=self._bus,  # type: ignore[arg-type]
            config=self._config,
        )
        from ..plugins.hooks import HookRegistry
        hooks = HookRegistry.instance()
        try:
            result = await agent.execute(**kwargs)
            return result
        except Exception as exc:
            await hooks.fire("on_error", agent_name=name, error=str(exc))
            raise

    def _build_debate_context(self, state: Any) -> str:
        parts: list[str] = []
        if state.scan:
            parts.append(f"Codebase: {state.scan.summary or 'analyzed'}")
        if state.research:
            parts.append(f"Research: {state.research.synthesis[:300] if state.research.synthesis else 'conducted'}")
        if state.patterns:
            recs = "; ".join(state.patterns.recommendations[:3])
            parts.append(f"Patterns identified: {recs}")
        return "\n".join(parts) if parts else ""
