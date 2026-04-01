"""Course builder agent — structures research findings into a learning path."""

from __future__ import annotations

from typing import Any

from ..core.agent import AgentResult, BaseAgent


class CourseBuilderAgent(BaseAgent):
    """
    Transforms research findings into a structured learning path:
    modules, lessons, exercises, and assessments.
    """

    name = "course_builder"

    @property
    def system_prompt(self) -> str:
        return (
            "You are a learning experience designer who specializes in technical education. "
            "You transform complex research into structured, progressive learning paths. "
            "Your curriculum designs are concrete, sequenced correctly (simple → complex), "
            "and always include hands-on exercises. You write for practitioners, not students."
        )

    async def run(self, subject: str, **_: Any) -> AgentResult:
        state = await self._state.get()

        context_parts = [f"Subject: {subject}"]
        if state.research and state.research.synthesis:
            context_parts.append(f"Research: {state.research.synthesis[:400]}")
        if state.patterns and state.patterns.recommendations:
            recs = "\n".join(f"• {r}" for r in state.patterns.recommendations[:5])
            context_parts.append(f"Key recommendations:\n{recs}")
        if state.debate and state.debate.decision:
            context_parts.append(f"Primary insight: {state.debate.decision[:300]}")

        context = "\n\n".join(context_parts)

        # Build the learning path structure
        structure_prompt = f"""{context}

---
Design a practical learning path for: {subject}

Create a 4-module course structure:

MODULE 1: Foundation (Week 1)
- Learning objectives (3)
- Core concepts (3-4)
- Hands-on exercise

MODULE 2: Core Skills (Week 2-3)
- Learning objectives (3)
- Core concepts (3-4)
- Hands-on exercise

MODULE 3: Advanced Application (Week 4-5)
- Learning objectives (3)
- Core concepts (3-4)
- Hands-on exercise

MODULE 4: Mastery Project (Week 6)
- Capstone project description
- Success criteria
- Extension challenges

PREREQUISITES: <what the learner needs before starting>
TARGET AUDIENCE: <who this is for>
TIME COMMITMENT: <hours/week>"""

        course_text = await self._llm([{"role": "user", "content": structure_prompt}])

        course = {
            "subject": subject,
            "raw_structure": course_text,
            "modules": self._parse_modules(course_text),
        }

        await self._state.update(course=course)

        return AgentResult(
            agent_name=self.name,
            success=True,
            output=course,
        )

    def _parse_modules(self, text: str) -> list[dict[str, str]]:
        modules: list[dict[str, str]] = []
        current: dict[str, str] = {}

        for line in text.split("\n"):
            stripped = line.strip()
            if stripped.upper().startswith("MODULE") and ":" in stripped:
                if current:
                    modules.append(current)
                title = stripped.split(":", 1)[1].strip()
                current = {"title": title, "content": ""}
            elif current:
                current["content"] = current.get("content", "") + line + "\n"

        if current:
            modules.append(current)

        return modules
