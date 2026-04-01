"""Tests for the SQLite memory persistence layer."""

from __future__ import annotations

import json
import threading
import time
import uuid
from pathlib import Path

import pytest

from crucible.memory.sqlite_store import SQLiteMemoryStore
from crucible.memory.migrations import migrate, _current_version
import sqlite3


# ------------------------------------------------------------------ #
# Fixtures                                                             #
# ------------------------------------------------------------------ #


@pytest.fixture
def tmp_store(tmp_path: Path) -> SQLiteMemoryStore:
    """Fresh store backed by a temp-dir DB."""
    return SQLiteMemoryStore(db_path=tmp_path / "test.db")


@pytest.fixture
def populated_store(tmp_store: SQLiteMemoryStore) -> SQLiteMemoryStore:
    """Store with one debate, one decision, two learnings, one run, one memory."""
    tmp_store.save_debate(
        debate_id="debate-001",
        topic="Microservices vs Monolith",
        rounds=[{"round": 1, "votes": {"micro": 3, "mono": 1}}],
        winner="micro",
        scores={"micro": 8.5, "mono": 6.0},
    )
    tmp_store.save_decision(
        debate_id="debate-001",
        decision="Use microservices for scalability",
        rationale="Higher score, better separation of concerns",
        confidence=0.85,
    )
    tmp_store.save_learning(
        agent_name="pattern_analyst",
        pattern="architecture",
        insight="Microservices suit high-traffic scenarios",
        source_debate_id="debate-001",
    )
    tmp_store.save_learning(
        agent_name="research",
        pattern="finding",
        insight="Monoliths are simpler to start with",
        source_debate_id=None,
    )
    tmp_store.save_agent_run(
        agent_name="research",
        run_id="run-001",
        inputs={"query": "microservices trends 2025"},
        outputs={"findings": ["finding1", "finding2"]},
        duration=3.14,
    )
    tmp_store.save_memory(
        entry_id="mem-001",
        agent_name="research",
        topic="microservices",
        content="Microservices enable independent deployment of services",
        metadata={"source": "arxiv"},
    )
    return tmp_store


# ------------------------------------------------------------------ #
# Migration tests                                                      #
# ------------------------------------------------------------------ #


class TestMigrations:
    def test_initial_migration_creates_tables(self, tmp_path: Path) -> None:
        conn = sqlite3.connect(str(tmp_path / "mig.db"))
        conn.row_factory = sqlite3.Row
        migrate(conn)

        tables = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        for expected in (
            "debates", "decisions", "learnings", "agent_runs", "memories", "schema_version"
        ):
            assert expected in tables, f"Missing table: {expected}"

    def test_version_tracked(self, tmp_path: Path) -> None:
        conn = sqlite3.connect(str(tmp_path / "mig.db"))
        conn.row_factory = sqlite3.Row
        migrate(conn)
        assert _current_version(conn) == 1

    def test_migration_idempotent(self, tmp_path: Path) -> None:
        conn = sqlite3.connect(str(tmp_path / "mig.db"))
        conn.row_factory = sqlite3.Row
        migrate(conn)
        migrate(conn)  # second call must be a no-op
        assert _current_version(conn) == 1


# ------------------------------------------------------------------ #
# CRUD — debates                                                       #
# ------------------------------------------------------------------ #


class TestDebates:
    def test_save_and_retrieve(self, tmp_store: SQLiteMemoryStore) -> None:
        tmp_store.save_debate(
            debate_id="d1",
            topic="REST vs GraphQL",
            rounds=[],
            winner="REST",
            scores={"REST": 7.0, "GraphQL": 6.5},
        )
        history = tmp_store.get_debate_history(limit=10)
        assert len(history) == 1
        assert history[0]["topic"] == "REST vs GraphQL"
        assert history[0]["winner"] == "REST"
        assert history[0]["winner_score"] == pytest.approx(7.0)

    def test_history_ordered_by_recency(self, tmp_store: SQLiteMemoryStore) -> None:
        for i in range(5):
            tmp_store.save_debate(
                debate_id=f"d{i}",
                topic=f"topic {i}",
                rounds=[],
                winner="A",
                scores={"A": float(i)},
            )
        history = tmp_store.get_debate_history(limit=5)
        assert history[0]["topic"] == "topic 4"

    def test_limit_respected(self, populated_store: SQLiteMemoryStore) -> None:
        history = populated_store.get_debate_history(limit=1)
        assert len(history) == 1

    def test_upsert_overwrites(self, tmp_store: SQLiteMemoryStore) -> None:
        tmp_store.save_debate("d1", "topic", [], "A", {"A": 5.0})
        tmp_store.save_debate("d1", "topic updated", [], "B", {"B": 9.0})
        history = tmp_store.get_debate_history()
        assert len(history) == 1
        assert history[0]["winner"] == "B"


# ------------------------------------------------------------------ #
# CRUD — decisions                                                     #
# ------------------------------------------------------------------ #


class TestDecisions:
    def test_save_decision(self, populated_store: SQLiteMemoryStore) -> None:
        # populated_store already has one decision; just verify no error
        # and that get_stats reflects it
        stats = populated_store.get_stats()
        assert stats["decisions"] >= 1


# ------------------------------------------------------------------ #
# CRUD — learnings                                                     #
# ------------------------------------------------------------------ #


class TestLearnings:
    def test_get_all_learnings(self, populated_store: SQLiteMemoryStore) -> None:
        learnings = populated_store.get_learnings()
        assert len(learnings) == 2

    def test_filter_by_agent(self, populated_store: SQLiteMemoryStore) -> None:
        learnings = populated_store.get_learnings(agent_name="research")
        assert len(learnings) == 1
        assert learnings[0]["agent_name"] == "research"

    def test_save_without_debate_id(self, tmp_store: SQLiteMemoryStore) -> None:
        tmp_store.save_learning("agent", "pattern", "insight")
        learnings = tmp_store.get_learnings()
        assert len(learnings) == 1
        assert learnings[0]["source_debate_id"] is None


# ------------------------------------------------------------------ #
# CRUD — agent runs                                                    #
# ------------------------------------------------------------------ #


class TestAgentRuns:
    def test_performance_stats(self, populated_store: SQLiteMemoryStore) -> None:
        perf = populated_store.get_agent_performance("research")
        assert perf["agent_name"] == "research"
        assert perf["total_runs"] == 1
        assert perf["avg_duration_seconds"] == pytest.approx(3.14, rel=1e-3)

    def test_unknown_agent_returns_zeros(self, tmp_store: SQLiteMemoryStore) -> None:
        perf = tmp_store.get_agent_performance("nonexistent")
        assert perf["total_runs"] == 0
        assert perf["win_rate"] == 0.0

    def test_win_rate_calculation(self, tmp_store: SQLiteMemoryStore) -> None:
        tmp_store.save_debate("d1", "T", [], "alpha", {"alpha": 9.0, "beta": 7.0})
        tmp_store.save_debate("d2", "T", [], "beta", {"alpha": 6.0, "beta": 8.0})
        perf = tmp_store.get_agent_performance("alpha")
        assert perf["debates_participated"] == 2
        assert perf["debate_wins"] == 1
        assert perf["win_rate"] == pytest.approx(0.5)


# ------------------------------------------------------------------ #
# Full-text search                                                     #
# ------------------------------------------------------------------ #


class TestFullTextSearch:
    def test_basic_keyword_match(self, populated_store: SQLiteMemoryStore) -> None:
        results = populated_store.query_memories("microservices")
        assert len(results) == 1
        assert results[0]["id"] == "mem-001"

    def test_no_match_returns_empty(self, populated_store: SQLiteMemoryStore) -> None:
        results = populated_store.query_memories("quantum computing")
        assert results == []

    def test_agent_name_filter(self, tmp_store: SQLiteMemoryStore) -> None:
        tmp_store.save_memory("m1", "agent_a", "topic", "shared keyword content")
        tmp_store.save_memory("m2", "agent_b", "topic", "shared keyword content")
        results = tmp_store.query_memories("keyword", agent_name="agent_a")
        assert len(results) == 1
        assert results[0]["agent_name"] == "agent_a"

    def test_access_count_incremented(self, populated_store: SQLiteMemoryStore) -> None:
        populated_store.query_memories("microservices")
        results = populated_store.query_memories("microservices")
        # access_count should be >= 1 (it was incremented on first query)
        assert results[0]["access_count"] >= 1

    def test_limit_respected(self, tmp_store: SQLiteMemoryStore) -> None:
        for i in range(10):
            tmp_store.save_memory(
                entry_id=str(i),
                agent_name="a",
                topic="topic",
                content=f"the quick brown fox number {i}",
            )
        results = tmp_store.query_memories("quick", limit=3)
        assert len(results) <= 3


# ------------------------------------------------------------------ #
# Export / Import roundtrip                                            #
# ------------------------------------------------------------------ #


class TestExportImport:
    def test_roundtrip(self, populated_store: SQLiteMemoryStore, tmp_path: Path) -> None:
        exported = populated_store.export_to_json()
        assert "exported_at" in exported
        assert len(exported["debates"]) == 1
        assert len(exported["learnings"]) == 2
        assert len(exported["memories"]) == 1

        new_store = SQLiteMemoryStore(db_path=tmp_path / "import.db")
        new_store.import_from_json(exported)

        imported_debates = new_store.get_debate_history()
        assert len(imported_debates) == 1
        assert imported_debates[0]["topic"] == "Microservices vs Monolith"

        imported_learnings = new_store.get_learnings()
        assert len(imported_learnings) == 2

        imported_memories = new_store.query_memories("Microservices")
        assert len(imported_memories) == 1

    def test_import_is_merge_not_replace(
        self, populated_store: SQLiteMemoryStore, tmp_path: Path
    ) -> None:
        new_store = SQLiteMemoryStore(db_path=tmp_path / "merge.db")
        new_store.save_debate("existing", "existing topic", [], "X", {"X": 5.0})

        exported = populated_store.export_to_json()
        new_store.import_from_json(exported)

        history = new_store.get_debate_history()
        assert len(history) == 2  # existing + imported

    def test_duplicate_import_idempotent(
        self, populated_store: SQLiteMemoryStore, tmp_path: Path
    ) -> None:
        exported = populated_store.export_to_json()
        new_store = SQLiteMemoryStore(db_path=tmp_path / "idem.db")
        new_store.import_from_json(exported)
        new_store.import_from_json(exported)  # second import must not duplicate

        assert len(new_store.get_debate_history()) == 1


# ------------------------------------------------------------------ #
# Concurrent access                                                    #
# ------------------------------------------------------------------ #


class TestConcurrentAccess:
    def test_threaded_writes_no_data_loss(self, tmp_path: Path) -> None:
        store = SQLiteMemoryStore(db_path=tmp_path / "concurrent.db")
        errors: list[Exception] = []

        def writer(idx: int) -> None:
            try:
                store.save_debate(
                    debate_id=f"d{idx}",
                    topic=f"Topic {idx}",
                    rounds=[],
                    winner="A",
                    scores={"A": float(idx % 10)},
                )
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Thread errors: {errors}"
        history = store.get_debate_history(limit=100)
        assert len(history) == 20

    def test_concurrent_reads_and_writes(self, tmp_path: Path) -> None:
        store = SQLiteMemoryStore(db_path=tmp_path / "rw.db")
        # Seed some data
        store.save_debate("d0", "seed", [], "A", {"A": 5.0})

        errors: list[Exception] = []

        def reader() -> None:
            try:
                store.get_debate_history(limit=5)
            except Exception as exc:
                errors.append(exc)

        def writer(idx: int) -> None:
            try:
                store.save_debate(f"dw{idx}", f"T{idx}", [], "B", {"B": 1.0})
            except Exception as exc:
                errors.append(exc)

        threads = (
            [threading.Thread(target=reader) for _ in range(10)]
            + [threading.Thread(target=writer, args=(i,)) for i in range(10)]
        )
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Thread errors: {errors}"


# ------------------------------------------------------------------ #
# Stats                                                                #
# ------------------------------------------------------------------ #


class TestStats:
    def test_stats_counts(self, populated_store: SQLiteMemoryStore) -> None:
        stats = populated_store.get_stats()
        assert stats["debates"] == 1
        assert stats["decisions"] == 1
        assert stats["learnings"] == 2
        assert stats["agent_runs"] == 1
        assert stats["memories"] == 1

    def test_empty_store_stats(self, tmp_store: SQLiteMemoryStore) -> None:
        stats = tmp_store.get_stats()
        assert all(stats[k] == 0 for k in ("debates", "decisions", "learnings", "agent_runs", "memories"))
