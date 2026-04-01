"""GitHub optimization agent — generates star-worthy README, badges, and release notes."""

from __future__ import annotations

from typing import Any

from ..core.agent import AgentResult, BaseAgent


class PublisherAgent(BaseAgent):
    """
    Optimizes a project for GitHub discoverability and community adoption.
    Generates README sections, topic tags, release notes, and contribution guides.
    """

    name = "publisher"

    @property
    def system_prompt(self) -> str:
        return (
            "You are a developer relations expert who has grown multiple open-source projects "
            "to thousands of GitHub stars. You understand what makes developers stop scrolling "
            "and actually star a repo. Your READMEs have strong hooks, clear value propositions, "
            "and make the first contribution feel achievable. You write for skimmers first, "
            "then for deep readers. You avoid marketing fluff — concrete beats abstract."
        )

    async def run(self, subject: str, **_: Any) -> AgentResult:
        state = await self._state.get()

        context_parts = [f"Project: {subject}"]
        if state.research and state.research.synthesis:
            context_parts.append(f"Research: {state.research.synthesis[:300]}")
        if state.debate and state.debate.decision:
            context_parts.append(f"Core value proposition: {state.debate.decision[:200]}")
        if state.patterns and state.patterns.recommendations:
            context_parts.append(
                "Key differentiators:\n" +
                "\n".join(f"• {r}" for r in state.patterns.recommendations[:3])
            )

        context = "\n\n".join(context_parts)

        # GitHub topics/tags
        tags_prompt = f"""{context}

Generate 10 optimal GitHub topic tags for this project.
Rules:
- Use lowercase, hyphen-separated
- Mix: technology tags + use-case tags + audience tags
- Avoid generic tags (python, javascript, etc.) unless highly specific
Output as comma-separated list only."""

        tags_text = await self._llm(
            [{"role": "user", "content": tags_prompt}], max_tokens=200
        )
        topics = [t.strip() for t in tags_text.split(",") if t.strip()][:10]

        # README hero section
        readme_prompt = f"""{context}

Write the hero section of a GitHub README (everything above the first horizontal rule).

Must include:
1. One-line description that captures the unique value
2. 3-4 badge placeholders (format: ![Badge Name](badge_url))
3. A 2-3 sentence problem statement (why does this exist?)
4. A 3-sentence "what it does" (solution, not features)
5. A "Quick Start" section with exactly 3 commands that get someone running

Tone: direct, technical, no marketing fluff. Write for a senior engineer who is skeptical."""

        readme_hero = await self._llm([{"role": "user", "content": readme_prompt}])

        # Release notes template
        release_notes_prompt = f"""For project: {subject}

Write a v0.1.0 release announcement (GitHub Releases format).
Include:
- What's new (3-5 bullet points)
- Breaking changes section (empty for v0.1.0)
- Installation instructions
- What's next (v0.2.0 preview)

Keep it under 300 words. Technical audience."""

        release_notes = await self._llm(
            [{"role": "user", "content": release_notes_prompt}], max_tokens=600
        )

        github_report = {
            "topics": topics,
            "readme_hero": readme_hero,
            "release_notes": release_notes,
        }

        await self._state.update(github_report=github_report)

        return AgentResult(
            agent_name=self.name,
            success=True,
            output=github_report,
        )
