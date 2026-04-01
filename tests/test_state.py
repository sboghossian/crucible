"""Tests for SharedState — typed access, concurrent updates, and persistence."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime

import pytest

from crucible.core.state import (
    DebateResult,
    ForecastResult,
    LearningRecord,
    PatternResult,
    ResearchResult,
    RunState,
    ScanResult,
    SharedState,
)


def make_state(subject: str = "test") -> SharedState:
    return SharedState(run_id=str(uuid.uuid4())[:8], subject=subject)


# ---------------------------------------------------------------------------
# RunState model tests
# ---------------------------------------------------------------------------


class TestRunState:
    def test_initial_status_is_running(self) -> None:
        state = RunState(run_id="abc", subject="test")
        assert state.status == "running"

    def test_initial_typed_fields_are_none(self) -> None:
        state = RunState(run_id="abc")
        assert state.scan is None
        assert state.research is None
        assert state.patterns is None
        assert state.debate is None
        assert state.forecast is None

    def test_initial_list_fields_are_empty(self) -> None:
        state = RunState(run_id="abc")
        assert state.learning_records == []
        assert state.visualizations == []
        assert state.errors == []

    def test_run_id_stored(self) -> None:
        state = RunState(run_id="xyz123")
        assert state.run_id == "xyz123"

    def test_subject_stored(self) -> None:
        state = RunState(run_id="abc", subject="multi-agent frameworks")
        assert state.subject == "multi-agent frameworks"

    def test_started_at_is_datetime(self) -> None:
        before = datetime.utcnow()
        state = RunState(run_id="abc")
        after = datetime.utcnow()
        assert before <= state.started_at <= after

    def test_finished_at_initially_none(self) -> None:
        state = RunState(run_id="abc")
        assert state.finished_at is None

    def test_scan_result_model(self) -> None:
        scan = ScanResult(repo_path="/tmp/test", file_count=100, total_lines=5000)
        assert scan.file_count == 100
        assert scan.total_lines == 5000
        assert scan.languages == {}
        assert scan.dependencies == []

    def test_debate_result_model(self) -> None:
        debate = DebateResult(
            topic="architecture choice",
            winner="pragmatist",
            winner_score=7.5,
        )
        assert debate.winner == "pragmatist"
        assert debate.winner_score == 7.5
        assert debate.rounds == []
        assert debate.scores == {}

    def test_forecast_result_model(self) -> None:
        forecast = ForecastResult(horizon="12 months", confidence=0.72)
        assert forecast.horizon == "12 months"
        assert forecast.confidence == 0.72
        assert forecast.predictions == []
        assert forecast.key_risks == []

    def test_learning_record_model(self) -> None:
        record = LearningRecord(
            agent_name="scanner",
            observation="Python codebase with 3 modules",
            pattern="success",
        )
        assert record.agent_name == "scanner"
        assert record.pattern == "success"
        assert isinstance(record.timestamp, datetime)


# ---------------------------------------------------------------------------
# SharedState access tests
# ---------------------------------------------------------------------------


class TestSharedStateGet:
    async def test_get_returns_run_state(self) -> None:
        shared = make_state("research topic")
        state = await shared.get()
        assert isinstance(state, RunState)
        assert state.subject == "research topic"

    async def test_get_returns_deep_copy(self) -> None:
        shared = make_state()
        state1 = await shared.get()
        state1.status = "mutated"
        state2 = await shared.get()
        # Internal state must be unchanged
        assert state2.status == "running"

    async def test_get_deep_copy_of_list_fields(self) -> None:
        shared = make_state()
        state1 = await shared.get()
        state1.errors.append({"agent": "test", "error": "bogus"})
        state2 = await shared.get()
        assert len(state2.errors) == 0


# ---------------------------------------------------------------------------
# SharedState update tests
# ---------------------------------------------------------------------------


class TestSharedStateUpdate:
    async def test_update_status_field(self) -> None:
        shared = make_state()
        await shared.update(status="complete")
        state = await shared.get()
        assert state.status == "complete"

    async def test_update_subject_field(self) -> None:
        shared = make_state()
        await shared.update(subject="new subject")
        state = await shared.get()
        assert state.subject == "new subject"

    async def test_update_finished_at(self) -> None:
        shared = make_state()
        now = datetime(2026, 4, 1, 12, 0, 0)
        await shared.update(finished_at=now, status="complete")
        state = await shared.get()
        assert state.finished_at == now
        assert state.status == "complete"

    async def test_update_unknown_field_raises_key_error(self) -> None:
        shared = make_state()
        with pytest.raises(KeyError, match="nonexistent_field"):
            await shared.update(nonexistent_field="value")

    async def test_update_does_not_affect_other_fields(self) -> None:
        shared = make_state("original subject")
        await shared.update(status="complete")
        state = await shared.get()
        assert state.subject == "original subject"


# ---------------------------------------------------------------------------
# SharedState set_typed tests
# ---------------------------------------------------------------------------


class TestSharedStateSetTyped:
    async def test_set_typed_stores_scan_result(self) -> None:
        shared = make_state()
        scan = ScanResult(repo_path="/tmp/repo", file_count=42, total_lines=1000)
        await shared.set_typed("scan", scan)
        state = await shared.get()
        assert state.scan is not None
        assert state.scan.file_count == 42
        assert state.scan.total_lines == 1000

    async def test_set_typed_stores_debate_result(self) -> None:
        shared = make_state()
        debate = DebateResult(
            topic="naming",
            winner="visionary",
            winner_score=8.0,
            scores={"visionary": 8.0, "pragmatist": 6.5},
        )
        await shared.set_typed("debate", debate)
        state = await shared.get()
        assert state.debate is not None
        assert state.debate.winner == "visionary"

    async def test_set_typed_stores_research_result(self) -> None:
        shared = make_state()
        research = ResearchResult(
            query="multi-agent AI",
            findings=["finding 1", "finding 2"],
            synthesis="Key synthesis.",
        )
        await shared.set_typed("research", research)
        state = await shared.get()
        assert state.research is not None
        assert len(state.research.findings) == 2

    async def test_set_typed_stores_pattern_result(self) -> None:
        shared = make_state()
        patterns = PatternResult(
            patterns=[{"name": "Event Bus", "description": "agents communicate via events"}],
            recommendations=["Use async patterns"],
        )
        await shared.set_typed("patterns", patterns)
        state = await shared.get()
        assert state.patterns is not None
        assert len(state.patterns.patterns) == 1

    async def test_set_typed_unknown_field_raises_key_error(self) -> None:
        shared = make_state()
        with pytest.raises(KeyError, match="unknown_field"):
            await shared.set_typed("unknown_field", ScanResult(repo_path="/tmp"))

    async def test_set_typed_overwrites_previous_value(self) -> None:
        shared = make_state()
        scan1 = ScanResult(repo_path="/tmp/repo1", file_count=10)
        scan2 = ScanResult(repo_path="/tmp/repo2", file_count=99)
        await shared.set_typed("scan", scan1)
        await shared.set_typed("scan", scan2)
        state = await shared.get()
        assert state.scan is not None
        assert state.scan.file_count == 99


# ---------------------------------------------------------------------------
# SharedState append tests
# ---------------------------------------------------------------------------


class TestSharedStateAppend:
    async def test_append_error_records_agent_and_message(self) -> None:
        shared = make_state()
        await shared.append_error("scanner", "File not found: /missing/path")
        state = await shared.get()
        assert len(state.errors) == 1
        assert state.errors[0]["agent"] == "scanner"
        assert state.errors[0]["error"] == "File not found: /missing/path"

    async def test_append_error_includes_timestamp(self) -> None:
        shared = make_state()
        await shared.append_error("test_agent", "test error")
        state = await shared.get()
        assert "timestamp" in state.errors[0]
        # Timestamp should be a parseable ISO string
        datetime.fromisoformat(state.errors[0]["timestamp"])

    async def test_append_multiple_errors_cumulative(self) -> None:
        shared = make_state()
        await shared.append_error("agent_a", "error 1")
        await shared.append_error("agent_b", "error 2")
        await shared.append_error("agent_c", "error 3")
        state = await shared.get()
        assert len(state.errors) == 3
        agents = [e["agent"] for e in state.errors]
        assert "agent_a" in agents
        assert "agent_c" in agents

    async def test_append_learning_record(self) -> None:
        shared = make_state()
        record = LearningRecord(
            agent_name="scanner",
            observation="Python codebase detected",
            pattern="success",
        )
        await shared.append_learning(record)
        state = await shared.get()
        assert len(state.learning_records) == 1
        assert state.learning_records[0].agent_name == "scanner"
        assert state.learning_records[0].observation == "Python codebase detected"

    async def test_append_learning_multiple_records(self) -> None:
        shared = make_state()
        for i in range(5):
            record = LearningRecord(
                agent_name=f"agent_{i}",
                observation=f"observation {i}",
            )
            await shared.append_learning(record)
        state = await shared.get()
        assert len(state.learning_records) == 5


# ---------------------------------------------------------------------------
# SharedState snapshot tests
# ---------------------------------------------------------------------------


class TestSharedStateSnapshot:
    async def test_snapshot_returns_dict(self) -> None:
        shared = make_state("snapshot test")
        snap = await shared.snapshot()
        assert isinstance(snap, dict)

    async def test_snapshot_contains_subject(self) -> None:
        shared = make_state("my subject")
        snap = await shared.snapshot()
        assert snap["subject"] == "my subject"

    async def test_snapshot_contains_status(self) -> None:
        shared = make_state()
        snap = await shared.snapshot()
        assert snap["status"] == "running"

    async def test_snapshot_null_for_unset_typed_fields(self) -> None:
        shared = make_state()
        snap = await shared.snapshot()
        assert snap["scan"] is None
        assert snap["debate"] is None
        assert snap["research"] is None

    async def test_snapshot_includes_typed_fields_when_set(self) -> None:
        shared = make_state()
        scan = ScanResult(repo_path="/tmp/test", file_count=7)
        await shared.set_typed("scan", scan)
        snap = await shared.snapshot()
        assert snap["scan"] is not None
        assert snap["scan"]["file_count"] == 7

    async def test_snapshot_is_json_serializable(self) -> None:
        import json

        shared = make_state("json test")
        debate = DebateResult(topic="test", winner="pragmatist", winner_score=7.0)
        await shared.set_typed("debate", debate)
        snap = await shared.snapshot()
        # Should not raise
        serialized = json.dumps(snap, default=str)
        assert "pragmatist" in serialized


# ---------------------------------------------------------------------------
# Concurrency tests
# ---------------------------------------------------------------------------


class TestSharedStateConcurrency:
    async def test_concurrent_updates_are_safe(self) -> None:
        shared = make_state()

        async def add_record(i: int) -> None:
            record = LearningRecord(
                agent_name=f"agent_{i}",
                observation=f"obs-{i}",
            )
            await shared.append_learning(record)

        await asyncio.gather(*[add_record(i) for i in range(20)])
        state = await shared.get()
        assert len(state.learning_records) == 20

    async def test_concurrent_error_appends_are_safe(self) -> None:
        shared = make_state()

        async def add_error(i: int) -> None:
            await shared.append_error(f"agent_{i}", f"error_{i}")

        await asyncio.gather(*[add_error(i) for i in range(15)])
        state = await shared.get()
        assert len(state.errors) == 15

    async def test_concurrent_set_typed_last_write_wins(self) -> None:
        shared = make_state()

        async def set_scan(file_count: int) -> None:
            scan = ScanResult(repo_path="/tmp", file_count=file_count)
            await shared.set_typed("scan", scan)

        await asyncio.gather(*[set_scan(i) for i in range(10)])
        state = await shared.get()
        # One of the writes must have won — scan should not be None
        assert state.scan is not None
        assert state.scan.file_count in range(10)
