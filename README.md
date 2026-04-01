# Crucible

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/crucible-ai.svg)](https://pypi.org/project/crucible-ai/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![GitHub Stars](https://img.shields.io/github/stars/sboghossian/crucible?style=social)](https://github.com/sboghossian/crucible)

**Most multi-agent frameworks are demos. Crucible is a research instrument.**

Every decision — naming, architecture, prioritization, interpretation — goes through a 4-persona adversarial Debate Council before anything happens. No consensus by default. The best argument wins.

---

## Why Crucible?

Multi-agent AI systems have a sycophancy problem. Agents agree with each other. They share the same model, similar priors, and no mechanism for adversarial challenge. You get fast answers, not rigorous ones.

**The empirical case for adversarial review:**
- METR (2026): developers using AI tools are 19% *slower* while believing they're 20% faster — consensus-based tools optimize for feeling, not accuracy
- Devin achieves 67% PR merge rate on precise tasks but drops to ~15% on ambiguous ones — the failure mode is silent confident-wrong, not loud uncertain
- Sonar (2025): AI coding tools without governance increase code issues 1.7x; *with* governance they decrease 0.3x

Research requires pressure. Metal is tested in a crucible. So are ideas.

---

## Quick Start

Three commands to a working debate:

```bash
pip install crucible-ai
export ANTHROPIC_API_KEY=sk-ant-...
python -c "
import asyncio
from crucible import Orchestrator

async def main():
    orch = Orchestrator()
    result = await orch.standalone_debate(
        topic='Should we migrate to a microservices architecture?',
        options=['yes, now', 'no, stay monolith', 'gradual strangler fig pattern'],
        context='We have 3 engineers and 50k DAU. Our monolith is 4 years old.'
    )
    print(f'Winner: {result.winner} ({result.winner_score:.1f}/10)')
    print(result.decision)
    print(f'Dissent: {result.dissenting_views}')

asyncio.run(main())
"
```

---

## The Debate Council

The crown jewel. Four personas. One topic. Three rounds. The best argument wins.

| Persona | Structural Bias | Weights Highest |
|---|---|---|
| **The Pragmatist** | Implementation feasibility first | Practical feasibility (40%) |
| **The Visionary** | Transformative potential first | Novelty & upside (45%) |
| **The Skeptic** | Evidence quality first | Evidence rigor (45%) |
| **The User Advocate** | Human experience first | Adoption & clarity (35%) |

**Round 1 — Opening Statements:** Each persona presents their position independently (parallel LLM calls, no anchoring).

**Round 2 — Cross-Examination:** Each persona challenges the two weakest arguments from the others.

**Round 3 — Closing Arguments:** Each persona refines their position. Intellectual honesty is rewarded — acknowledging valid challenges is scored higher than repeating Round 1.

**Scoring:** Evidence quality × logical consistency × practical feasibility × novelty. The winner's position becomes the decision. All arguments and scores are logged. Dissent is preserved.

### A Real Debate: Naming This Framework

The Debate Council named Crucible. Here's the abridged transcript:

```
TOPIC: What should this multi-agent research framework be named?
OPTIONS: crucible, forge, tribunal, assay, crucis

[PRAGMATIST — OPENING]
"Crucible wins on implementability: it's memorable, already a common English word
with strong connotations, lowercase-safe as a package name, and not taken on PyPI.
Forge is too generic (already used by multiple projects). Tribunal implies judgment
but not refinement. Assay is too obscure."

[VISIONARY — CROSS-EXAMINATION]
"The Pragmatist focuses only on present-tense naming constraints. The long-term
question is what this name enables — Crucible implies transformation through pressure,
which is exactly what adversarial multi-agent research is. I challenge Assay:
it's scientifically precise but will be mispronounced and misunderstood."

[SKEPTIC — CROSS-EXAMINATION]
"Citing evidence: GitHub repos named after metallurgical processes (forge, anvil, foundry)
have lower star counts than abstract but resonant names. Crucible is the exception
because it has natural language salience. However: is PyPI availability confirmed?
What's the evidence this won't conflict with existing tooling?"

[USER ADVOCATE — CLOSING]
"Closing argument: Crucible. Users searching for 'AI research framework' will
land on a name they can pronounce, remember, and explain to teammates in one sentence:
'It's called Crucible because ideas get tested under pressure.' That sentence writes itself."

WINNER: pragmatist (7.8/10)
DECISION: Crucible — pragmatic, memorable, available, and metaphorically precise.
```

This debate happens for **every decision**: project structure, agent ordering, output formats, KPIs.

---

## Architecture

```mermaid
graph TD
    User([User / CLI]) --> Orch[Orchestrator]

    Orch -->|Phase 1: parallel| Scanner[Scanner Agent]
    Orch -->|Phase 1: parallel| Research[Research Agent]

    Scanner --> State[(Shared State)]
    Research --> State

    State --> PatternAnalyst[Pattern Analyst]
    PatternAnalyst --> State

    State -->|every decision| DC{Debate Council}
    DC --> Pragmatist[The Pragmatist]
    DC --> Visionary[The Visionary]
    DC --> Skeptic[The Skeptic]
    DC --> UserAdvocate[The User Advocate]

    Pragmatist -->|Round 1| R1[Opening Statements]
    Visionary --> R1
    Skeptic --> R1
    UserAdvocate --> R1

    R1 --> R2[Cross-Examination]
    R2 --> R3[Closing Arguments]
    R3 --> Resolver[Resolver: score + pick winner]

    Resolver --> State

    State -->|Phase 4: parallel| Forecaster[Forecaster]
    State -->|Phase 4: parallel| Visualizer[Visualizer]

    Forecaster --> State
    Visualizer --> State

    State --> CourseBuilder[Course Builder]
    State --> Publisher[Publisher / GitHub optimizer]

    Bus([Event Bus]) -.->|all events| Learning[Learning Agent]
    Learning -.-> Memory[(Persistent Memory)]

    style DC fill:#ff6b6b,color:#fff
    style Resolver fill:#ee5a24,color:#fff
    style Bus fill:#686de0,color:#fff
    style Learning fill:#686de0,color:#fff
```

---

## Feature Highlights

### Debate Council
Four AI personas with structural biases argue adversarially across three rounds. Every decision fork goes through the council. Close margins (< 0.5 score gap) are flagged — genuine uncertainty shouldn't produce false confidence.

### Agent Society (Research Preview)
Persistent agent identities with episodic memory, personality traits (drift capped at 0.02/cycle), and an XP economy where teaching pays 20 XP vs. learning 5 XP. Emergent compression tokens develop between agent pairs. Safety enforced as physics, not policy.

### Learning Agent
A passive observer on the event bus. Distills meta-patterns from all agent outputs. Builds up cross-run institutional knowledge.

### Full Audit Trail
Every agent output, every debate round, every scoring decision is logged and preserved. Dissenting views are not discarded. A close debate (7.1 vs. 6.9) is structurally different from a blowout (9.2 vs. 4.1) — that information is kept.

---

## Agent Reference

| Agent | What it does |
|---|---|
| **Scanner** | Analyzes a git repo: languages, structure, dependencies, git stats, LLM synthesis |
| **Research** | Synthesizes topic knowledge into structured findings with confidence scores |
| **Pattern Analyst** | Finds recurring patterns and anti-patterns across projects |
| **Debate Council** | 4 personas, 3 rounds, adversarial scoring — for every decision |
| **Learning** | Passive observer; distills meta-patterns from all agent outputs |
| **Visualizer** | Generates Mermaid diagrams from findings (architecture, debates, mindmaps) |
| **Forecaster** | Probabilistic predictions with reference classes and disconfirming evidence |
| **Course Builder** | Structures findings into a learning path |
| **Publisher** | GitHub optimization: topics, README hero, release notes |

---

## The `standalone_debate()` Method

Any decision. Any context. Three lines.

```python
from crucible import Orchestrator

orch = Orchestrator()

# Architecture decision
result = await orch.standalone_debate(
    topic="How should we store agent outputs?",
    options=["SQLite", "JSON files", "PostgreSQL", "in-memory only"],
    context="MVP with <100 concurrent runs, need to add persistence later."
)

# Prioritization decision
result = await orch.standalone_debate(
    topic="Which feature should we build next?",
    options=["web UI", "streaming output", "plugin API", "better caching"],
)

print(f"Winner: {result.winner}")
print(f"Score: {result.winner_score:.1f}/10")
print(f"Decision: {result.decision}")
print(f"Dissent: {result.dissenting_views}")
```

---

## Installation

```bash
pip install crucible-ai          # from PyPI
pip install -e ".[dev]"          # development install with test dependencies
```

**Requirements:** Python 3.11+, Anthropic API key

---

## Running Tests

```bash
pytest tests/ -v
pytest tests/test_debate_council.py -v   # just the debate tests
pytest tests/ -m "not api"               # skip tests that make real API calls
```

---

## Configuration

```python
from crucible import Orchestrator

orch = Orchestrator(
    api_key="sk-ant-...",          # or ANTHROPIC_API_KEY env var
    model="claude-opus-4-6",       # orchestrator model
    debate_model="claude-opus-4-6", # debate council model
    max_tokens=4096,
)
```

---

## Research & Documentation

This project is grounded in research produced by the Crucible system itself:

- **[AI-Assisted Development Landscape 2026](docs/research/ai-coding-landscape-2026.md)** — Claude Code leak analysis, vibe coding, tool convergence, SWE-bench contamination, Devin data, multi-agent framework comparison
- **[Forecasts and Scenarios 2027](docs/research/forecast-2027.md)** — METR productivity study, 73% daily adoption, Gartner upskilling forecast, three scenarios with probabilities
- **[Agent Society Specification](docs/architecture/agent-society-spec.md)** — persistent identity, XP economy, personality drift, emergent language, safety-as-physics
- **[Debate Council Deep Dive](docs/architecture/debate-council-deep-dive.md)** — persona specifications, scoring model, real debate examples, anti-patterns

---

## The Course

A 10-module course produced from the research study:

| Module | Title |
|--------|-------|
| 01 | [State of AI-Assisted Development](course/01-state-of-ai-development.md) |
| 02 | [Anatomy of Vibe Coding](course/02-vibe-coding-anatomy.md) |
| 03 | [Multi-Agent Systems: Theory to Practice](course/03-multi-agent-theory.md) |
| 04 | [Building Your First Agent Team with Crucible](course/04-first-agent-team.md) |
| 05 | [The Debate Council Pattern](course/05-debate-council-pattern.md) |
| 06 | [Code Quality in the AI Era](course/06-code-quality-ai-era.md) |
| 07 | [Predictive Analysis](course/07-predictive-analysis.md) |
| 08 | [Building an Agent Society](course/08-agent-society.md) |
| 09 | [Open Source Strategy](course/09-open-source-strategy.md) |
| 10 | [The Developer's Evolving Role](course/10-developers-evolving-role.md) |

---

## Philosophy

Three convictions:

1. **Adversarial review finds what consensus misses.** The best way to stress-test an idea is to have a skeptic, a pragmatist, a visionary, and a user advocate fight over it.

2. **Every decision is a research question.** Naming, architecture, prioritization — these aren't administrative tasks. They're hypotheses. Test them.

3. **Dissent is data.** The losing arguments are logged, not discarded. A close debate (7.1 vs 6.9) is very different from a blowout (9.2 vs 4.1). Both pieces of information matter.

---

## Roadmap

- [ ] Streaming output (watch debates unfold in real-time)
- [ ] Web UI (visual debate transcript viewer)
- [ ] Plugin API (custom agents)
- [ ] Live web search integration
- [ ] SQLite memory persistence across runs
- [ ] Debate replay and branching
- [ ] Custom persona definitions
- [ ] Agent Society Phase 2 (persistent identity, XP economy)

---

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR. The short version: open an issue first for anything non-trivial, write tests before marking complete, one thing per PR.

Real-world debate transcripts that produced wrong results are among the most valuable contributions. If the Debate Council got it wrong, that's a bug.

---

## License

MIT — see [LICENSE](LICENSE)
