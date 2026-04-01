"""REST + WebSocket API handlers for the debate web UI."""

from __future__ import annotations

import asyncio
import json
import logging
import sqlite3
import uuid
from dataclasses import asdict
from typing import Any

from aiohttp import web, WSMsgType

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

# Typed app keys — avoid string-key warnings
KEY_API_KEY: web.AppKey[str] = web.AppKey("api_key")
KEY_MODEL: web.AppKey[str] = web.AppKey("model")
KEY_DB_PATH: web.AppKey[str] = web.AppKey("db_path")

# In-memory live debate registry: debate_id -> list of subscriber queues
_live_debates: dict[str, list[asyncio.Queue[Any]]] = {}


# ------------------------------------------------------------------ #
# DB helpers (read-only, no external deps beyond sqlite3)             #
# ------------------------------------------------------------------ #

def _db_list_debates(db_path: str, limit: int = 100) -> list[dict[str, Any]]:
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, topic, winner, winner_score, scores_json, created_at
            FROM debates ORDER BY created_at DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        conn.close()
    except sqlite3.OperationalError:
        return []
    return [
        {
            "id": r["id"],
            "topic": r["topic"],
            "winner": r["winner"],
            "winner_score": r["winner_score"],
            "scores": json.loads(r["scores_json"] or "{}"),
            "created_at": r["created_at"],
        }
        for r in rows
    ]


def _db_get_debate(db_path: str, debate_id: str) -> dict[str, Any] | None:
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT id, topic, winner, winner_score, rounds_json, scores_json, created_at
            FROM debates WHERE id = ?
            """,
            (debate_id,),
        ).fetchone()
        conn.close()
    except sqlite3.OperationalError:
        return None
    if not row:
        return None
    return {
        "id": row["id"],
        "topic": row["topic"],
        "winner": row["winner"],
        "winner_score": row["winner_score"],
        "rounds": json.loads(row["rounds_json"] or "[]"),
        "scores": json.loads(row["scores_json"] or "{}"),
        "created_at": row["created_at"],
    }


# ------------------------------------------------------------------ #
# REST endpoints                                                       #
# ------------------------------------------------------------------ #

@routes.get("/api/debates")
async def list_debates(request: web.Request) -> web.Response:
    db_path: str = request.app[KEY_DB_PATH]
    loop = asyncio.get_running_loop()
    debates = await loop.run_in_executor(None, _db_list_debates, db_path)
    return web.json_response({"debates": debates})


@routes.get("/api/debates/{id}")
async def get_debate(request: web.Request) -> web.Response:
    db_path: str = request.app[KEY_DB_PATH]
    debate_id = request.match_info["id"]
    loop = asyncio.get_running_loop()
    debate = await loop.run_in_executor(None, _db_get_debate, db_path, debate_id)
    if debate is None:
        raise web.HTTPNotFound(reason="Debate not found")
    return web.json_response(debate)


@routes.post("/api/debates")
async def start_debate(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except Exception:
        raise web.HTTPBadRequest(reason="Invalid JSON body")

    topic = (data.get("topic") or "").strip()
    if not topic:
        raise web.HTTPBadRequest(reason="'topic' is required")

    api_key: str = request.app[KEY_API_KEY]
    if not api_key:
        raise web.HTTPServiceUnavailable(reason="No API key configured; start server with --api-key")

    model: str = request.app[KEY_MODEL]
    db_path: str = request.app[KEY_DB_PATH]
    debate_id = str(uuid.uuid4())
    context: str = data.get("context") or ""
    options: list[str] = data.get("options") or []

    _live_debates[debate_id] = []

    asyncio.create_task(
        _run_live_debate(debate_id, topic, context, options, api_key, model, db_path)
    )

    return web.json_response({"debate_id": debate_id, "status": "started"}, status=202)


# ------------------------------------------------------------------ #
# WebSocket live stream                                                #
# ------------------------------------------------------------------ #

@routes.get("/ws/debate/{id}")
async def ws_debate(request: web.Request) -> web.WebSocketResponse:
    debate_id = request.match_info["id"]
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    if debate_id not in _live_debates:
        await ws.send_json({"kind": "error", "message": "Debate not found or already finished"})
        await ws.close()
        return ws

    queue: asyncio.Queue[Any] = asyncio.Queue()
    _live_debates[debate_id].append(queue)

    async def _reader() -> None:
        """Drain incoming WS messages (ping/close frames)."""
        async for msg in ws:
            if msg.type in (WSMsgType.ERROR, WSMsgType.CLOSE):
                break

    reader_task = asyncio.create_task(_reader())

    try:
        while True:
            event = await queue.get()
            if event is None:  # sentinel — debate finished
                break
            if ws.closed:
                break
            await ws.send_json(event)
    finally:
        reader_task.cancel()
        if debate_id in _live_debates and queue in _live_debates[debate_id]:
            _live_debates[debate_id].remove(queue)

    if not ws.closed:
        await ws.close()
    return ws


# ------------------------------------------------------------------ #
# Background debate runner                                            #
# ------------------------------------------------------------------ #

async def _run_live_debate(
    debate_id: str,
    topic: str,
    context: str,
    options: list[str],
    api_key: str,
    model: str,
    db_path: str,
) -> None:
    import anthropic
    from ..streaming.stream import DebateStream
    from ..memory.sqlite_store import SQLiteMemoryStore

    client = anthropic.AsyncAnthropic(api_key=api_key)
    stream = DebateStream(client=client, model=model)

    rounds: list[dict[str, Any]] = [
        {"round": 1, "statements": []},
        {"round": 2, "statements": []},
        {"round": 3, "statements": []},
    ]
    scores: dict[str, float] = {}
    winner = ""
    winner_score = 0.0

    async def _broadcast(event_data: dict[str, Any]) -> None:
        subscribers = _live_debates.get(debate_id, [])
        for q in list(subscribers):
            await q.put(event_data)

    try:
        async for event in stream.run(topic=topic, context=context, options=options):
            event_data = asdict(event)

            # Collect rounds for DB persistence
            kind = event_data.get("kind", "")
            if kind in ("argument_submitted", "cross_examination"):
                rn = event_data.get("round", 1) - 1
                if 0 <= rn <= 2:
                    rounds[rn]["statements"].append({
                        "persona": event_data.get("persona_name", ""),
                        "content": event_data.get("content", ""),
                        "targets": event_data.get("targets", []),
                    })
            elif kind == "scoring_complete":
                scores = event_data.get("scores", {})
            elif kind == "winner_declared":
                winner = event_data.get("winner", "")
                winner_score = event_data.get("winner_score", 0.0)

            await _broadcast(event_data)

        # Persist to DB
        store = SQLiteMemoryStore(db_path=db_path)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: store.save_debate(
                debate_id=debate_id,
                topic=topic,
                rounds=rounds,
                winner=winner,
                scores=scores,
            ),
        )
        logger.info("Debate %s saved to DB (winner: %s, score: %.1f)", debate_id, winner, winner_score)

    except Exception as exc:
        logger.exception("Live debate %s failed: %s", debate_id, exc)
        await _broadcast({"kind": "error", "message": str(exc)})
    finally:
        # Send sentinel to all waiting subscribers
        for q in list(_live_debates.get(debate_id, [])):
            await q.put(None)
        _live_debates.pop(debate_id, None)
