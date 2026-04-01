"""Lightweight aiohttp server: serves static UI and REST/WebSocket API."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from aiohttp import web

from .api import routes, KEY_API_KEY, KEY_MODEL, KEY_DB_PATH

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"


async def _handle_index(request: web.Request) -> web.FileResponse:
    return web.FileResponse(STATIC_DIR / "index.html")


async def create_app(
    api_key: str = "",
    model: str = "claude-opus-4-6",
    db_path: str = ".crucible_memory.db",
) -> web.Application:
    app = web.Application()
    app[KEY_API_KEY] = api_key
    app[KEY_MODEL] = model
    app[KEY_DB_PATH] = db_path

    app.router.add_get("/", _handle_index)
    app.router.add_routes(routes)
    app.router.add_static("/static", STATIC_DIR)

    return app


async def run_server(
    port: int = 8420,
    api_key: str = "",
    model: str = "claude-opus-4-6",
    db_path: str = ".crucible_memory.db",
) -> None:
    app = await create_app(api_key=api_key, model=model, db_path=db_path)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", port)
    await site.start()

    print(f"\n  Crucible Web UI → http://localhost:{port}\n  Press Ctrl+C to stop\n")
    logger.info("Web server started on port %d", port)

    try:
        await asyncio.sleep(float("inf"))
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass
    finally:
        await runner.cleanup()
