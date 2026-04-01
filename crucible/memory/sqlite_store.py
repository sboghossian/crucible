"""SQLite-backed persistent memory store for cross-session learning."""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from .migrations import migrate

logger = logging.getLogger(__name__)

_SENTINEL = object()


class SQLiteMemoryStore:
    """
    Thread-safe SQLite memory store.

    Uses Python's built-in sqlite3 module — no external dependencies.
    Each method acquires a per-connection lock so the store is safe to
    call from multiple threads (or asyncio tasks via run_in_executor).
    """

    def __init__(self, db_path: str | Path = ".crucible_memory.db") -> None:
        self._path = Path(db_path)
        self._lock = threading.Lock()
        self._conn: sqlite3.Connection | None = None

    # ------------------------------------------------------------------ #
    # Connection management                                                #
    # ------------------------------------------------------------------ #

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(
                str(self._path),
                check_same_thread=False,
                timeout=30,
            )
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
            migrate(self._conn)
        return self._conn

    def close(self) -> None:
        with self._lock:
            if self._conn is not None:
                self._conn.close()
                self._conn = None

    # ------------------------------------------------------------------ #
    # Debates                                                              #
    # ------------------------------------------------------------------ #

    def save_debate(
        self,
        debate_id: str,
        topic: str,
        rounds: list[dict[str, Any]],
        winner: str,
        scores: dict[str, float],
    ) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """
                INSERT OR REPLACE INTO debates
                    (id, topic, winner, winner_score, rounds_json, scores_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    debate_id,
                    topic,
                    winner,
                    float(scores.get(winner, 0.0)),
                    json.dumps(rounds),
                    json.dumps(scores),
                ),
            )
            conn.commit()

    def get_debate_history(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._lock:
            conn = self._get_conn()
            rows = conn.execute(
                """
                SELECT id, topic, winner, winner_score, scores_json, created_at
                FROM debates
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "id": r["id"],
                "topic": r["topic"],
                "winner": r["winner"],
                "winner_score": r["winner_score"],
                "scores": json.loads(r["scores_json"]),
                "created_at": r["created_at"],
            }
            for r in rows
        ]

    # ------------------------------------------------------------------ #
    # Decisions                                                            #
    # ------------------------------------------------------------------ #

    def save_decision(
        self,
        debate_id: str,
        decision: str,
        rationale: str,
        confidence: float,
    ) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """
                INSERT INTO decisions (debate_id, decision, rationale, confidence)
                VALUES (?, ?, ?, ?)
                """,
                (debate_id, decision, rationale, confidence),
            )
            conn.commit()

    # ------------------------------------------------------------------ #
    # Learnings                                                            #
    # ------------------------------------------------------------------ #

    def save_learning(
        self,
        agent_name: str,
        pattern: str,
        insight: str,
        source_debate_id: str | None = None,
    ) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """
                INSERT INTO learnings (agent_name, pattern, insight, source_debate_id)
                VALUES (?, ?, ?, ?)
                """,
                (agent_name, pattern, insight, source_debate_id),
            )
            conn.commit()

    def get_learnings(
        self,
        agent_name: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        with self._lock:
            conn = self._get_conn()
            if agent_name:
                rows = conn.execute(
                    """
                    SELECT agent_name, pattern, insight, source_debate_id, created_at
                    FROM learnings
                    WHERE agent_name = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (agent_name, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT agent_name, pattern, insight, source_debate_id, created_at
                    FROM learnings
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------ #
    # Agent runs                                                           #
    # ------------------------------------------------------------------ #

    def save_agent_run(
        self,
        agent_name: str,
        run_id: str,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        duration: float,
    ) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """
                INSERT OR REPLACE INTO agent_runs
                    (id, agent_name, inputs_json, outputs_json, duration_seconds)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    agent_name,
                    json.dumps(inputs),
                    json.dumps(outputs),
                    duration,
                ),
            )
            conn.commit()

    def get_agent_performance(self, agent_name: str) -> dict[str, Any]:
        """Return win rates and average scores for an agent across all debates."""
        with self._lock:
            conn = self._get_conn()

            run_stats = conn.execute(
                """
                SELECT COUNT(*) as total_runs,
                       AVG(duration_seconds) as avg_duration
                FROM agent_runs
                WHERE agent_name = ?
                """,
                (agent_name,),
            ).fetchone()

            debate_stats = conn.execute(
                """
                SELECT COUNT(*) as total_debates,
                       SUM(CASE WHEN winner = ? THEN 1 ELSE 0 END) as wins,
                       AVG(CASE WHEN scores_json LIKE ? THEN 1 ELSE 0 END) as participation
                FROM debates
                """,
                (agent_name, f'%"{agent_name}"%'),
            ).fetchone()

            scores_row = conn.execute(
                """
                SELECT scores_json FROM debates
                WHERE scores_json LIKE ?
                ORDER BY created_at DESC
                LIMIT 100
                """,
                (f'%"{agent_name}"%',),
            ).fetchall()

        scores: list[float] = []
        for row in scores_row:
            try:
                s = json.loads(row["scores_json"])
                if agent_name in s:
                    scores.append(float(s[agent_name]))
            except (json.JSONDecodeError, KeyError, ValueError):
                pass

        avg_score = sum(scores) / len(scores) if scores else 0.0
        wins = debate_stats["wins"] or 0
        total_debates = len(scores)
        win_rate = wins / total_debates if total_debates > 0 else 0.0

        return {
            "agent_name": agent_name,
            "total_runs": run_stats["total_runs"] or 0,
            "avg_duration_seconds": round(run_stats["avg_duration"] or 0.0, 3),
            "debates_participated": total_debates,
            "debate_wins": wins,
            "win_rate": round(win_rate, 3),
            "avg_score": round(avg_score, 3),
        }

    # ------------------------------------------------------------------ #
    # General memories (replaces the old MemoryStore JSONL approach)      #
    # ------------------------------------------------------------------ #

    def save_memory(
        self,
        entry_id: str,
        agent_name: str,
        topic: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """
                INSERT OR REPLACE INTO memories
                    (id, agent_name, topic, content, metadata_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    entry_id,
                    agent_name,
                    topic,
                    content,
                    json.dumps(metadata or {}),
                ),
            )
            conn.commit()

    def query_memories(
        self,
        keywords: str,
        agent_name: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Full-text search over memory content using SQLite FTS5."""
        with self._lock:
            conn = self._get_conn()

            if agent_name:
                rows = conn.execute(
                    """
                    SELECT m.id, m.agent_name, m.topic, m.content,
                           m.metadata_json, m.access_count,
                           m.last_accessed, m.created_at
                    FROM memories m
                    JOIN memories_fts f ON m.rowid = f.rowid
                    WHERE memories_fts MATCH ?
                      AND m.agent_name = ?
                    ORDER BY rank, m.access_count DESC
                    LIMIT ?
                    """,
                    (keywords, agent_name, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT m.id, m.agent_name, m.topic, m.content,
                           m.metadata_json, m.access_count,
                           m.last_accessed, m.created_at
                    FROM memories m
                    JOIN memories_fts f ON m.rowid = f.rowid
                    WHERE memories_fts MATCH ?
                    ORDER BY rank, m.access_count DESC
                    LIMIT ?
                    """,
                    (keywords, limit),
                ).fetchall()

            ids = [r["id"] for r in rows]
            if ids:
                placeholders = ",".join("?" * len(ids))
                conn.execute(
                    f"""
                    UPDATE memories
                    SET access_count = access_count + 1,
                        last_accessed = datetime('now')
                    WHERE id IN ({placeholders})
                    """,
                    ids,
                )
                conn.commit()

        return [
            {
                "id": r["id"],
                "agent_name": r["agent_name"],
                "topic": r["topic"],
                "content": r["content"],
                "metadata": json.loads(r["metadata_json"]),
                "access_count": r["access_count"],
                "last_accessed": r["last_accessed"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]

    # ------------------------------------------------------------------ #
    # Export / Import                                                      #
    # ------------------------------------------------------------------ #

    def export_to_json(self) -> dict[str, Any]:
        """Dump the full store to a JSON-serialisable dict."""
        with self._lock:
            conn = self._get_conn()

            debates = [
                {
                    "id": r["id"],
                    "topic": r["topic"],
                    "winner": r["winner"],
                    "winner_score": r["winner_score"],
                    "rounds": json.loads(r["rounds_json"]),
                    "scores": json.loads(r["scores_json"]),
                    "created_at": r["created_at"],
                }
                for r in conn.execute("SELECT * FROM debates ORDER BY created_at").fetchall()
            ]

            decisions = [
                {
                    "id": r["id"],
                    "debate_id": r["debate_id"],
                    "decision": r["decision"],
                    "rationale": r["rationale"],
                    "confidence": r["confidence"],
                    "created_at": r["created_at"],
                }
                for r in conn.execute("SELECT * FROM decisions ORDER BY created_at").fetchall()
            ]

            learnings = [
                dict(r)
                for r in conn.execute("SELECT * FROM learnings ORDER BY created_at").fetchall()
            ]

            agent_runs = [
                {
                    "id": r["id"],
                    "agent_name": r["agent_name"],
                    "inputs": json.loads(r["inputs_json"]),
                    "outputs": json.loads(r["outputs_json"]),
                    "duration_seconds": r["duration_seconds"],
                    "created_at": r["created_at"],
                }
                for r in conn.execute("SELECT * FROM agent_runs ORDER BY created_at").fetchall()
            ]

            memories = [
                {
                    "id": r["id"],
                    "agent_name": r["agent_name"],
                    "topic": r["topic"],
                    "content": r["content"],
                    "metadata": json.loads(r["metadata_json"]),
                    "access_count": r["access_count"],
                    "last_accessed": r["last_accessed"],
                    "created_at": r["created_at"],
                }
                for r in conn.execute("SELECT * FROM memories ORDER BY created_at").fetchall()
            ]

        return {
            "exported_at": datetime.utcnow().isoformat(),
            "debates": debates,
            "decisions": decisions,
            "learnings": learnings,
            "agent_runs": agent_runs,
            "memories": memories,
        }

    def import_from_json(self, data: dict[str, Any]) -> None:
        """Restore records from a previously exported dict (merge, not replace)."""
        with self._lock:
            conn = self._get_conn()

            for d in data.get("debates", []):
                conn.execute(
                    """
                    INSERT OR IGNORE INTO debates
                        (id, topic, winner, winner_score, rounds_json, scores_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        d["id"], d["topic"], d["winner"], d["winner_score"],
                        json.dumps(d.get("rounds", [])),
                        json.dumps(d.get("scores", {})),
                        d.get("created_at", datetime.utcnow().isoformat()),
                    ),
                )

            for dec in data.get("decisions", []):
                conn.execute(
                    """
                    INSERT OR IGNORE INTO decisions
                        (id, debate_id, decision, rationale, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        dec.get("id"),
                        dec["debate_id"], dec["decision"],
                        dec["rationale"], dec["confidence"],
                        dec.get("created_at", datetime.utcnow().isoformat()),
                    ),
                )

            for lrn in data.get("learnings", []):
                conn.execute(
                    """
                    INSERT OR IGNORE INTO learnings
                        (id, agent_name, pattern, insight, source_debate_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        lrn.get("id"),
                        lrn["agent_name"], lrn["pattern"],
                        lrn["insight"], lrn.get("source_debate_id"),
                        lrn.get("created_at", datetime.utcnow().isoformat()),
                    ),
                )

            for run in data.get("agent_runs", []):
                conn.execute(
                    """
                    INSERT OR IGNORE INTO agent_runs
                        (id, agent_name, inputs_json, outputs_json, duration_seconds, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run["id"], run["agent_name"],
                        json.dumps(run.get("inputs", {})),
                        json.dumps(run.get("outputs", {})),
                        run.get("duration_seconds", 0.0),
                        run.get("created_at", datetime.utcnow().isoformat()),
                    ),
                )

            for mem in data.get("memories", []):
                conn.execute(
                    """
                    INSERT OR IGNORE INTO memories
                        (id, agent_name, topic, content, metadata_json,
                         access_count, last_accessed, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        mem["id"], mem["agent_name"],
                        mem["topic"], mem["content"],
                        json.dumps(mem.get("metadata", {})),
                        mem.get("access_count", 0),
                        mem.get("last_accessed", datetime.utcnow().isoformat()),
                        mem.get("created_at", datetime.utcnow().isoformat()),
                    ),
                )

            conn.commit()

    # ------------------------------------------------------------------ #
    # Stats helper                                                         #
    # ------------------------------------------------------------------ #

    def get_stats(self) -> dict[str, Any]:
        with self._lock:
            conn = self._get_conn()
            stats: dict[str, Any] = {}
            for table in ("debates", "decisions", "learnings", "agent_runs", "memories"):
                row = conn.execute(f"SELECT COUNT(*) as n FROM {table}").fetchone()
                stats[table] = row["n"]

            top_agents = conn.execute(
                """
                SELECT agent_name, COUNT(*) as runs
                FROM agent_runs
                GROUP BY agent_name
                ORDER BY runs DESC
                LIMIT 10
                """
            ).fetchall()
            stats["top_agents"] = [dict(r) for r in top_agents]

            win_leaders = conn.execute(
                """
                SELECT winner, COUNT(*) as wins
                FROM debates
                WHERE winner != ''
                GROUP BY winner
                ORDER BY wins DESC
                LIMIT 5
                """
            ).fetchall()
            stats["debate_winners"] = [dict(r) for r in win_leaders]

        return stats
