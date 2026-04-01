"""Version-based migration system for the SQLite memory store."""

from __future__ import annotations

import sqlite3
import logging

logger = logging.getLogger(__name__)

# Each entry: (version, description, sql)
MIGRATIONS: list[tuple[int, str, str]] = [
    (
        1,
        "initial schema",
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS debates (
            id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            winner TEXT NOT NULL DEFAULT '',
            winner_score REAL NOT NULL DEFAULT 0.0,
            rounds_json TEXT NOT NULL DEFAULT '[]',
            scores_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            debate_id TEXT NOT NULL REFERENCES debates(id),
            decision TEXT NOT NULL DEFAULT '',
            rationale TEXT NOT NULL DEFAULT '',
            confidence REAL NOT NULL DEFAULT 0.0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS learnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_name TEXT NOT NULL,
            pattern TEXT NOT NULL,
            insight TEXT NOT NULL,
            source_debate_id TEXT REFERENCES debates(id),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS agent_runs (
            id TEXT PRIMARY KEY,
            agent_name TEXT NOT NULL,
            inputs_json TEXT NOT NULL DEFAULT '{}',
            outputs_json TEXT NOT NULL DEFAULT '{}',
            duration_seconds REAL NOT NULL DEFAULT 0.0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            agent_name TEXT NOT NULL,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata_json TEXT NOT NULL DEFAULT '{}',
            access_count INTEGER NOT NULL DEFAULT 0,
            last_accessed TEXT NOT NULL DEFAULT (datetime('now')),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
            id UNINDEXED,
            topic,
            content,
            content='memories',
            content_rowid='rowid'
        );

        CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
            INSERT INTO memories_fts(rowid, id, topic, content)
            VALUES (new.rowid, new.id, new.topic, new.content);
        END;

        CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
            INSERT INTO memories_fts(memories_fts, rowid, id, topic, content)
            VALUES ('delete', old.rowid, old.id, old.topic, old.content);
        END;

        CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
            INSERT INTO memories_fts(memories_fts, rowid, id, topic, content)
            VALUES ('delete', old.rowid, old.id, old.topic, old.content);
            INSERT INTO memories_fts(rowid, id, topic, content)
            VALUES (new.rowid, new.id, new.topic, new.content);
        END;

        CREATE INDEX IF NOT EXISTS idx_debates_created ON debates(created_at);
        CREATE INDEX IF NOT EXISTS idx_learnings_agent ON learnings(agent_name);
        CREATE INDEX IF NOT EXISTS idx_agent_runs_agent ON agent_runs(agent_name);
        CREATE INDEX IF NOT EXISTS idx_memories_agent ON memories(agent_name);
        """,
    ),
    (
        2,
        "debate replay tables",
        """
        CREATE TABLE IF NOT EXISTS debate_sessions (
            id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            context TEXT NOT NULL DEFAULT '',
            options_json TEXT NOT NULL DEFAULT '[]',
            personas_json TEXT NOT NULL DEFAULT '[]',
            parent_debate_id TEXT,
            branch_round INTEGER,
            new_prompt TEXT,
            total_events INTEGER NOT NULL DEFAULT 0,
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS debate_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            debate_id TEXT NOT NULL REFERENCES debate_sessions(id),
            seq INTEGER NOT NULL,
            round_number INTEGER NOT NULL DEFAULT 0,
            persona TEXT NOT NULL DEFAULT '',
            event_kind TEXT NOT NULL,
            event_json TEXT NOT NULL,
            elapsed_ms INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_events_debate_seq ON debate_events(debate_id, seq);
        CREATE INDEX IF NOT EXISTS idx_sessions_parent ON debate_sessions(parent_debate_id);
        """,
    ),
    (
        3,
        "agent society tables",
        """
        CREATE TABLE IF NOT EXISTS agent_identities (
            agent_id         TEXT PRIMARY KEY,
            name             TEXT NOT NULL,
            agent_type       TEXT NOT NULL DEFAULT 'generic',
            creator          TEXT NOT NULL DEFAULT 'Steph',
            xp               INTEGER NOT NULL DEFAULT 0,
            traits_json      TEXT NOT NULL DEFAULT '{}',
            skill_names_json TEXT NOT NULL DEFAULT '[]',
            created_at       TEXT NOT NULL DEFAULT (datetime('now')),
            last_active      TEXT NOT NULL DEFAULT (datetime('now'))
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
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id      TEXT NOT NULL,
            event         TEXT NOT NULL,
            amount        INTEGER NOT NULL,
            balance_after INTEGER NOT NULL,
            context       TEXT NOT NULL DEFAULT '',
            occurred_at   TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS skill_acquisitions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id    TEXT NOT NULL,
            skill_name  TEXT NOT NULL,
            proficiency REAL NOT NULL DEFAULT 0.5,
            source      TEXT NOT NULL DEFAULT 'self',
            use_count   INTEGER NOT NULL DEFAULT 0,
            acquired_at TEXT NOT NULL DEFAULT (datetime('now')),
            last_used   TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS compression_tokens (
            token_id        TEXT PRIMARY KEY,
            agent_a         TEXT NOT NULL,
            agent_b         TEXT NOT NULL,
            concept         TEXT NOT NULL,
            token           TEXT NOT NULL,
            use_count       INTEGER NOT NULL DEFAULT 0,
            is_active       INTEGER NOT NULL DEFAULT 0,
            last_used_cycle INTEGER NOT NULL DEFAULT 0,
            created_at      TEXT NOT NULL DEFAULT (datetime('now'))
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
        """,
    ),
]


def _current_version(conn: sqlite3.Connection) -> int:
    try:
        row = conn.execute(
            "SELECT MAX(version) FROM schema_version"
        ).fetchone()
        return row[0] if row[0] is not None else 0
    except sqlite3.OperationalError:
        return 0


def migrate(conn: sqlite3.Connection) -> None:
    """Apply all pending migrations in order."""
    current = _current_version(conn)

    for version, description, sql in MIGRATIONS:
        if version <= current:
            continue

        logger.info("Applying migration %d: %s", version, description)
        # Execute each statement separately (sqlite3 doesn't support multiple statements in executescript inside a transaction)
        conn.executescript(sql)
        conn.execute(
            "INSERT INTO schema_version (version) VALUES (?)", (version,)
        )
        conn.commit()
        logger.info("Migration %d applied", version)
