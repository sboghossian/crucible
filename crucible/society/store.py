"""SQLite persistence for all Agent Society data."""

from __future__ import annotations

import json
import sqlite3
import threading
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from .identity import AgentIdentity
from .economy import XPTransaction
from .personality import PersonalitySnapshot
from .relationships import AgentRelationship
from .language import CompressionToken
from .skills import Skill

logger = logging.getLogger(__name__)

# Migration version for society tables
SOCIETY_MIGRATION_VERSION = 3

SOCIETY_SCHEMA = """
CREATE TABLE IF NOT EXISTS agent_identities (
    agent_id    TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    agent_type  TEXT NOT NULL DEFAULT 'generic',
    creator     TEXT NOT NULL DEFAULT 'Steph',
    xp          INTEGER NOT NULL DEFAULT 0,
    traits_json TEXT NOT NULL DEFAULT '{}',
    skill_names_json TEXT NOT NULL DEFAULT '[]',
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    last_active TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS agent_relationships (
    agent_id            TEXT NOT NULL,
    peer_id             TEXT NOT NULL,
    trust               REAL NOT NULL DEFAULT 0.5,
    collaboration_count INTEGER NOT NULL DEFAULT 0,
    success_count       INTEGER NOT NULL DEFAULT 0,
    last_interaction    TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (agent_id, peer_id)
);

CREATE TABLE IF NOT EXISTS xp_transactions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id     TEXT NOT NULL,
    event        TEXT NOT NULL,
    amount       INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    context      TEXT NOT NULL DEFAULT '',
    occurred_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS skill_acquisitions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id     TEXT NOT NULL,
    skill_name   TEXT NOT NULL,
    proficiency  REAL NOT NULL DEFAULT 0.5,
    source       TEXT NOT NULL DEFAULT 'self',
    use_count    INTEGER NOT NULL DEFAULT 0,
    acquired_at  TEXT NOT NULL DEFAULT (datetime('now')),
    last_used    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS compression_tokens (
    token_id         TEXT PRIMARY KEY,
    agent_a          TEXT NOT NULL,
    agent_b          TEXT NOT NULL,
    concept          TEXT NOT NULL,
    token            TEXT NOT NULL,
    use_count        INTEGER NOT NULL DEFAULT 0,
    is_active        INTEGER NOT NULL DEFAULT 0,
    last_used_cycle  INTEGER NOT NULL DEFAULT 0,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS personality_snapshots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id    TEXT NOT NULL,
    traits_json TEXT NOT NULL DEFAULT '{}',
    cycle       INTEGER NOT NULL DEFAULT 0,
    reason      TEXT NOT NULL DEFAULT '',
    recorded_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_xp_agent ON xp_transactions(agent_id);
CREATE INDEX IF NOT EXISTS idx_skills_agent ON skill_acquisitions(agent_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_agent ON personality_snapshots(agent_id);
CREATE INDEX IF NOT EXISTS idx_tokens_pair ON compression_tokens(agent_a, agent_b);
"""


class SocietyStore:
    """
    Thread-safe SQLite store for all Agent Society data.

    Uses the same WAL + foreign_keys pragmas as SQLiteMemoryStore.
    Schema is managed via the shared migration system (migration #3).
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
            # Apply the main migrations (covers tables 1–2) then society tables
            from ..memory.migrations import migrate
            migrate(self._conn)
            self._ensure_society_schema()
        return self._conn

    def _ensure_society_schema(self) -> None:
        """Create society tables if they don't exist yet."""
        assert self._conn is not None
        self._conn.executescript(SOCIETY_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        with self._lock:
            if self._conn is not None:
                self._conn.close()
                self._conn = None

    # ------------------------------------------------------------------ #
    # Agent identities                                                     #
    # ------------------------------------------------------------------ #

    def save_identity(self, identity: AgentIdentity) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """
                INSERT OR REPLACE INTO agent_identities
                    (agent_id, name, agent_type, creator, xp,
                     traits_json, skill_names_json, created_at, last_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identity.agent_id,
                    identity.name,
                    identity.agent_type,
                    identity.creator,
                    identity.xp,
                    json.dumps(identity.traits),
                    json.dumps(identity.skill_names),
                    identity.created_at.isoformat(),
                    identity.last_active.isoformat(),
                ),
            )
            conn.commit()

    def get_identity(self, agent_id: str) -> AgentIdentity | None:
        with self._lock:
            conn = self._get_conn()
            row = conn.execute(
                "SELECT * FROM agent_identities WHERE agent_id = ?", (agent_id,)
            ).fetchone()
            if row is None:
                return None
            return self._row_to_identity(row)

    def get_identity_by_name(self, name: str) -> AgentIdentity | None:
        with self._lock:
            conn = self._get_conn()
            row = conn.execute(
                "SELECT * FROM agent_identities WHERE name = ?", (name,)
            ).fetchone()
            if row is None:
                return None
            return self._row_to_identity(row)

    def list_identities(self) -> list[AgentIdentity]:
        with self._lock:
            conn = self._get_conn()
            rows = conn.execute(
                "SELECT * FROM agent_identities ORDER BY xp DESC"
            ).fetchall()
            return [self._row_to_identity(r) for r in rows]

    def _row_to_identity(self, row: sqlite3.Row) -> AgentIdentity:
        return AgentIdentity(
            agent_id=row["agent_id"],
            name=row["name"],
            agent_type=row["agent_type"],
            creator=row["creator"],
            xp=row["xp"],
            traits=json.loads(row["traits_json"]),
            skill_names=json.loads(row["skill_names_json"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            last_active=datetime.fromisoformat(row["last_active"]),
        )

    def delete_identity(self, agent_id: str) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                "DELETE FROM agent_identities WHERE agent_id = ?", (agent_id,)
            )
            conn.commit()

    # ------------------------------------------------------------------ #
    # XP transactions                                                      #
    # ------------------------------------------------------------------ #

    def save_xp_transaction(self, tx: XPTransaction) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """
                INSERT INTO xp_transactions
                    (agent_id, event, amount, balance_after, context, occurred_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    tx.agent_id,
                    tx.event.value,
                    tx.amount,
                    tx.balance_after,
                    tx.context,
                    tx.occurred_at.isoformat(),
                ),
            )
            conn.commit()

    def get_xp_history(
        self, agent_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        with self._lock:
            conn = self._get_conn()
            rows = conn.execute(
                """
                SELECT * FROM xp_transactions
                WHERE agent_id = ?
                ORDER BY occurred_at DESC
                LIMIT ?
                """,
                (agent_id, limit),
            ).fetchall()
            return [dict(r) for r in rows]

    # ------------------------------------------------------------------ #
    # Relationships                                                        #
    # ------------------------------------------------------------------ #

    def save_relationship(self, rel: AgentRelationship) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """
                INSERT OR REPLACE INTO agent_relationships
                    (agent_id, peer_id, trust, collaboration_count,
                     success_count, last_interaction)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    rel.agent_id,
                    rel.peer_id,
                    rel.trust,
                    rel.collaboration_count,
                    rel.success_count,
                    rel.last_interaction.isoformat(),
                ),
            )
            conn.commit()

    def get_relationship(
        self, agent_id: str, peer_id: str
    ) -> AgentRelationship | None:
        with self._lock:
            conn = self._get_conn()
            row = conn.execute(
                "SELECT * FROM agent_relationships WHERE agent_id = ? AND peer_id = ?",
                (agent_id, peer_id),
            ).fetchone()
            if row is None:
                return None
            return self._row_to_relationship(row)

    def list_relationships(self, agent_id: str) -> list[AgentRelationship]:
        with self._lock:
            conn = self._get_conn()
            rows = conn.execute(
                """
                SELECT * FROM agent_relationships
                WHERE agent_id = ?
                ORDER BY trust DESC
                """,
                (agent_id,),
            ).fetchall()
            return [self._row_to_relationship(r) for r in rows]

    def all_relationships(self) -> list[AgentRelationship]:
        with self._lock:
            conn = self._get_conn()
            rows = conn.execute(
                "SELECT * FROM agent_relationships ORDER BY trust DESC"
            ).fetchall()
            return [self._row_to_relationship(r) for r in rows]

    def _row_to_relationship(self, row: sqlite3.Row) -> AgentRelationship:
        return AgentRelationship(
            agent_id=row["agent_id"],
            peer_id=row["peer_id"],
            trust=row["trust"],
            collaboration_count=row["collaboration_count"],
            success_count=row["success_count"],
            last_interaction=datetime.fromisoformat(row["last_interaction"]),
        )

    # ------------------------------------------------------------------ #
    # Skills                                                               #
    # ------------------------------------------------------------------ #

    def save_skill(self, agent_id: str, skill: Skill) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """
                INSERT OR REPLACE INTO skill_acquisitions
                    (agent_id, skill_name, proficiency, source,
                     use_count, acquired_at, last_used)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    agent_id,
                    skill.name,
                    skill.proficiency,
                    skill.source,
                    skill.use_count,
                    skill.acquired_at.isoformat(),
                    skill.last_used.isoformat(),
                ),
            )
            conn.commit()

    def get_skills(self, agent_id: str) -> list[Skill]:
        with self._lock:
            conn = self._get_conn()
            rows = conn.execute(
                "SELECT * FROM skill_acquisitions WHERE agent_id = ? ORDER BY proficiency DESC",
                (agent_id,),
            ).fetchall()
            return [self._row_to_skill(r) for r in rows]

    def _row_to_skill(self, row: sqlite3.Row) -> Skill:
        return Skill(
            name=row["skill_name"],
            proficiency=row["proficiency"],
            source=row["source"],
            use_count=row["use_count"],
            acquired_at=datetime.fromisoformat(row["acquired_at"]),
            last_used=datetime.fromisoformat(row["last_used"]),
        )

    # ------------------------------------------------------------------ #
    # Compression tokens                                                   #
    # ------------------------------------------------------------------ #

    def save_token(self, token: CompressionToken) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """
                INSERT OR REPLACE INTO compression_tokens
                    (token_id, agent_a, agent_b, concept, token,
                     use_count, is_active, last_used_cycle, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    token.token_id,
                    token.agent_a,
                    token.agent_b,
                    token.concept,
                    token.token,
                    token.use_count,
                    1 if token.is_active else 0,
                    token.last_used_cycle,
                    token.created_at.isoformat(),
                ),
            )
            conn.commit()

    def list_tokens(self, active_only: bool = False) -> list[CompressionToken]:
        with self._lock:
            conn = self._get_conn()
            query = "SELECT * FROM compression_tokens"
            if active_only:
                query += " WHERE is_active = 1"
            query += " ORDER BY use_count DESC"
            rows = conn.execute(query).fetchall()
            return [self._row_to_token(r) for r in rows]

    def _row_to_token(self, row: sqlite3.Row) -> CompressionToken:
        return CompressionToken(
            token_id=row["token_id"],
            agent_a=row["agent_a"],
            agent_b=row["agent_b"],
            concept=row["concept"],
            token=row["token"],
            use_count=row["use_count"],
            is_active=bool(row["is_active"]),
            last_used_cycle=row["last_used_cycle"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    # ------------------------------------------------------------------ #
    # Personality snapshots                                                #
    # ------------------------------------------------------------------ #

    def save_personality_snapshot(self, snapshot: PersonalitySnapshot) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """
                INSERT INTO personality_snapshots
                    (agent_id, traits_json, cycle, reason, recorded_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    snapshot.agent_id,
                    json.dumps(snapshot.traits),
                    snapshot.cycle,
                    snapshot.reason,
                    snapshot.recorded_at.isoformat(),
                ),
            )
            conn.commit()

    def get_personality_history(
        self, agent_id: str, limit: int = 50
    ) -> list[PersonalitySnapshot]:
        with self._lock:
            conn = self._get_conn()
            rows = conn.execute(
                """
                SELECT * FROM personality_snapshots
                WHERE agent_id = ?
                ORDER BY recorded_at ASC
                LIMIT ?
                """,
                (agent_id, limit),
            ).fetchall()
            return [
                PersonalitySnapshot(
                    agent_id=r["agent_id"],
                    traits=json.loads(r["traits_json"]),
                    cycle=r["cycle"],
                    reason=r["reason"],
                    recorded_at=datetime.fromisoformat(r["recorded_at"]),
                )
                for r in rows
            ]

    # ------------------------------------------------------------------ #
    # Reset                                                                #
    # ------------------------------------------------------------------ #

    def reset(self) -> None:
        """Wipe all society data. Irreversible — caller must confirm first."""
        with self._lock:
            conn = self._get_conn()
            for table in (
                "agent_identities",
                "agent_relationships",
                "xp_transactions",
                "skill_acquisitions",
                "compression_tokens",
                "personality_snapshots",
            ):
                conn.execute(f"DELETE FROM {table}")  # noqa: S608
            conn.commit()
        logger.info("Society data reset.")
