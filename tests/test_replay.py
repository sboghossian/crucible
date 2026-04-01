"""Tests for the debate replay and branching system."""

from __future__ import annotations

import json
from pathlib import Path
from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest

from crucible.memory.sqlite_store import SQLiteMemoryStore
from crucible.replay import DebateBrancher, DebatePlayer, DebateRecorder
from crucible.replay._serde import event_from_row, event_round, event_to_json
from crucible.streaming.events import (
    ArgumentSubmitted,
    CrossExamination,
    DebateStarted,
    PersonaThinking,
    ScoringComplete,
    ScoringStarted,
    WinnerDeclared,
)


# ------------------------------------------------------------------ #
# Fixtures                                                             #
# ------------------------------------------------------------------ #


@pytest.fixture
def tmp_store(tmp_path: Path) -> SQLiteMemoryStore:
    return SQLiteMemoryStore(db_path=tmp_path / "test.db")


def make_sample_events() -> list:
    """3-round debate fixture (2 personas for brevity)."""
    return [
        DebateStarted(topic="Test topic", context="ctx", options=["yes", "no"]),
        PersonaThinking(persona_name="pragmatist", round=1, round_label="Opening Statement"),
        ArgumentSubmitted(
            persona_name="pragmatist", round=1, round_label="Opening Statement",
            content="Pragmatist opening.",
        ),
        PersonaThinking(persona_name="visionary", round=1, round_label="Opening Statement"),
        ArgumentSubmitted(
            persona_name="visionary", round=1, round_label="Opening Statement",
            content="Visionary opening.",
        ),
        PersonaThinking(persona_name="pragmatist", round=2, round_label="Cross-Examination"),
        CrossExamination(
            persona_name="pragmatist", content="Pragma cross.", targets=["visionary"],
        ),
        PersonaThinking(persona_name="visionary", round=2, round_label="Cross-Examination"),
        CrossExamination(
            persona_name="visionary", content="Vision cross.", targets=["pragmatist"],
        ),
        PersonaThinking(persona_name="pragmatist", round=3, round_label="Closing Argument"),
        ArgumentSubmitted(
            persona_name="pragmatist", round=3, round_label="Closing Argument",
            content="Pragmatist closing.",
        ),
        PersonaThinking(persona_name="visionary", round=3, round_label="Closing Argument"),
        ArgumentSubmitted(
            persona_name="visionary", round=3, round_label="Closing Argument",
            content="Visionary closing.",
        ),
        ScoringStarted(),
        ScoringComplete(scores={"pragmatist": 7.5, "visionary": 6.0}),
        WinnerDeclared(
            winner="pragmatist", winner_score=7.5,
            decision="Pragmatist wins.", dissenting_views=[],
        ),
    ]


async def fake_stream(events: list) -> AsyncIterator:
    for event in events:
        yield event


def make_mock_client(text: str = "Mock response.") -> MagicMock:
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    client = MagicMock()
    client.messages = MagicMock()
    client.messages.create = AsyncMock(return_value=msg)
    return client


# ------------------------------------------------------------------ #
# _serde helpers                                                       #
# ------------------------------------------------------------------ #


def test_event_round_values():
    assert event_round(DebateStarted(topic="t")) == 0
    assert event_round(PersonaThinking(persona_name="p", round=1, round_label="L")) == 1
    assert event_round(CrossExamination(persona_name="p", content="c")) == 2
    assert event_round(ArgumentSubmitted(persona_name="p", round=3, round_label="L", content="c")) == 3
    assert event_round(ScoringStarted()) == 4
    assert event_round(ScoringComplete(scores={})) == 4
    assert event_round(WinnerDeclared(winner="p", winner_score=5.0, decision="d")) == 4


def test_event_serialization_roundtrip():
    original = ArgumentSubmitted(
        persona_name="pragmatist", round=1, round_label="Opening",
        content="Hello world.", targets=["visionary"],
    )
    row = {"event_kind": original.kind, "event_json": event_to_json(original)}
    restored = event_from_row(row)
    assert isinstance(restored, ArgumentSubmitted)
    assert restored.persona_name == "pragmatist"
    assert restored.content == "Hello world."
    assert restored.targets == ["visionary"]


def test_cross_examination_roundtrip():
    original = CrossExamination(persona_name="visionary", content="I challenge.", targets=["pragmatist"])
    row = {"event_kind": original.kind, "event_json": event_to_json(original)}
    restored = event_from_row(row)
    assert isinstance(restored, CrossExamination)
    assert restored.targets == ["pragmatist"]


# ------------------------------------------------------------------ #
# DebateRecorder                                                       #
# ------------------------------------------------------------------ #


async def test_recorder_creates_session(tmp_store: SQLiteMemoryStore):
    recorder = DebateRecorder(tmp_store)
    debate_id = recorder.new_session(
        topic="Test topic", context="ctx", options=["yes", "no"],
        personas=["pragmatist", "visionary"],
    )
    recorded = []
    async for event in recorder.record(debate_id, fake_stream(make_sample_events())):
        recorded.append(event)

    session = tmp_store.get_debate_session(debate_id)
    assert session is not None
    assert session["topic"] == "Test topic"
    assert session["context"] == "ctx"
    assert session["completed"] is True
    assert len(recorded) == len(make_sample_events())


async def test_recorder_captures_all_events(tmp_store: SQLiteMemoryStore):
    events = make_sample_events()
    recorder = DebateRecorder(tmp_store)
    debate_id = recorder.new_session(topic="T", context="", options=[], personas=[])
    async for _ in recorder.record(debate_id, fake_stream(events)):
        pass

    stored = tmp_store.get_debate_events(debate_id)
    assert len(stored) == len(events)


async def test_recorder_saves_correct_event_kinds(tmp_store: SQLiteMemoryStore):
    recorder = DebateRecorder(tmp_store)
    debate_id = recorder.new_session(topic="T", context="", options=[], personas=[])
    async for _ in recorder.record(debate_id, fake_stream(make_sample_events())):
        pass

    stored = tmp_store.get_debate_events(debate_id)
    kinds = [r["event_kind"] for r in stored]
    assert kinds[0] == "debate_started"
    assert "argument_submitted" in kinds
    assert "cross_examination" in kinds
    assert "scoring_complete" in kinds
    assert kinds[-1] == "winner_declared"


async def test_recorder_marks_total_events(tmp_store: SQLiteMemoryStore):
    events = make_sample_events()
    recorder = DebateRecorder(tmp_store)
    debate_id = recorder.new_session(topic="T", context="", options=[], personas=[])
    async for _ in recorder.record(debate_id, fake_stream(events)):
        pass

    session = tmp_store.get_debate_session(debate_id)
    assert session is not None
    assert session["total_events"] == len(events)


async def test_recorder_assigns_round_numbers(tmp_store: SQLiteMemoryStore):
    recorder = DebateRecorder(tmp_store)
    debate_id = recorder.new_session(topic="T", context="", options=[], personas=[])
    async for _ in recorder.record(debate_id, fake_stream(make_sample_events())):
        pass

    stored = tmp_store.get_debate_events(debate_id)
    rounds = {r["event_kind"]: r["round_number"] for r in stored}
    assert rounds["debate_started"] == 0
    assert rounds["scoring_started"] == 4
    assert rounds["winner_declared"] == 4


# ------------------------------------------------------------------ #
# DebatePlayer                                                         #
# ------------------------------------------------------------------ #


async def _record_all(tmp_store: SQLiteMemoryStore, events: list | None = None) -> str:
    ev = events or make_sample_events()
    recorder = DebateRecorder(tmp_store)
    debate_id = recorder.new_session(topic="T", context="", options=[], personas=[])
    async for _ in recorder.record(debate_id, fake_stream(ev)):
        pass
    return debate_id


async def test_player_replays_all_events(tmp_store: SQLiteMemoryStore):
    events = make_sample_events()
    debate_id = await _record_all(tmp_store, events)

    player = DebatePlayer(tmp_store)
    replayed = []
    async for event in player.replay(debate_id, speed=float("inf")):
        replayed.append(event)

    assert len(replayed) == len(events)
    assert replayed[0].kind == "debate_started"
    assert replayed[-1].kind == "winner_declared"


async def test_player_produces_same_kinds(tmp_store: SQLiteMemoryStore):
    events = make_sample_events()
    debate_id = await _record_all(tmp_store, events)

    player = DebatePlayer(tmp_store)
    replayed = []
    async for event in player.replay(debate_id, speed=float("inf")):
        replayed.append(event)

    assert [e.kind for e in events] == [e.kind for e in replayed]


async def test_player_replays_content(tmp_store: SQLiteMemoryStore):
    debate_id = await _record_all(tmp_store)

    player = DebatePlayer(tmp_store)
    replayed = []
    async for event in player.replay(debate_id, speed=float("inf")):
        replayed.append(event)

    arg = next(e for e in replayed if isinstance(e, ArgumentSubmitted) and e.round == 1)
    assert arg.persona_name == "pragmatist"
    assert "Pragmatist opening" in arg.content


async def test_player_replay_from_round(tmp_store: SQLiteMemoryStore):
    debate_id = await _record_all(tmp_store)

    player = DebatePlayer(tmp_store)
    replayed = []
    async for event in player.replay_from(debate_id, round_number=3, speed=float("inf")):
        replayed.append(event)

    # Must include DebateStarted (round 0) and round 3+ events, but NOT round 1 or 2 args
    kinds = {e.kind for e in replayed}
    assert "debate_started" in kinds
    assert "winner_declared" in kinds

    for e in replayed:
        r = getattr(e, "round", None)
        if r is not None:
            assert r >= 3, f"Unexpected round {r} for {e.kind}"


async def test_player_replay_from_round2_skips_round1(tmp_store: SQLiteMemoryStore):
    debate_id = await _record_all(tmp_store)

    player = DebatePlayer(tmp_store)
    replayed = []
    async for event in player.replay_from(debate_id, round_number=2, speed=float("inf")):
        replayed.append(event)

    # No round-1 ArgumentSubmitted
    round1_args = [
        e for e in replayed
        if isinstance(e, ArgumentSubmitted) and e.round == 1
    ]
    assert round1_args == []


# ------------------------------------------------------------------ #
# DebateBrancher                                                       #
# ------------------------------------------------------------------ #


async def test_brancher_creates_branch(tmp_store: SQLiteMemoryStore):
    debate_id = await _record_all(tmp_store)

    brancher = DebateBrancher(tmp_store)
    branch_id = brancher.branch(debate_id, round_number=2, new_personas=["pragmatist"])

    assert branch_id != debate_id
    session = tmp_store.get_debate_session(branch_id)
    assert session is not None
    assert session["parent_debate_id"] == debate_id
    assert session["branch_round"] == 2
    assert session["personas"] == ["pragmatist"]


async def test_brancher_inherits_topic_and_context(tmp_store: SQLiteMemoryStore):
    events = make_sample_events()
    recorder = DebateRecorder(tmp_store)
    debate_id = recorder.new_session(topic="Original topic", context="ctx", options=["yes"])
    async for _ in recorder.record(debate_id, fake_stream(events)):
        pass

    brancher = DebateBrancher(tmp_store)
    branch_id = brancher.branch(debate_id, round_number=1)

    branch = tmp_store.get_debate_session(branch_id)
    assert branch is not None
    assert branch["context"] == "ctx"
    assert branch["options"] == ["yes"]
    # topic unchanged when no new_prompt
    assert branch["topic"] == "Original topic"


async def test_brancher_overrides_topic_with_new_prompt(tmp_store: SQLiteMemoryStore):
    debate_id = await _record_all(tmp_store)

    brancher = DebateBrancher(tmp_store)
    branch_id = brancher.branch(debate_id, round_number=2, new_prompt="Reframed topic")

    branch = tmp_store.get_debate_session(branch_id)
    assert branch is not None
    assert branch["topic"] == "Reframed topic"
    assert branch["new_prompt"] == "Reframed topic"


async def test_brancher_copies_inherited_events(tmp_store: SQLiteMemoryStore):
    debate_id = await _record_all(tmp_store)

    brancher = DebateBrancher(tmp_store)
    branch_id = brancher.branch(debate_id, round_number=1)

    inherited = tmp_store.get_debate_events(branch_id)
    # Only rounds 0 and 1 should be inherited
    for row in inherited:
        assert row["round_number"] <= 1


async def test_brancher_branch_from_round2_inherits_rounds_0_1_2(tmp_store: SQLiteMemoryStore):
    debate_id = await _record_all(tmp_store)

    brancher = DebateBrancher(tmp_store)
    branch_id = brancher.branch(debate_id, round_number=2)

    inherited = tmp_store.get_debate_events(branch_id)
    rounds = {row["round_number"] for row in inherited}
    assert 0 in rounds
    assert 1 in rounds
    assert 2 in rounds
    assert 3 not in rounds
    assert 4 not in rounds


async def test_branch_tree_structure(tmp_store: SQLiteMemoryStore):
    debate_id = await _record_all(tmp_store)

    brancher = DebateBrancher(tmp_store)
    branch1_id = brancher.branch(debate_id, round_number=1)
    branch2_id = brancher.branch(debate_id, round_number=2)

    tree = brancher.get_branch_tree(debate_id)

    assert debate_id in tree
    child_ids = [c["id"] for c in tree[debate_id]]
    assert branch1_id in child_ids
    assert branch2_id in child_ids


async def test_branch_tree_nested(tmp_store: SQLiteMemoryStore):
    """A branch of a branch should appear in the tree."""
    debate_id = await _record_all(tmp_store)
    brancher = DebateBrancher(tmp_store)

    branch1_id = brancher.branch(debate_id, round_number=1)
    # branch1 only has rounds 0-1, so we can only branch at round <= 1
    branch2_id = brancher.branch(branch1_id, round_number=0)

    tree = brancher.get_branch_tree(debate_id)

    # Root's direct child is branch1
    assert branch1_id in [c["id"] for c in tree[debate_id]]
    # branch1's direct child is branch2
    assert branch1_id in tree
    assert branch2_id in [c["id"] for c in tree[branch1_id]]


async def test_run_branch_emits_inherited_then_new(tmp_store: SQLiteMemoryStore):
    """run_branch should re-emit inherited events then produce new closing events."""
    debate_id = await _record_all(tmp_store)

    brancher = DebateBrancher(tmp_store)
    branch_id = brancher.branch(debate_id, round_number=2, new_personas=["pragmatist"])

    # Mock client: score call returns JSON, statement call returns text
    call_count = 0

    async def _create(**kwargs: object) -> MagicMock:
        nonlocal call_count
        call_count += 1
        msg = MagicMock()
        max_tok = kwargs.get("max_tokens", 1024)
        if max_tok == 200:  # scoring
            msg.content = [MagicMock(
                text='{"evidence_quality": 7, "logical_consistency": 7, '
                     '"practical_feasibility": 7, "novelty": 7}'
            )]
        else:
            msg.content = [MagicMock(text="Closing argument: I recommend this.")]
        return msg

    client = MagicMock()
    client.messages = MagicMock()
    client.messages.create = AsyncMock(side_effect=_create)

    emitted = []
    async for event in brancher.run_branch(branch_id, client=client, model="claude-opus-4-6"):
        emitted.append(event)

    kinds = [e.kind for e in emitted]

    # Inherited: debate_started + rounds 1 & 2 events
    assert kinds[0] == "debate_started"
    # Must end with winner_declared
    assert kinds[-1] == "winner_declared"
    # Must have new closing arguments
    assert "argument_submitted" in kinds
    # Branch session should be marked complete
    session = tmp_store.get_debate_session(branch_id)
    assert session is not None
    assert session["completed"] is True


async def test_run_branch_records_new_events(tmp_store: SQLiteMemoryStore):
    """New events from run_branch should be persisted in the branch session."""
    debate_id = await _record_all(tmp_store)
    brancher = DebateBrancher(tmp_store)
    branch_id = brancher.branch(debate_id, round_number=2, new_personas=["pragmatist"])

    inherited_count = len(tmp_store.get_debate_events(branch_id))

    async def _create(**kwargs: object) -> MagicMock:
        msg = MagicMock()
        max_tok = kwargs.get("max_tokens", 1024)
        if max_tok == 200:
            msg.content = [MagicMock(
                text='{"evidence_quality": 6, "logical_consistency": 6, '
                     '"practical_feasibility": 6, "novelty": 6}'
            )]
        else:
            msg.content = [MagicMock(text="Closing argument: Done.")]
        return msg

    client = MagicMock()
    client.messages.create = AsyncMock(side_effect=_create)

    async for _ in brancher.run_branch(branch_id, client=client):
        pass

    all_events = tmp_store.get_debate_events(branch_id)
    assert len(all_events) > inherited_count
