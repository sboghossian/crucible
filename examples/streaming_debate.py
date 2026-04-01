"""
Example: Streaming Debate — watch the debate unfold in real-time.

Runs an adversarial Debate Council on "Should we use microservices or monolith?"
and renders each event live in the terminal using Rich.

Usage:
    python examples/streaming_debate.py

Requires ANTHROPIC_API_KEY to be set.
"""

from __future__ import annotations

import asyncio
import os
import sys

# Allow running from repo root without installing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import anthropic
from rich.console import Console

from crucible.streaming import DebateRenderer
from crucible.streaming.stream import DebateStream

TOPIC = "Should we use microservices or a monolith for our new product?"

OPTIONS = [
    "Go with a monolith — ship fast, extract later if needed",
    "Go with microservices — design for scale from day one",
    "Modular monolith — best of both worlds",
]

CONTEXT = """
We are a 6-person startup with 2 backend engineers. Our product is an early-stage
B2B SaaS with ~50 beta customers. We expect 10x growth over the next 12 months.
Our team has strong monolith experience but limited microservices operational experience.
"""


async def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    console = Console()
    client = anthropic.AsyncAnthropic(api_key=api_key)
    stream = DebateStream(client=client, model="claude-opus-4-6")
    renderer = DebateRenderer(console=console)

    async for event in stream.run(topic=TOPIC, context=CONTEXT, options=OPTIONS):
        renderer.render(event)


if __name__ == "__main__":
    asyncio.run(main())
