"""Tests for the web UI server, REST API, and WebSocket endpoint."""

from __future__ import annotations

import asyncio
import json
import sqlite3
import tempfile
import uuid
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from crucible.web.api import _db_get_debate, _db_list_debates, routes
from crucible.web.server import create_app


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_db(tmp_path: Path) -> str:
    """Create a minimal SQLite DB with the debates schema."""
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE debates (
            id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            winner TEXT NOT NULL DEFAULT '',
            winner_score REAL NOT NULL DEFAULT 0.0,
            rounds_json TEXT NOT NULL DEFAULT '[]',
            scores_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()
    return db_path


def _insert_debate(db_path: str, debate_id: str, topic: str, winner: str,
                   winner_score: float, rounds: list, scores: dict) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO debates (id, topic, winner, winner_score, rounds_json, scores_json) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (debate_id, topic, winner, winner_score,
         json.dumps(rounds), json.dumps(scores)),
    )
    conn.commit()
    conn.close()


@pytest.fixture
async def client(tmp_db: str) -> TestClient:
    app = await create_app(api_key="test-key", db_path=tmp_db)
    server = TestServer(app)
    client = TestClient(server)
    await client.start_server()
    yield client
    await client.close()


# ─── DB helper tests ──────────────────────────────────────────────────────────

def test_db_list_debates_empty(tmp_db: str) -> None:
    result = _db_list_debates(tmp_db)
    assert result == []


def test_db_list_debates_returns_rows(tmp_db: str) -> None:
    _insert_debate(tmp_db, "d1", "Topic A", "pragmatist", 7.5,
                   [], {"pragmatist": 7.5, "skeptic": 6.0})
    _insert_debate(tmp_db, "d2", "Topic B", "visionary", 8.1,
                   [], {"visionary": 8.1})
    rows = _db_list_debates(tmp_db)
    assert len(rows) == 2
    assert rows[0]["topic"] in ("Topic A", "Topic B")


def test_db_get_debate_found(tmp_db: str) -> None:
    rounds = [{"round": 1, "statements": [{"persona": "pragmatist", "content": "Hello", "targets": []}]}]
    _insert_debate(tmp_db, "d1", "My topic", "skeptic", 6.5, rounds, {"skeptic": 6.5})
    result = _db_get_debate(tmp_db, "d1")
    assert result is not None
    assert result["topic"] == "My topic"
    assert result["winner"] == "skeptic"
    assert len(result["rounds"]) == 1


def test_db_get_debate_not_found(tmp_db: str) -> None:
    result = _db_get_debate(tmp_db, "nonexistent")
    assert result is None


def test_db_list_debates_missing_file() -> None:
    result = _db_list_debates("/tmp/does_not_exist_crucible.db")
    assert result == []


# ─── REST API tests ───────────────────────────────────────────────────────────

async def test_get_debates_empty(client: TestClient) -> None:
    resp = await client.get("/api/debates")
    assert resp.status == 200
    data = await resp.json()
    assert data["debates"] == []


async def test_get_debates_with_data(client: TestClient, tmp_db: str) -> None:
    _insert_debate(tmp_db, "abc", "Debate topic", "pragmatist", 7.0,
                   [], {"pragmatist": 7.0})
    resp = await client.get("/api/debates")
    assert resp.status == 200
    data = await resp.json()
    assert len(data["debates"]) == 1
    assert data["debates"][0]["id"] == "abc"
    assert data["debates"][0]["topic"] == "Debate topic"


async def test_get_debate_by_id(client: TestClient, tmp_db: str) -> None:
    rounds = [{"round": 1, "statements": []}]
    _insert_debate(tmp_db, "xyz", "Some topic", "visionary", 8.5,
                   rounds, {"visionary": 8.5})
    resp = await client.get("/api/debates/xyz")
    assert resp.status == 200
    data = await resp.json()
    assert data["id"] == "xyz"
    assert data["winner"] == "visionary"
    assert data["rounds"] == rounds


async def test_get_debate_not_found(client: TestClient) -> None:
    resp = await client.get("/api/debates/doesnotexist")
    assert resp.status == 404


async def test_post_debate_missing_topic(client: TestClient) -> None:
    resp = await client.post("/api/debates", json={})
    assert resp.status == 400


async def test_post_debate_no_api_key(tmp_db: str) -> None:
    """Server without API key should return 503 when starting a debate."""
    app = await create_app(api_key="", db_path=tmp_db)
    server = TestServer(app)
    c = TestClient(server)
    await c.start_server()
    try:
        resp = await c.post("/api/debates", json={"topic": "Test topic"})
        assert resp.status == 503
    finally:
        await c.close()


async def test_post_debate_starts_background_task(client: TestClient) -> None:
    """POST /api/debates with a valid key returns 202 and a debate_id."""
    with patch("crucible.web.api._run_live_debate", new_callable=AsyncMock) as mock_run:
        # Prevent the real background task from actually running
        mock_run.return_value = None

        resp = await client.post("/api/debates", json={"topic": "Is async better?"})
        assert resp.status == 202
        data = await resp.json()
        assert "debate_id" in data
        assert data["status"] == "started"


# ─── Static file serving ──────────────────────────────────────────────────────

async def test_index_html_served(client: TestClient) -> None:
    resp = await client.get("/")
    assert resp.status == 200
    content_type = resp.headers.get("Content-Type", "")
    assert "text/html" in content_type


async def test_static_js_served(client: TestClient) -> None:
    resp = await client.get("/static/app.js")
    assert resp.status == 200
    ct = resp.headers.get("Content-Type", "")
    assert "javascript" in ct


async def test_static_css_served(client: TestClient) -> None:
    resp = await client.get("/static/styles.css")
    assert resp.status == 200
    ct = resp.headers.get("Content-Type", "")
    assert "css" in ct


# ─── WebSocket tests ──────────────────────────────────────────────────────────

async def test_ws_unknown_debate(client: TestClient) -> None:
    """WebSocket to an unknown debate_id should receive an error message and close."""
    async with client.ws_connect("/ws/debate/unknown-id") as ws:
        msg = await ws.receive_json()
        assert msg["kind"] == "error"


async def test_ws_receives_events(client: TestClient) -> None:
    """WebSocket subscriber receives broadcast events from a live debate."""
    from crucible.web.api import _live_debates

    debate_id = str(uuid.uuid4())
    _live_debates[debate_id] = []

    async with client.ws_connect(f"/ws/debate/{debate_id}") as ws:
        # Brief pause to let subscriber register
        await asyncio.sleep(0.05)

        # Simulate broadcasting one event then sentinel
        subscribers = _live_debates.get(debate_id, [])
        assert len(subscribers) == 1

        await subscribers[0].put({"kind": "debate_started", "topic": "Live test", "context": "", "options": []})
        await subscribers[0].put(None)  # sentinel

        msg = await ws.receive_json()
        assert msg["kind"] == "debate_started"
        assert msg["topic"] == "Live test"
