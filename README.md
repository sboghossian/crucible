# Crucible

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-alpha-orange.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)

**Most multi-agent frameworks are demos. Crucible is a research instrument.**

Every decision — naming, architecture, prioritization, interpretation — goes through a 4-persona adversarial Debate Council before anything happens. No consensus by default. The best argument wins.

---

## The Problem

Multi-agent AI systems have a sycophancy problem. Agents agree with each other. They share the same model, similar priors, and no mechanism for adversarial challenge. You get fast answers, not rigorous ones.

Research requires pressure. Metal is tested in a crucible. So are ideas.

## What Crucible Does

Crucible is a Python framework for running parallel AI research agents with a mandatory adversarial review layer. You point it at a codebase, a question, or a decision — and it runs:

1. **Specialized agents** in parallel: scan the codebase, research the topic, find patterns, forecast outcomes
2. **Every decision** routes through the **Debate Council** — 4 AI personas with structural biases who argue adversarially across 3 rounds
3. The winner's position becomes the decision. All arguments are logged. Dissent is preserved.

## The Debate Council

The crown jewel. Four personas, one topic, three rounds.

| Persona | Structural Bias | Weights Highest |
|---|---|---|
| **The Pragmatist** | Implementation feasibility first | Practical feasibility (40%) |
| **The Visionary** | Transformative potential first | Novelty & upside (45%) |
| **The Skeptic** | Evidence quality first | Evidence rigor (45%) |
| **The User Advocate** | Human experience first | Adoption & clarity (35%) |

**Round 1 — Opening Statements:** Each persona presents their position independently (parallel LLM calls).

**Round 2 — Cross-Examination:** Each persona challenges the two weakest arguments from the others.

**Round 3 — Closing Arguments:** Each persona refines their position. Intellectual honesty is rewarded.

**Scoring:** Each closing argument is scored on evidence quality, logical consistency, practical feasibility, and novelty. The winner's position becomes the decision.

### Example: Naming This Framework

The Debate Council actually named this framework. Here's the abridged transcript:

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

## Quick Start

```bash
pip install crucible-ai
export ANTHROPIC_API_KEY=sk-...
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

asyncio.run(main())
"
```

Or run the full example:

```bash
git clone https://github.com/your-org/crucible
cd crucible && pip install -e .
python examples/analyze_projects.py --debate-only
```

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
| **Course Builder** | Structures findings into a 4-module learning path |
| **Publisher** | GitHub optimization: topics, README hero, release notes |

## The `decide()` Method

The orchestrator's `decide()` method is how every fork in the road is handled:

```python
from crucible import Orchestrator

orch = Orchestrator()

# Naming decision
result = await orch.standalone_debate(
    topic="What should we call the new API endpoint?",
    options=["/analyze", "/research", "/inspect", "/run"],
    context="This endpoint kicks off a full multi-agent research run."
)

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
print(f"Decision: {result.decision}")
print(f"Dissent: {result.dissenting_views}")
```

## Installation

```bash
pip install crucible-ai          # from PyPI (coming soon)
pip install -e ".[dev]"          # development install
```

**Requirements:** Python 3.11+, Anthropic API key

## Running Tests

```bash
pytest tests/ -v
pytest tests/test_debate_council.py -v  # just the debate tests
```

## Configuration

```python
from crucible import Orchestrator, AgentConfig

orch = Orchestrator(
    api_key="sk-...",           # or ANTHROPIC_API_KEY env var
    model="claude-opus-4-6",    # orchestrator model
    debate_model="claude-opus-4-6",  # debate council model
    max_tokens=4096,
)
```

## Philosophy

Crucible is built on three convictions:

1. **Adversarial review finds what consensus misses.** The best way to stress-test an idea is to have a skeptic, a pragmatist, a visionary, and a user advocate fight over it.

2. **Every decision is a research question.** Naming, architecture, prioritization — these aren't administrative tasks. They're hypotheses. Test them.

3. **Dissent is data.** The losing arguments are logged, not discarded. A close debate (7.1 vs 6.9) is very different from a blowout (9.2 vs 4.1).

## Roadmap

- [ ] Streaming output (watch debates in real-time)
- [ ] Web UI (visual debate transcript viewer)
- [ ] Plugin API (custom agents)
- [ ] Live web search integration (Brave/Tavily)
- [ ] Memory persistence across runs (SQLite backend)
- [ ] Debate replay and branching
- [ ] Custom persona definitions

## Contributing

Crucible is early. The best contributions right now are:
- New agent implementations (open an issue first)
- Persona refinement (bias profiles should be grounded in research)
- Real-world test cases (debates that surprised you)

## License

MIT — see [LICENSE](LICENSE)
