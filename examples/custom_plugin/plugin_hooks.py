"""
Lifecycle hooks for the sentiment-analyzer plugin.

These are referenced in plugin.yaml and fired by the Orchestrator.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def setup(**kwargs: object) -> None:
    """before_run hook — called before any agent runs."""
    subject = kwargs.get("subject", "")
    logger.info("[sentiment-analyzer] before_run: preparing for subject=%r", subject)


async def cleanup(**kwargs: object) -> None:
    """after_run hook — called after all agents complete."""
    run_id = kwargs.get("run_id", "")
    logger.info("[sentiment-analyzer] after_run: run %r complete", run_id)
