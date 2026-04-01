"""Visualizer agent — creates Mermaid diagrams and visual maps from research findings."""

from __future__ import annotations

from typing import Any

from ..core.agent import AgentResult, BaseAgent


class VisualizerAgent(BaseAgent):
    """
    Generates Mermaid diagrams, ASCII maps, and structured visual representations
    of research findings. Outputs are stored in state.visualizations.
    """

    name = "visualizer"

    @property
    def system_prompt(self) -> str:
        return (
            "You are a technical visualization expert who translates complex analysis "
            "into clear Mermaid diagrams, mind maps, and structured visual artifacts. "
            "Your diagrams are syntactically correct and immediately renderable. "
            "Always output valid Mermaid syntax. No prose in diagram blocks."
        )

    async def run(self, subject: str, **_: Any) -> AgentResult:
        state = await self._state.get()
        visualizations: list[dict[str, Any]] = []

        # 1. Architecture diagram if we have scan data
        if state.scan and state.scan.structure:
            arch_diagram = await self._generate_architecture_diagram(state.scan)
            if arch_diagram:
                visualizations.append({
                    "type": "mermaid",
                    "title": "Codebase Architecture",
                    "content": arch_diagram,
                })

        # 2. Debate outcome visualization
        if state.debate and state.debate.scores:
            debate_diagram = self._generate_debate_chart(state.debate)
            visualizations.append({
                "type": "mermaid",
                "title": "Debate Council Scores",
                "content": debate_diagram,
            })

        # 3. Research mindmap
        if state.research and state.research.findings:
            mindmap = await self._generate_mindmap(subject, state.research.findings)
            visualizations.append({
                "type": "mermaid",
                "title": "Research Mind Map",
                "content": mindmap,
            })

        # 4. Pattern landscape
        if state.patterns and state.patterns.patterns:
            pattern_viz = await self._generate_pattern_diagram(
                state.patterns.patterns, state.patterns.anti_patterns
            )
            visualizations.append({
                "type": "mermaid",
                "title": "Pattern Landscape",
                "content": pattern_viz,
            })

        state_snapshot = await self._state.get()
        existing = state_snapshot.visualizations or []

        await self._state.update(visualizations=existing + visualizations)

        return AgentResult(
            agent_name=self.name,
            success=True,
            output={"count": len(visualizations), "visualizations": visualizations},
        )

    async def _generate_architecture_diagram(self, scan: Any) -> str:
        dirs = scan.structure.get("root_dirs", [])[:8]
        files = scan.structure.get("root_files", [])[:6]

        langs = list(scan.languages.keys())[:4]
        lang_str = ", ".join(langs)

        prompt = f"""Generate a Mermaid graph TD diagram showing the high-level architecture of a codebase.

Root directories: {dirs}
Root files: {files}
Primary languages: {lang_str}
Summary: {scan.summary[:300]}

Rules:
- Use graph TD syntax
- Show only the most important 6-10 nodes
- Group by concern (src, tests, config, docs, etc.)
- Use descriptive edge labels
- Valid Mermaid syntax ONLY, no markdown fences"""

        return await self._llm([{"role": "user", "content": prompt}])

    def _generate_debate_chart(self, debate: Any) -> str:
        scores = debate.scores
        bars = "\n".join(
            f'    {name}["{name.title()}: {score:.1f}"]'
            for name, score in sorted(scores.items(), key=lambda x: -x[1])
        )
        winner_node = f'    {debate.winner}["{debate.winner.title()}: {debate.winner_score:.1f} 🏆"]'
        return f"""graph LR
    title["{debate.topic[:50]}..."]
{bars}"""

    async def _generate_mindmap(self, subject: str, findings: list[str]) -> str:
        findings_text = "\n".join(f"- {f[:100]}" for f in findings[:6])
        prompt = f"""Generate a Mermaid mindmap for this research topic.

Subject: {subject}
Key findings:
{findings_text}

Rules:
- Use mindmap syntax
- Root node is the subject
- 3-5 main branches from key findings
- 2-3 sub-nodes per branch maximum
- Valid Mermaid mindmap syntax ONLY"""

        return await self._llm([{"role": "user", "content": prompt}])

    async def _generate_pattern_diagram(
        self, patterns: list[Any], anti_patterns: list[Any]
    ) -> str:
        p_names = [p.get("name", str(p))[:40] for p in patterns[:4]]
        ap_names = [ap.get("name", str(ap))[:40] for ap in anti_patterns[:4]]

        prompt = f"""Generate a Mermaid flowchart showing patterns vs anti-patterns.

Patterns (good): {p_names}
Anti-patterns (avoid): {ap_names}

Create a quadrant-style graph TD showing:
- Left side: patterns to adopt
- Right side: anti-patterns to avoid
- Connect related patterns/anti-patterns with labeled edges

Valid Mermaid graph TD syntax ONLY."""

        return await self._llm([{"role": "user", "content": prompt}])
