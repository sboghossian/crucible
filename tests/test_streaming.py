"""Tests for the streaming debate module."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from crucible.streaming.events import (
    ArgumentSubmitted,
    CrossExamination,
    DebateStarted,
    PersonaThinking,
    ScoringComplete,
    ScoringStarted,
    WinnerDeclared,
)
from crucible.streaming.renderer import DebateRenderer
from crucible.streaming.stream import DebateStream


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_mock_client(response_text: str = "Mock argument content.") -> Any:
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=response_text)]
    mock_client = MagicMock()
    mock_client.messages = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_message)
    return mock_client


def make_mock_score_client() -> Any:
    """Client that returns valid JSON for scoring and text for arguments."""
    call_count = 0

    async def create_side_effect(**kwargs: Any) -> Any:
        nonlocal call_count
        call_count += 1
        mock_message = MagicMock()
        # Scoring calls use max_tokens=200 — return JSON
        if kwargs.get("max_tokens", 1024) <= 200:
            mock_message.content = [MagicMock(
                text='{"evidence_quality": 7, "logical_consistency": 8, "practical_feasibility": 6, "novelty": 5}'
            )]
        else:
            mock_message.content = [MagicMock(text=f"Mock statement #{call_count}.")]
        return mock_message

    mock_client = MagicMock()
    mock_client.messages = MagicMock()
    mock_client.messages.create = AsyncMock(side_effect=create_side_effect)
    return mock_client


# ---------------------------------------------------------------------------
# Event type tests
# ---------------------------------------------------------------------------


def test_event_kinds() -> None:
    assert DebateStarted().kind == "debate_started"
    assert PersonaThinking().kind == "persona_thinking"
    assert ArgumentSubmitted().kind == "argument_submitted"
    assert CrossExamination().kind == "cross_examination"
    assert ScoringStarted().kind == "scoring_started"
    assert ScoringComplete().kind == "scoring_complete"
    assert WinnerDeclared().kind == "winner_declared"


def test_debate_started_fields() -> None:
    ev = DebateStarted(topic="T", context="C", options=["A", "B"])
    assert ev.topic == "T"
    assert ev.context == "C"
    assert ev.options == ["A", "B"]


def test_argument_submitted_fields() -> None:
    ev = ArgumentSubmitted(
        persona_name="pragmatist",
        round=1,
        round_label="Opening Statement",
        content="My argument.",
        targets=[],
    )
    assert ev.persona_name == "pragmatist"
    assert ev.round == 1
    assert ev.content == "My argument."


def test_winner_declared_fields() -> None:
    ev = WinnerDeclared(
        winner="skeptic",
        winner_score=8.5,
        decision="Go with monolith.",
        dissenting_views=["visionary: disagrees"],
    )
    assert ev.winner == "skeptic"
    assert ev.winner_score == 8.5
    assert len(ev.dissenting_views) == 1


# ---------------------------------------------------------------------------
# Streaming order tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stream_yields_debate_started_first() -> None:
    client = make_mock_score_client()
    stream = DebateStream(client=client, model="claude-haiku-4-5-20251001", max_tokens=256)

    events = []
    async for event in stream.run(topic="Test topic", options=["A", "B"]):
        events.append(event)

    assert isinstance(events[0], DebateStarted)
    assert events[0].topic == "Test topic"
    assert events[0].options == ["A", "B"]


@pytest.mark.asyncio
async def test_stream_event_order() -> None:
    client = make_mock_score_client()
    stream = DebateStream(client=client, model="claude-haiku-4-5-20251001", max_tokens=256)

    events = []
    async for event in stream.run(topic="Monolith vs microservices"):
        events.append(event)

    kinds = [e.kind for e in events]

    # Must start with debate_started
    assert kinds[0] == "debate_started"

    # Must end with winner_declared
    assert kinds[-1] == "winner_declared"

    # scoring_started must come before scoring_complete
    assert kinds.index("scoring_started") < kinds.index("scoring_complete")

    # scoring_complete must come before winner_declared
    assert kinds.index("scoring_complete") < kinds.index("winner_declared")

    # Each PersonaThinking must immediately precede an argument or cross_examination
    for i, kind in enumerate(kinds):
        if kind == "persona_thinking":
            assert i + 1 < len(kinds)
            assert kinds[i + 1] in ("argument_submitted", "cross_examination")


@pytest.mark.asyncio
async def test_stream_yields_all_four_personas_per_round() -> None:
    client = make_mock_score_client()
    stream = DebateStream(client=client, model="claude-haiku-4-5-20251001", max_tokens=256)

    events = []
    async for event in stream.run(topic="Test"):
        events.append(event)

    thinking_events = [e for e in events if isinstance(e, PersonaThinking)]
    # 4 personas × 3 rounds = 12
    assert len(thinking_events) == 12

    # Each round should have all 4 personas
    for round_num in [1, 2, 3]:
        round_personas = {e.persona_name for e in thinking_events if e.round == round_num}
        assert round_personas == {"pragmatist", "visionary", "skeptic", "user_advocate"}


@pytest.mark.asyncio
async def test_stream_cross_examination_round() -> None:
    client = make_mock_score_client()
    stream = DebateStream(client=client, model="claude-haiku-4-5-20251001", max_tokens=256)

    events = []
    async for event in stream.run(topic="Test"):
        events.append(event)

    cross_events = [e for e in events if isinstance(e, CrossExamination)]
    assert len(cross_events) == 4  # one per persona


@pytest.mark.asyncio
async def test_stream_scoring_complete_has_scores() -> None:
    client = make_mock_score_client()
    stream = DebateStream(client=client, model="claude-haiku-4-5-20251001", max_tokens=256)

    events = []
    async for event in stream.run(topic="Test"):
        events.append(event)

    scoring_events = [e for e in events if isinstance(e, ScoringComplete)]
    assert len(scoring_events) == 1
    scores = scoring_events[0].scores
    assert set(scores.keys()) == {"pragmatist", "visionary", "skeptic", "user_advocate"}
    for score in scores.values():
        assert 0 <= score <= 10


@pytest.mark.asyncio
async def test_stream_winner_declared() -> None:
    client = make_mock_score_client()
    stream = DebateStream(client=client, model="claude-haiku-4-5-20251001", max_tokens=256)

    events = []
    async for event in stream.run(topic="Test"):
        events.append(event)

    winner_events = [e for e in events if isinstance(e, WinnerDeclared)]
    assert len(winner_events) == 1
    winner = winner_events[0]
    assert winner.winner in {"pragmatist", "visionary", "skeptic", "user_advocate"}
    assert 0 <= winner.winner_score <= 10


# ---------------------------------------------------------------------------
# Renderer tests
# ---------------------------------------------------------------------------


def make_null_console() -> Any:
    """Console that discards all output."""
    from rich.console import Console
    import io
    return Console(file=io.StringIO(), highlight=False)


def test_renderer_handles_debate_started() -> None:
    renderer = DebateRenderer(console=make_null_console())
    renderer.render(DebateStarted(topic="T", context="C", options=["A"]))


def test_renderer_handles_persona_thinking() -> None:
    renderer = DebateRenderer(console=make_null_console())
    renderer.render(PersonaThinking(persona_name="pragmatist", round=1, round_label="Opening Statement"))


def test_renderer_handles_argument_submitted() -> None:
    renderer = DebateRenderer(console=make_null_console())
    renderer.render(ArgumentSubmitted(
        persona_name="visionary",
        round=1,
        round_label="Opening Statement",
        content="The future is bright.",
        targets=[],
    ))


def test_renderer_handles_cross_examination() -> None:
    renderer = DebateRenderer(console=make_null_console())
    renderer.render(CrossExamination(
        persona_name="skeptic",
        content="Cross-examination: You are wrong.",
        targets=["pragmatist"],
    ))


def test_renderer_handles_scoring_started() -> None:
    renderer = DebateRenderer(console=make_null_console())
    renderer.render(ScoringStarted())


def test_renderer_handles_scoring_complete() -> None:
    renderer = DebateRenderer(console=make_null_console())
    renderer.render(ScoringComplete(scores={
        "pragmatist": 7.5,
        "visionary": 6.0,
        "skeptic": 8.0,
        "user_advocate": 5.5,
    }))


def test_renderer_handles_winner_declared() -> None:
    renderer = DebateRenderer(console=make_null_console())
    renderer.render(WinnerDeclared(
        winner="skeptic",
        winner_score=8.0,
        decision="[skeptic wins with score 8.0/10]\n\nGo with monolith.",
        dissenting_views=["pragmatist: agrees partially"],
    ))


def test_renderer_handles_all_event_types() -> None:
    """Smoke test: renderer must handle every DebateEvent subtype without raising."""
    renderer = DebateRenderer(console=make_null_console())
    all_events = [
        DebateStarted(topic="T", options=["A", "B"]),
        PersonaThinking(persona_name="pragmatist", round=1, round_label="Opening Statement"),
        ArgumentSubmitted(persona_name="pragmatist", round=1, round_label="Opening Statement", content="x"),
        PersonaThinking(persona_name="skeptic", round=2, round_label="Cross-Examination"),
        CrossExamination(persona_name="skeptic", content="x", targets=["pragmatist"]),
        PersonaThinking(persona_name="visionary", round=3, round_label="Closing Argument"),
        ArgumentSubmitted(persona_name="visionary", round=3, round_label="Closing Argument", content="x"),
        ScoringStarted(),
        ScoringComplete(scores={"pragmatist": 7.0, "visionary": 6.0, "skeptic": 8.0, "user_advocate": 5.0}),
        WinnerDeclared(winner="skeptic", winner_score=8.0, decision="Monolith wins.", dissenting_views=[]),
    ]
    for event in all_events:
        renderer.render(event)  # must not raise
