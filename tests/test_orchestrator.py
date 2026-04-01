"""Tests for Orchestrator — agent coordination, phases, failure handling, events."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from crucible.core.agent import AgentResult
from crucible.core.events import EventBus, EventType
from crucible.core.state import DebateResult, SharedState
from crucible.debate.personas import ALL_PERSONAS
from crucible.debate.protocol import DebateTranscript, Statement


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_mock_client(response_text: str = "Mock LLM response.") -> Any:
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=response_text)]
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_message)
    return mock_client


def make_state(subject: str = "test") -> SharedState:
    return SharedState(run_id=str(uuid.uuid4())[:8], subject=subject)


def make_mock_transcript(
    topic: str = "Test topic",
    winner: str = "pragmatist",
) -> DebateTranscript:
    transcript = DebateTranscript(topic=topic, context="", options=["A", "B"])
    for persona in ALL_PERSONAS:
        for round_num in [1, 2, 3]:
            transcript.statements.append(
                Statement(
                    persona_name=persona.name,
                    round=round_num,
                    content=f"{persona.name} round {round_num} statement.",
                )
            )
    transcript.winner = winner
    transcript.winner_score = 7.5
    transcript.scores = {
        "pragmatist": 7.5,
        "visionary": 6.0,
        "skeptic": 6.5,
        "user_advocate": 5.5,
    }
    transcript.decision = f"[{winner} wins] Final decision."
    transcript.dissenting_views = [
        f"{p.name}: dissenting view."
        for p in ALL_PERSONAS
        if p.name != winner
    ]
    return transcript


# ---------------------------------------------------------------------------
# Orchestrator initialization
# ---------------------------------------------------------------------------


class TestOrchestratorInit:
    def test_initial_state_is_none(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic"):
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            assert orch._state is None

    def test_initial_bus_is_none(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic"):
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            assert orch._bus is None

    def test_initial_agents_list_is_empty(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic"):
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            assert orch._agents == []

    def test_model_is_stored(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic"):
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key", model="claude-opus-4-6")
            assert orch._model == "claude-opus-4-6"

    def test_config_stores_model(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic"):
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key", model="claude-opus-4-6")
            assert orch._config.model == "claude-opus-4-6"


# ---------------------------------------------------------------------------
# Orchestrator.run() tests
# ---------------------------------------------------------------------------


class TestOrchestratorRun:
    async def test_run_initializes_state_and_bus(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            assert orch._state is None

            await orch.run(subject="test subject", run_agents=[])

            assert orch._state is not None
            assert orch._bus is not None

    async def test_run_returns_dict_snapshot(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            result = await orch.run(subject="test subject", run_agents=[])

            assert isinstance(result, dict)
            assert result["subject"] == "test subject"

    async def test_run_sets_status_complete(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            result = await orch.run(subject="test", run_agents=[])

            assert result["status"] == "complete"

    async def test_run_sets_finished_at(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            result = await orch.run(subject="test", run_agents=[])

            assert result["finished_at"] is not None

    async def test_run_publishes_orchestrator_started_event(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            await orch.run(subject="test", run_agents=[])

            history = orch._bus.history()  # type: ignore[union-attr]
            event_types = {e.type for e in history}
            assert EventType.ORCHESTRATOR_STARTED in event_types

    async def test_run_publishes_orchestrator_completed_event(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            await orch.run(subject="test", run_agents=[])

            history = orch._bus.history()  # type: ignore[union-attr]
            event_types = {e.type for e in history}
            assert EventType.ORCHESTRATOR_COMPLETED in event_types

    async def test_run_calls_research_agent_when_in_list(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            mock_result = AgentResult(
                agent_name="research", success=True, output={"synthesis": "test"}
            )

            with patch.object(
                orch, "_run_research", new=AsyncMock(return_value=mock_result)
            ) as mock_research:
                await orch.run(subject="test", run_agents=["research"])

            mock_research.assert_called_once()

    async def test_run_skips_scanner_without_repo_path(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")

            with patch.object(orch, "_run_scanner", new=AsyncMock()) as mock_scanner:
                # scanner in list but no repo_path — must NOT be called
                await orch.run(
                    subject="test", run_agents=["scanner"], repo_path=None
                )

            mock_scanner.assert_not_called()

    async def test_run_calls_scanner_when_repo_path_provided(
        self, tmp_path: Path
    ) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            mock_result = AgentResult(
                agent_name="scanner", success=True, output={}
            )

            with patch.object(
                orch, "_run_scanner", new=AsyncMock(return_value=mock_result)
            ) as mock_scanner:
                await orch.run(
                    subject="test",
                    run_agents=["scanner"],
                    repo_path=str(tmp_path),
                )

            mock_scanner.assert_called_once_with(str(tmp_path))

    async def test_run_phase1_executes_scanner_and_research_in_parallel(
        self, tmp_path: Path
    ) -> None:
        """Both scanner and research agents must run when listed with a repo path."""
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            scanner_called = False
            research_called = False

            async def fake_scanner(path: str) -> AgentResult:
                nonlocal scanner_called
                scanner_called = True
                return AgentResult(agent_name="scanner", success=True, output={})

            async def fake_research(query: str) -> AgentResult:
                nonlocal research_called
                research_called = True
                return AgentResult(agent_name="research", success=True, output={})

            with (
                patch.object(orch, "_run_scanner", new=fake_scanner),
                patch.object(orch, "_run_research", new=fake_research),
            ):
                await orch.run(
                    subject="test",
                    run_agents=["scanner", "research"],
                    repo_path=str(tmp_path),
                )

            assert scanner_called
            assert research_called

    async def test_run_handles_agent_exception_gracefully(self) -> None:
        """If a phase-1 agent raises, the orchestrator must still complete."""
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")

            with patch.object(
                orch,
                "_run_research",
                new=AsyncMock(side_effect=RuntimeError("Simulated LLM failure")),
            ):
                # Should NOT propagate — asyncio.gather uses return_exceptions=True
                result = await orch.run(subject="test", run_agents=["research"])

            assert result["status"] == "complete"

    async def test_run_debate_phase_invokes_debate_protocol(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            mock_transcript = make_mock_transcript()

            with patch.object(
                orch._debate_protocol,
                "run",
                new=AsyncMock(return_value=mock_transcript),
            ) as mock_debate:
                await orch.run(subject="test subject", run_agents=["debate"])

            mock_debate.assert_called_once()

    async def test_run_debate_phase_stores_result_in_state(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            mock_transcript = make_mock_transcript(winner="visionary")

            with patch.object(
                orch._debate_protocol,
                "run",
                new=AsyncMock(return_value=mock_transcript),
            ):
                await orch.run(subject="test", run_agents=["debate"])

            state = await orch._state.get()  # type: ignore[union-attr]
            assert state.debate is not None
            assert state.debate.winner == "visionary"

    async def test_run_with_custom_research_query(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            captured_queries: list[str] = []

            async def capture_query(query: str) -> AgentResult:
                captured_queries.append(query)
                return AgentResult(agent_name="research", success=True, output={})

            with patch.object(orch, "_run_research", new=capture_query):
                await orch.run(
                    subject="default subject",
                    research_query="custom research query",
                    run_agents=["research"],
                )

            assert captured_queries == ["custom research query"]


# ---------------------------------------------------------------------------
# Orchestrator.decide() tests
# ---------------------------------------------------------------------------


class TestOrchestratorDecide:
    async def test_decide_raises_without_prior_run(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic"):
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            with pytest.raises(RuntimeError, match="run\\(\\)"):
                await orch.decide(topic="Test")

    async def test_decide_calls_debate_protocol_with_topic(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            orch._state = make_state()
            orch._bus = EventBus()

            mock_transcript = make_mock_transcript()
            with patch.object(
                orch._debate_protocol,
                "run",
                new=AsyncMock(return_value=mock_transcript),
            ) as mock_run:
                await orch.decide(
                    topic="Should we use microservices?",
                    options=["yes", "no"],
                )

            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert "Should we use microservices?" in str(call_args)

    async def test_decide_stores_result_in_state(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            orch._state = make_state()
            orch._bus = EventBus()

            mock_transcript = make_mock_transcript(winner="skeptic")
            with patch.object(
                orch._debate_protocol,
                "run",
                new=AsyncMock(return_value=mock_transcript),
            ):
                await orch.decide(topic="Test decision")

            state = await orch._state.get()
            assert state.debate is not None
            assert state.debate.winner == "skeptic"

    async def test_decide_returns_debate_result_type(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            orch._state = make_state()
            orch._bus = EventBus()

            mock_transcript = make_mock_transcript()
            with patch.object(
                orch._debate_protocol,
                "run",
                new=AsyncMock(return_value=mock_transcript),
            ):
                result = await orch.decide(topic="Test")

            assert isinstance(result, DebateResult)

    async def test_decide_publishes_debate_round_started_event(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            orch._state = make_state()
            orch._bus = EventBus()

            mock_transcript = make_mock_transcript()
            with patch.object(
                orch._debate_protocol,
                "run",
                new=AsyncMock(return_value=mock_transcript),
            ):
                await orch.decide(topic="Test decision")

            event_types = {e.type for e in orch._bus.history()}
            assert EventType.DEBATE_ROUND_STARTED in event_types

    async def test_decide_publishes_debate_completed_event(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            orch._state = make_state()
            orch._bus = EventBus()

            mock_transcript = make_mock_transcript()
            with patch.object(
                orch._debate_protocol,
                "run",
                new=AsyncMock(return_value=mock_transcript),
            ):
                await orch.decide(topic="Test decision")

            event_types = {e.type for e in orch._bus.history()}
            assert EventType.DEBATE_COMPLETED in event_types

    async def test_decide_completed_event_includes_winner(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            orch._state = make_state()
            orch._bus = EventBus()

            mock_transcript = make_mock_transcript(winner="user_advocate")
            with patch.object(
                orch._debate_protocol,
                "run",
                new=AsyncMock(return_value=mock_transcript),
            ):
                await orch.decide(topic="UX decision")

            completed_events = orch._bus.history(EventType.DEBATE_COMPLETED)
            assert len(completed_events) == 1
            assert completed_events[0].payload["winner"] == "user_advocate"

    async def test_decide_passes_options_to_protocol(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            orch._state = make_state()
            orch._bus = EventBus()

            mock_transcript = make_mock_transcript()
            with patch.object(
                orch._debate_protocol,
                "run",
                new=AsyncMock(return_value=mock_transcript),
            ) as mock_run:
                await orch.decide(
                    topic="Architecture",
                    options=["microservices", "monolith", "modular monolith"],
                )

            _, call_kwargs = mock_run.call_args
            assert call_kwargs["options"] == [
                "microservices",
                "monolith",
                "modular monolith",
            ]


# ---------------------------------------------------------------------------
# Orchestrator.standalone_debate() tests
# ---------------------------------------------------------------------------


class TestOrchestratorStandaloneDebate:
    async def test_standalone_debate_initializes_state(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            assert orch._state is None

            mock_transcript = make_mock_transcript()
            with patch.object(
                orch._debate_protocol,
                "run",
                new=AsyncMock(return_value=mock_transcript),
            ):
                await orch.standalone_debate(topic="standalone test")

            assert orch._state is not None
            assert orch._bus is not None

    async def test_standalone_debate_returns_debate_result(self) -> None:
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            mock_transcript = make_mock_transcript(winner="visionary")
            with patch.object(
                orch._debate_protocol,
                "run",
                new=AsyncMock(return_value=mock_transcript),
            ):
                result = await orch.standalone_debate(topic="standalone test")

            assert isinstance(result, DebateResult)
            assert result.winner == "visionary"

    async def test_standalone_debate_without_prior_run(self) -> None:
        """standalone_debate must work even without calling run() first."""
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockClient:
            MockClient.return_value = make_mock_client()
            from crucible.core.orchestrator import Orchestrator

            orch = Orchestrator(api_key="test-key")
            mock_transcript = make_mock_transcript()
            with patch.object(
                orch._debate_protocol,
                "run",
                new=AsyncMock(return_value=mock_transcript),
            ):
                # Must NOT raise RuntimeError about needing run() first
                result = await orch.standalone_debate(topic="no prior run")

            assert result is not None
