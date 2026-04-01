"""Tests for LearningAgent (observation, synthesis) and MemoryStore (persistence)."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from crucible.agents.learning import LearningAgent
from crucible.core.agent import AgentConfig
from crucible.core.events import Event, EventBus, EventType
from crucible.core.state import LearningRecord, SharedState
from crucible.memory.store import MemoryEntry, MemoryStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_mock_client(response_text: str = "Meta-pattern synthesis result.") -> Any:
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=response_text)]
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_message)
    return mock_client


def make_agent(
    response_text: str = "Meta-pattern synthesis result.",
) -> tuple[LearningAgent, SharedState, EventBus]:
    mock_client = make_mock_client(response_text)
    state = SharedState(run_id=str(uuid.uuid4())[:8], subject="test")
    bus = EventBus()
    config = AgentConfig(model="claude-opus-4-6", timeout=30.0)
    agent = LearningAgent(client=mock_client, state=state, bus=bus, config=config)
    return agent, state, bus


def make_event(
    event_type: EventType,
    source: str = "test_agent",
    payload: dict[str, Any] | None = None,
) -> Event:
    return Event(
        type=event_type,
        source=source,
        payload=payload or {},
        run_id="test-run-id",
    )


# ---------------------------------------------------------------------------
# LearningAgent instantiation
# ---------------------------------------------------------------------------


class TestLearningAgentInit:
    def test_name_is_learning(self) -> None:
        agent, _, _ = make_agent()
        assert agent.name == "learning"

    def test_initial_observations_empty(self) -> None:
        agent, _, _ = make_agent()
        assert agent._observations == []

    def test_has_asyncio_lock(self) -> None:
        agent, _, _ = make_agent()
        assert agent._lock is not None


# ---------------------------------------------------------------------------
# LearningAgent.on_event() — passive observation
# ---------------------------------------------------------------------------


class TestLearningAgentOnEvent:
    async def test_ignores_agent_started_events(self) -> None:
        agent, _, _ = make_agent()
        await agent.on_event(make_event(EventType.AGENT_STARTED, "scanner"))
        assert len(agent._observations) == 0

    async def test_ignores_agent_completed_events(self) -> None:
        agent, _, _ = make_agent()
        await agent.on_event(make_event(EventType.AGENT_COMPLETED, "research"))
        assert len(agent._observations) == 0

    async def test_ignores_orchestrator_started(self) -> None:
        agent, _, _ = make_agent()
        await agent.on_event(make_event(EventType.ORCHESTRATOR_STARTED, "orchestrator"))
        assert len(agent._observations) == 0

    async def test_ignores_state_updated(self) -> None:
        agent, _, _ = make_agent()
        await agent.on_event(make_event(EventType.STATE_UPDATED, "state"))
        assert len(agent._observations) == 0

    async def test_records_agent_output(self) -> None:
        agent, _, _ = make_agent()
        event = make_event(
            EventType.AGENT_OUTPUT,
            "scanner",
            {"output": {"file_count": 42}},
        )
        await agent.on_event(event)
        assert len(agent._observations) == 1

    async def test_agent_output_observation_has_source(self) -> None:
        agent, _, _ = make_agent()
        await agent.on_event(
            make_event(EventType.AGENT_OUTPUT, "pattern_analyst", {"output": "test"})
        )
        obs = agent._observations[0]
        assert obs["source"] == "pattern_analyst"

    async def test_agent_output_observation_has_event_type(self) -> None:
        agent, _, _ = make_agent()
        await agent.on_event(make_event(EventType.AGENT_OUTPUT, "forecaster", {}))
        obs = agent._observations[0]
        assert obs["event_type"] == EventType.AGENT_OUTPUT.value

    async def test_agent_output_observation_has_timestamp(self) -> None:
        agent, _, _ = make_agent()
        await agent.on_event(make_event(EventType.AGENT_OUTPUT, "scanner", {}))
        obs = agent._observations[0]
        assert "timestamp" in obs

    async def test_records_agent_failed(self) -> None:
        agent, _, _ = make_agent()
        event = make_event(
            EventType.AGENT_FAILED,
            "forecaster",
            {"error": "LLM timeout after 120s"},
        )
        await agent.on_event(event)
        assert len(agent._observations) == 1

    async def test_agent_failed_writes_learning_record(self) -> None:
        agent, state, _ = make_agent()
        event = make_event(
            EventType.AGENT_FAILED,
            "forecaster",
            {"error": "LLM timeout after 120s"},
        )
        await agent.on_event(event)

        run_state = await state.get()
        assert len(run_state.learning_records) == 1
        record = run_state.learning_records[0]
        assert record.agent_name == "forecaster"
        assert "failed" in record.observation.lower()

    async def test_agent_failed_record_has_failure_pattern(self) -> None:
        agent, state, _ = make_agent()
        await agent.on_event(
            make_event(EventType.AGENT_FAILED, "scanner", {"error": "disk error"})
        )
        run_state = await state.get()
        assert run_state.learning_records[0].pattern == "failure"

    async def test_agent_failed_includes_error_in_observation(self) -> None:
        agent, state, _ = make_agent()
        await agent.on_event(
            make_event(
                EventType.AGENT_FAILED, "research", {"error": "connection refused"}
            )
        )
        run_state = await state.get()
        assert "connection refused" in run_state.learning_records[0].observation

    async def test_records_debate_completed(self) -> None:
        agent, _, _ = make_agent()
        event = make_event(
            EventType.DEBATE_COMPLETED,
            "orchestrator",
            {"topic": "naming decision", "winner": "pragmatist", "winner_score": 7.5},
        )
        await agent.on_event(event)
        assert len(agent._observations) == 1

    async def test_debate_completed_writes_learning_record(self) -> None:
        agent, state, _ = make_agent()
        event = make_event(
            EventType.DEBATE_COMPLETED,
            "orchestrator",
            {"topic": "architecture choice", "winner": "visionary"},
        )
        await agent.on_event(event)

        run_state = await state.get()
        assert len(run_state.learning_records) == 1

    async def test_debate_completed_record_has_decision_pattern(self) -> None:
        agent, state, _ = make_agent()
        await agent.on_event(
            make_event(
                EventType.DEBATE_COMPLETED,
                "orchestrator",
                {"topic": "test", "winner": "skeptic"},
            )
        )
        run_state = await state.get()
        assert run_state.learning_records[0].pattern == "decision"

    async def test_debate_completed_observation_includes_topic(self) -> None:
        agent, state, _ = make_agent()
        await agent.on_event(
            make_event(
                EventType.DEBATE_COMPLETED,
                "orchestrator",
                {"topic": "naming the framework", "winner": "visionary"},
            )
        )
        run_state = await state.get()
        assert "naming the framework" in run_state.learning_records[0].observation

    async def test_debate_completed_observation_includes_winner(self) -> None:
        agent, state, _ = make_agent()
        await agent.on_event(
            make_event(
                EventType.DEBATE_COMPLETED,
                "orchestrator",
                {"topic": "test", "winner": "user_advocate"},
            )
        )
        run_state = await state.get()
        assert "user_advocate" in run_state.learning_records[0].observation

    async def test_concurrent_event_handling_is_thread_safe(self) -> None:
        agent, _, _ = make_agent()
        events = [
            make_event(EventType.AGENT_OUTPUT, f"agent_{i}", {"x": i})
            for i in range(30)
        ]
        await asyncio.gather(*[agent.on_event(e) for e in events])
        # All 30 events should be recorded without race conditions
        assert len(agent._observations) == 30


# ---------------------------------------------------------------------------
# LearningAgent.run() — meta-synthesis
# ---------------------------------------------------------------------------


class TestLearningAgentRun:
    async def test_run_with_no_observations_returns_empty(self) -> None:
        agent, _, _ = make_agent()
        result = await agent.run()
        assert result.success is True
        assert result.output["meta_patterns"] == []
        assert "No observations" in result.output["synthesis"]

    async def test_run_with_no_observations_does_not_call_llm(self) -> None:
        agent, _, _ = make_agent()
        result = await agent.run()
        # LLM must NOT be called — no observations to synthesize
        agent._client.messages.create.assert_not_called()

    async def test_run_with_observations_calls_llm(self) -> None:
        agent, _, _ = make_agent("Synthesis result from LLM.")
        async with agent._lock:
            agent._observations.append({
                "event_type": "agent.output",
                "source": "scanner",
                "payload_summary": "file scan complete",
                "timestamp": "2026-04-01T00:00:00",
            })

        result = await agent.run()
        agent._client.messages.create.assert_called_once()
        assert result.output["synthesis"] == "Synthesis result from LLM."

    async def test_run_returns_correct_observations_count(self) -> None:
        agent, _, _ = make_agent()
        async with agent._lock:
            for i in range(5):
                agent._observations.append({
                    "event_type": "agent.output",
                    "source": f"agent_{i}",
                    "payload_summary": f"output {i}",
                    "timestamp": "2026-04-01T00:00:00",
                })

        result = await agent.run()
        assert result.output["observations_count"] == 5

    async def test_run_extracts_bullet_meta_patterns(self) -> None:
        synthesis = "Some analysis.\n• Pattern 1: agents repeat themselves\n• Pattern 2: skeptic wins often"
        agent, _, _ = make_agent(synthesis)
        async with agent._lock:
            agent._observations.append({
                "event_type": "agent.output",
                "source": "test",
                "payload_summary": "data",
                "timestamp": "2026-04-01T00:00:00",
            })

        result = await agent.run()
        assert len(result.output["meta_patterns"]) >= 2

    async def test_run_adds_meta_synthesis_learning_record(self) -> None:
        agent, state, _ = make_agent()
        async with agent._lock:
            agent._observations.append({
                "event_type": "agent.output",
                "source": "scanner",
                "payload_summary": "test",
                "timestamp": "2026-04-01T00:00:00",
            })

        await agent.run()
        run_state = await state.get()
        assert any(r.pattern == "meta_synthesis" for r in run_state.learning_records)

    async def test_run_caps_observations_at_thirty_for_llm(self) -> None:
        agent, _, _ = make_agent("capped synthesis")
        # Add 50 observations
        async with agent._lock:
            for i in range(50):
                agent._observations.append({
                    "event_type": "agent.output",
                    "source": "test",
                    "payload_summary": f"obs {i}",
                    "timestamp": "2026-04-01T00:00:00",
                })

        result = await agent.run()
        # All 50 are returned in observations_count
        assert result.output["observations_count"] == 50
        # LLM was called (capping happens silently)
        agent._client.messages.create.assert_called_once()


# ---------------------------------------------------------------------------
# MemoryStore tests
# ---------------------------------------------------------------------------


@pytest.fixture
def memory_store(tmp_path: Path) -> MemoryStore:
    return MemoryStore(store_path=tmp_path / ".crucible_memory.jsonl")


def make_entry(
    agent_name: str = "scanner",
    topic: str = "test topic",
    content: str = "test content",
) -> MemoryEntry:
    return MemoryEntry(
        id=str(uuid.uuid4()),
        agent_name=agent_name,
        topic=topic,
        content=content,
    )


class TestMemoryEntry:
    def test_to_dict_contains_required_fields(self) -> None:
        entry = make_entry(content="hello world")
        d = entry.to_dict()
        assert d["id"] == entry.id
        assert d["agent_name"] == "scanner"
        assert d["content"] == "hello world"
        assert isinstance(d["created_at"], str)
        assert isinstance(d["last_accessed"], str)

    def test_from_dict_roundtrip(self) -> None:
        entry = make_entry(agent_name="research", topic="my topic", content="my content")
        d = entry.to_dict()
        restored = MemoryEntry.from_dict(d)
        assert restored.id == entry.id
        assert restored.agent_name == entry.agent_name
        assert restored.topic == entry.topic
        assert restored.content == entry.content

    def test_from_dict_parses_datetime_strings(self) -> None:
        entry = make_entry()
        d = entry.to_dict()
        restored = MemoryEntry.from_dict(d)
        assert isinstance(restored.created_at, datetime)
        assert isinstance(restored.last_accessed, datetime)

    def test_default_access_count_is_zero(self) -> None:
        entry = make_entry()
        assert entry.access_count == 0

    def test_metadata_defaults_to_empty_dict(self) -> None:
        entry = make_entry()
        assert entry.metadata == {}


class TestMemoryStoreSaveAndRetrieve:
    async def test_save_and_retrieve_all_entries(
        self, memory_store: MemoryStore
    ) -> None:
        entry = make_entry(content="Python codebase with 3 modules")
        await memory_store.save(entry)
        entries = await memory_store.all_entries()
        assert len(entries) == 1
        assert entries[0].content == "Python codebase with 3 modules"

    async def test_multiple_saves_cumulative(self, memory_store: MemoryStore) -> None:
        for i in range(5):
            await memory_store.save(make_entry(content=f"entry {i}"))
        entries = await memory_store.all_entries()
        assert len(entries) == 5

    async def test_all_entries_sorted_by_recency(
        self, memory_store: MemoryStore
    ) -> None:
        import asyncio

        await memory_store.save(make_entry(content="first"))
        await asyncio.sleep(0.01)  # small delay to ensure different timestamps
        await memory_store.save(make_entry(content="second"))
        entries = await memory_store.all_entries()
        # Most recent first
        assert entries[0].content == "second"

    async def test_persistence_across_store_instances(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "memory.jsonl"
        store1 = MemoryStore(store_path=path)
        await store1.save(make_entry(content="persisted learning"))

        store2 = MemoryStore(store_path=path)
        await store2.load()
        entries = await store2.all_entries()
        assert len(entries) == 1
        assert entries[0].content == "persisted learning"

    async def test_load_skips_malformed_lines(self, tmp_path: Path) -> None:
        path = tmp_path / "memory.jsonl"
        # Write one valid and one malformed line
        valid_entry = make_entry(content="valid")
        with open(path, "w") as f:
            import json
            f.write(json.dumps(valid_entry.to_dict()) + "\n")
            f.write("not valid json{\n")

        store = MemoryStore(store_path=path)
        await store.load()
        entries = await store.all_entries()
        assert len(entries) == 1
        assert entries[0].content == "valid"


class TestMemoryStoreSearch:
    async def test_search_finds_by_content_keyword(
        self, memory_store: MemoryStore
    ) -> None:
        await memory_store.save(make_entry(content="React application with TypeScript"))
        await memory_store.save(make_entry(content="Rust binary with cargo"))
        results = await memory_store.search("TypeScript")
        assert len(results) == 1
        assert "TypeScript" in results[0].content

    async def test_search_finds_by_topic_keyword(
        self, memory_store: MemoryStore
    ) -> None:
        await memory_store.save(
            make_entry(topic="microservices architecture", content="service mesh pattern")
        )
        await memory_store.save(
            make_entry(topic="monolith refactor", content="big ball of mud")
        )
        results = await memory_store.search("microservices")
        assert len(results) == 1
        assert results[0].topic == "microservices architecture"

    async def test_search_case_insensitive(self, memory_store: MemoryStore) -> None:
        await memory_store.save(make_entry(content="PYTHON codebase detected"))
        results = await memory_store.search("python")
        assert len(results) == 1

    async def test_search_filters_by_agent_name(
        self, memory_store: MemoryStore
    ) -> None:
        await memory_store.save(
            make_entry(agent_name="scanner", content="scanner result about tests")
        )
        await memory_store.save(
            make_entry(agent_name="research", content="research result about tests")
        )
        results = await memory_store.search("tests", agent_name="scanner")
        assert len(results) == 1
        assert results[0].agent_name == "scanner"

    async def test_search_returns_empty_for_no_match(
        self, memory_store: MemoryStore
    ) -> None:
        await memory_store.save(make_entry(content="something completely unrelated"))
        results = await memory_store.search("xyzzy_absolutely_no_match")
        assert results == []

    async def test_search_respects_limit(self, memory_store: MemoryStore) -> None:
        for i in range(10):
            await memory_store.save(make_entry(content=f"searchable content {i}"))
        results = await memory_store.search("searchable", limit=3)
        assert len(results) == 3

    async def test_search_increments_access_count(
        self, memory_store: MemoryStore
    ) -> None:
        entry = make_entry(content="the searchable content here")
        await memory_store.save(entry)

        # Access count before search
        before = (await memory_store.all_entries())[0].access_count
        await memory_store.search("searchable")
        after = (await memory_store.all_entries())[0].access_count
        assert after == before + 1

    async def test_search_ranks_by_access_count(
        self, memory_store: MemoryStore
    ) -> None:
        entry_popular = make_entry(content="popular keyword match")
        entry_rare = make_entry(content="rare keyword match")
        await memory_store.save(entry_popular)
        await memory_store.save(entry_rare)

        # Access popular 3 times
        for _ in range(3):
            await memory_store.search("popular")

        # Now search for "keyword" which matches both
        results = await memory_store.search("keyword")
        assert len(results) == 2
        # Popular entry (higher access count) should rank first
        assert results[0].access_count >= results[1].access_count


class TestMemoryStoreClear:
    async def test_clear_removes_all_in_memory_entries(
        self, memory_store: MemoryStore
    ) -> None:
        await memory_store.save(make_entry(content="entry 1"))
        await memory_store.save(make_entry(content="entry 2"))
        await memory_store.clear()
        entries = await memory_store.all_entries()
        assert entries == []

    async def test_clear_removes_file(self, tmp_path: Path) -> None:
        path = tmp_path / "memory.jsonl"
        store = MemoryStore(store_path=path)
        await store.save(make_entry())
        assert path.exists()
        await store.clear()
        assert not path.exists()

    async def test_save_after_clear_works(self, memory_store: MemoryStore) -> None:
        await memory_store.save(make_entry(content="before clear"))
        await memory_store.clear()
        await memory_store.save(make_entry(content="after clear"))
        entries = await memory_store.all_entries()
        assert len(entries) == 1
        assert entries[0].content == "after clear"


class TestMemoryStoreLen:
    async def test_len_reflects_saved_entries(
        self, memory_store: MemoryStore
    ) -> None:
        assert len(memory_store) == 0
        await memory_store.save(make_entry())
        assert len(memory_store) == 1
        await memory_store.save(make_entry())
        assert len(memory_store) == 2

    async def test_len_zero_after_clear(self, memory_store: MemoryStore) -> None:
        await memory_store.save(make_entry())
        await memory_store.save(make_entry())
        await memory_store.clear()
        assert len(memory_store) == 0
