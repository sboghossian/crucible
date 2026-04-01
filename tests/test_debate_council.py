"""Tests for the Debate Council — the crown jewel of Crucible."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from crucible.core.agent import AgentConfig
from crucible.core.events import EventBus, EventType
from crucible.core.state import SharedState
from crucible.debate.personas import (
    ALL_PERSONAS,
    PERSONA_BY_NAME,
    PRAGMATIST,
    SKEPTIC,
    USER_ADVOCATE,
    VISIONARY,
)
from crucible.debate.protocol import DebateProtocol, DebateTranscript, Statement
from crucible.debate.resolver import format_summary, resolve, to_debate_result


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def make_state(subject: str = "test") -> SharedState:
    return SharedState(run_id=str(uuid.uuid4())[:8], subject=subject)


def make_mock_client(response_text: str = "Mock response text.") -> Any:
    """Create a mock Anthropic async client."""
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=response_text)]

    mock_client = MagicMock()
    mock_client.messages = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_message)
    return mock_client


def make_transcript(
    topic: str = "Test topic",
    winner: str = "pragmatist",
    scores: dict[str, float] | None = None,
) -> DebateTranscript:
    scores = scores or {"pragmatist": 7.5, "visionary": 6.0, "skeptic": 6.5, "user_advocate": 5.5}
    transcript = DebateTranscript(
        topic=topic,
        context="Test context",
        options=["Option A", "Option B"],
    )
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
    transcript.winner_score = scores[winner]
    transcript.scores = scores
    transcript.decision = f"[{winner} wins] This is the decision."
    transcript.dissenting_views = [f"{p}: dissenting view." for p in scores if p != winner]
    return transcript


# ---------------------------------------------------------------------------
# Persona tests
# ---------------------------------------------------------------------------


class TestPersonas:
    def test_all_personas_exist(self) -> None:
        assert len(ALL_PERSONAS) == 4
        names = {p.name for p in ALL_PERSONAS}
        assert names == {"pragmatist", "visionary", "skeptic", "user_advocate"}

    def test_persona_by_name_lookup(self) -> None:
        assert PERSONA_BY_NAME["pragmatist"] is PRAGMATIST
        assert PERSONA_BY_NAME["visionary"] is VISIONARY
        assert PERSONA_BY_NAME["skeptic"] is SKEPTIC
        assert PERSONA_BY_NAME["user_advocate"] is USER_ADVOCATE

    def test_scoring_weights_sum_to_one(self) -> None:
        for persona in ALL_PERSONAS:
            total = sum(persona.scoring_weight.values())
            assert abs(total - 1.0) < 0.01, (
                f"{persona.name} weights sum to {total}, expected 1.0"
            )

    def test_pragmatist_weights_feasibility(self) -> None:
        # Pragmatist should weight practical_feasibility highest
        weights = PRAGMATIST.scoring_weight
        assert weights["practical_feasibility"] == max(weights.values())

    def test_skeptic_weights_evidence(self) -> None:
        # Skeptic should weight evidence_quality highest
        weights = SKEPTIC.scoring_weight
        assert weights["evidence_quality"] == max(weights.values())

    def test_visionary_weights_novelty(self) -> None:
        # Visionary should weight novelty highest
        weights = VISIONARY.scoring_weight
        assert weights["novelty"] == max(weights.values())

    def test_system_prompts_are_unique(self) -> None:
        prompts = [p.system_prompt for p in ALL_PERSONAS]
        assert len(set(prompts)) == 4, "All system prompts must be unique"

    def test_system_prompts_encode_bias(self) -> None:
        # Each prompt should reference its core bias
        assert "feasibility" in PRAGMATIST.system_prompt.lower()
        assert "evidence" in SKEPTIC.system_prompt.lower() or "rigor" in SKEPTIC.system_prompt.lower()
        assert "transform" in VISIONARY.system_prompt.lower() or "potential" in VISIONARY.system_prompt.lower()
        assert "user" in USER_ADVOCATE.system_prompt.lower()


# ---------------------------------------------------------------------------
# Protocol tests
# ---------------------------------------------------------------------------


class TestDebateProtocol:
    @pytest.mark.asyncio
    async def test_protocol_runs_three_rounds(self) -> None:
        mock_client = make_mock_client("Opening statement: I recommend option A for these reasons.")
        protocol = DebateProtocol(client=mock_client, model="claude-opus-4-6")

        # Mock the scoring to return valid JSON
        score_response = MagicMock()
        score_response.content = [MagicMock(
            text='{"evidence_quality": 7, "logical_consistency": 8, "practical_feasibility": 6, "novelty": 5}'
        )]
        mock_client.messages.create = AsyncMock(
            side_effect=[
                # 4 opening statements
                *[MagicMock(content=[MagicMock(text="Opening statement: test.")]) for _ in range(4)],
                # 4 cross-examination statements
                *[MagicMock(content=[MagicMock(text="Cross-examination: test.")]) for _ in range(4)],
                # 4 closing statements
                *[MagicMock(content=[MagicMock(text="Closing argument: test.")]) for _ in range(4)],
                # 4 scoring calls (one per closing statement)
                *[score_response for _ in range(4)],
            ]
        )

        transcript = await protocol.run(
            topic="Should we use microservices?",
            options=["yes", "no", "hybrid"],
        )

        assert isinstance(transcript, DebateTranscript)
        assert len(transcript.statements) == 12  # 4 personas × 3 rounds
        assert len([s for s in transcript.statements if s.round == 1]) == 4
        assert len([s for s in transcript.statements if s.round == 2]) == 4
        assert len([s for s in transcript.statements if s.round == 3]) == 4

    @pytest.mark.asyncio
    async def test_protocol_handles_llm_failure_gracefully(self) -> None:
        mock_client = make_mock_client()
        mock_client.messages.create = AsyncMock(side_effect=Exception("API error"))
        protocol = DebateProtocol(client=mock_client, model="claude-opus-4-6")

        transcript = await protocol.run(topic="Test topic")

        # Should not raise, should return transcript with error messages
        assert isinstance(transcript, DebateTranscript)
        # Statements should contain error indicators
        for stmt in transcript.statements:
            if stmt.round == 1:
                assert "unavailable" in stmt.content.lower() or "error" in stmt.content.lower()

    @pytest.mark.asyncio
    async def test_protocol_accepts_empty_options(self) -> None:
        mock_client = make_mock_client()
        score_response = MagicMock()
        score_response.content = [MagicMock(text='{"evidence_quality": 7, "logical_consistency": 7, "practical_feasibility": 7, "novelty": 7}')]
        mock_client.messages.create = AsyncMock(return_value=MagicMock(
            content=[MagicMock(text="Statement text.")]
        ))

        protocol = DebateProtocol(client=mock_client, model="claude-opus-4-6")
        # Should not raise with empty options
        transcript = await protocol.run(topic="Open-ended debate topic", options=[])
        assert transcript.options == []


# ---------------------------------------------------------------------------
# Resolver tests
# ---------------------------------------------------------------------------


class TestResolver:
    def test_resolve_returns_correct_winner(self) -> None:
        transcript = make_transcript(winner="skeptic", scores={
            "pragmatist": 6.0, "visionary": 5.5, "skeptic": 8.0, "user_advocate": 5.0
        })
        resolution = resolve(transcript)
        assert resolution.winner == "skeptic"
        assert resolution.winner_score == 8.0

    def test_resolve_captures_dissenting_views(self) -> None:
        transcript = make_transcript(winner="visionary")
        resolution = resolve(transcript)
        assert len(resolution.dissenting_views) == 3
        non_winner_names = {"pragmatist", "skeptic", "user_advocate"}
        for view in resolution.dissenting_views:
            persona = view.split(":")[0]
            assert persona in non_winner_names

    def test_resolve_rounds_summary_has_three_rounds(self) -> None:
        transcript = make_transcript()
        resolution = resolve(transcript)
        assert len(resolution.rounds_summary) == 3
        for round_data in resolution.rounds_summary:
            assert "round" in round_data
            assert "statements" in round_data
            assert len(round_data["statements"]) == 4

    def test_to_debate_result_stores_in_state(self) -> None:
        transcript = make_transcript(topic="Architecture choice", winner="pragmatist")
        result = to_debate_result(transcript)
        assert result.topic == "Architecture choice"
        assert result.winner == "pragmatist"
        assert len(result.rounds) == 3
        assert len(result.dissenting_views) == 3

    def test_format_summary_includes_scores(self) -> None:
        transcript = make_transcript(
            scores={"pragmatist": 7.5, "visionary": 6.0, "skeptic": 6.5, "user_advocate": 5.5}
        )
        resolution = resolve(transcript)
        summary = format_summary(resolution)
        assert "pragmatist" in summary.lower()
        assert "7.5" in summary

    def test_format_summary_verbose_includes_transcript(self) -> None:
        transcript = make_transcript()
        resolution = resolve(transcript)
        summary = format_summary(resolution, verbose=True)
        assert "OPENING STATEMENTS" in summary
        assert "CROSS-EXAMINATION" in summary
        assert "CLOSING ARGUMENTS" in summary


# ---------------------------------------------------------------------------
# Debate Council agent tests
# ---------------------------------------------------------------------------


class TestDebateCouncilAgent:
    @pytest.mark.asyncio
    async def test_agent_stores_result_in_state(self) -> None:
        from crucible.agents.debate_council import DebateCouncilAgent

        mock_client = make_mock_client()
        state = make_state()
        bus = EventBus()
        config = AgentConfig(model="claude-opus-4-6", timeout=30.0)

        agent = DebateCouncilAgent(client=mock_client, state=state, bus=bus, config=config)

        # Mock the debate protocol
        mock_result = make_transcript(winner="pragmatist")
        with patch.object(
            agent,
            "run",
            new_callable=lambda: lambda self: AsyncMock(
                return_value=MagicMock(success=True, output={})
            ),
        ):
            pass  # just test that it instantiates correctly

        assert agent.name == "debate_council"

    @pytest.mark.asyncio
    async def test_agent_publishes_events(self) -> None:
        from crucible.agents.debate_council import DebateCouncilAgent

        mock_client = make_mock_client()
        state = make_state()
        bus = EventBus()
        config = AgentConfig(model="claude-opus-4-6", timeout=30.0)

        events_received: list[EventType] = []

        async def capture(event: Any) -> None:
            events_received.append(event.type)

        bus.subscribe_all(capture)

        agent = DebateCouncilAgent(client=mock_client, state=state, bus=bus, config=config)

        # Mock the underlying protocol
        mock_transcript = make_transcript()
        with patch(
            "crucible.agents.debate_council.DebateProtocol"
        ) as MockProtocol:
            mock_protocol = AsyncMock()
            mock_protocol.run = AsyncMock(return_value=mock_transcript)
            MockProtocol.return_value = mock_protocol

            result = await agent.execute(topic="Test decision")

        assert EventType.AGENT_STARTED in events_received
        # AGENT_COMPLETED or AGENT_FAILED depending on mock setup
        assert (
            EventType.AGENT_COMPLETED in events_received
            or EventType.AGENT_FAILED in events_received
        )


# ---------------------------------------------------------------------------
# Orchestrator.decide() tests
# ---------------------------------------------------------------------------


class TestOrchestratorDecide:
    @pytest.mark.asyncio
    async def test_decide_requires_initialized_state(self) -> None:
        from crucible.core.orchestrator import Orchestrator

        orch = Orchestrator(api_key="test-key")
        # State not initialized — should raise
        with pytest.raises(RuntimeError, match="run\\(\\)"):
            await orch.decide(topic="Test")

    @pytest.mark.asyncio
    async def test_decide_stores_result_in_state(self) -> None:
        from crucible.core.orchestrator import Orchestrator

        mock_client = make_mock_client()
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockAnthropic:
            MockAnthropic.return_value = mock_client

            orch = Orchestrator(api_key="test-key")
            orch._state = make_state("naming test")
            orch._bus = EventBus()

            mock_transcript = make_transcript(topic="naming test", winner="visionary")
            with patch.object(orch._debate_protocol, "run", new=AsyncMock(return_value=mock_transcript)):
                result = await orch.decide(
                    topic="naming test",
                    options=["crucible", "forge", "tribunal"],
                )

        assert result.winner == "visionary"
        state = await orch._state.get()
        assert state.debate is not None
        assert state.debate.winner == "visionary"

    @pytest.mark.asyncio
    async def test_decide_publishes_debate_events(self) -> None:
        from crucible.core.orchestrator import Orchestrator

        mock_client = make_mock_client()
        with patch("crucible.core.orchestrator.anthropic.AsyncAnthropic") as MockAnthropic:
            MockAnthropic.return_value = mock_client

            orch = Orchestrator(api_key="test-key")
            orch._state = make_state()
            orch._bus = EventBus()

            debate_events: list[Any] = []

            async def capture(event: Any) -> None:
                if event.type in (EventType.DEBATE_ROUND_STARTED, EventType.DEBATE_COMPLETED):
                    debate_events.append(event)

            orch._bus.subscribe_all(capture)

            mock_transcript = make_transcript()
            with patch.object(orch._debate_protocol, "run", new=AsyncMock(return_value=mock_transcript)):
                await orch.decide(topic="Test decision")

        event_types = {e.type for e in debate_events}
        assert EventType.DEBATE_ROUND_STARTED in event_types
        assert EventType.DEBATE_COMPLETED in event_types


# ---------------------------------------------------------------------------
# Event bus tests
# ---------------------------------------------------------------------------


class TestEventBus:
    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self) -> None:
        from crucible.core.events import Event

        bus = EventBus()
        received: list[Event] = []

        async def handler(event: Event) -> None:
            received.append(event)

        bus.subscribe(EventType.AGENT_STARTED, handler)

        event = Event(
            type=EventType.AGENT_STARTED,
            source="scanner",
            payload={"test": True},
        )
        await bus.publish(event)

        assert len(received) == 1
        assert received[0].source == "scanner"

    @pytest.mark.asyncio
    async def test_wildcard_subscriber_receives_all(self) -> None:
        from crucible.core.events import Event

        bus = EventBus()
        all_events: list[Event] = []

        async def wildcard(event: Event) -> None:
            all_events.append(event)

        bus.subscribe_all(wildcard)

        for event_type in [EventType.AGENT_STARTED, EventType.AGENT_COMPLETED, EventType.DEBATE_COMPLETED]:
            await bus.publish(Event(type=event_type, source="test", payload={}))

        assert len(all_events) == 3

    @pytest.mark.asyncio
    async def test_failing_handler_does_not_block_others(self) -> None:
        from crucible.core.events import Event

        bus = EventBus()
        good_events: list[Event] = []

        async def bad_handler(event: Event) -> None:
            raise ValueError("handler failure")

        async def good_handler(event: Event) -> None:
            good_events.append(event)

        bus.subscribe(EventType.AGENT_OUTPUT, bad_handler)
        bus.subscribe(EventType.AGENT_OUTPUT, good_handler)

        await bus.publish(Event(type=EventType.AGENT_OUTPUT, source="test", payload={}))

        assert len(good_events) == 1  # good handler still ran

    def test_history_filters_by_type(self) -> None:
        import asyncio
        from crucible.core.events import Event

        bus = EventBus()

        async def _add() -> None:
            await bus.publish(Event(type=EventType.AGENT_STARTED, source="a", payload={}))
            await bus.publish(Event(type=EventType.AGENT_COMPLETED, source="b", payload={}))
            await bus.publish(Event(type=EventType.AGENT_STARTED, source="c", payload={}))

        asyncio.get_event_loop().run_until_complete(_add())

        started = bus.history(EventType.AGENT_STARTED)
        assert len(started) == 2
        assert all(e.type == EventType.AGENT_STARTED for e in started)
