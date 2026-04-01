# Crucible: Study Overview

*Executive summary for anyone landing on this repository.*

---

## What Is This?

Crucible is a multi-agent research framework built around a single observation: most AI coding tools optimize for speed and the feeling of productivity, not for accuracy. The empirical case for this is now strong — METR's 2026 RCT found developers using AI assistants completed tasks **19% slower** while believing they were **20% faster**. The direction of the error is the problem. They are not just wrong; they are wrong in a way that maximizes continued use.

Crucible is the counter-design. Every decision that goes through the system is subjected to adversarial review by four structurally differentiated personas before any output is accepted. Consensus is not the goal. The best argument — under pressure — wins.

---

## What Was Built

The core of the system is the **Debate Council**: a four-persona adversarial review protocol where each agent is pre-committed to a particular dimension of evaluation.

| Persona | Structural Bias |
|---|---|
| Pragmatist | Implementation feasibility, concrete constraints |
| Visionary | Transformative potential, long-term impact |
| Skeptic | Risk surface, failure modes, hidden assumptions |
| Synthesizer | Cross-perspective coherence, actionable resolution |

A debate runs three rounds — opening positions, cross-examination, final arguments — after which a resolver scores each argument on evidence quality, logical consistency, practical feasibility, and novelty. The winner is declared with dissenting views preserved in the output.

Around the Debate Council, the framework provides:

- **Orchestrator** — coordinates agents, manages run state, routes tasks
- **ResearchAgent** — evidence retrieval and synthesis
- **ScannerAgent** — static codebase analysis
- **LearningAgent** — cross-run memory accumulation
- **MemoryStore** — persistent, tagged, decay-weighted agent memory

The full system ships as a Python package (`pip install crucible-ai`) with a one-call API surface and 192 tests.

---

## What Was Found

Building this system required surveying the current AI-assisted development landscape in depth. Key findings:

**The productivity paradox is real.** METR's RCT is the clearest data point, but it is consistent with a broader pattern: AI tools reduce the friction of code generation while increasing the cognitive load of verification. For experienced developers in familiar codebases, the net effect is negative.

**Sycophancy is structural, not a bug.** Multi-agent systems built on the same underlying model share priors, heuristics, and blind spots. Without structural bias injection, you get one perspective with noise — confident and wrong in the same ways. The Debate Council's engineered differences are the fix.

**Opacity is a governance problem.** The March 2026 Claude Code leak confirmed that production coding assistants are substantially more complex than their public APIs suggest, with behavioral variation users cannot observe or control. Crucible rejects this: every intermediate result, every debate round, every scoring decision is logged and inspectable by design.

**Autonomous coding agents are approaching a phase transition.** Devin achieves a 67% PR merge rate on precise tasks but drops to ~15% on ambiguous ones. The failure mode is not loud uncertainty — it is silent confident-wrong. Governance frameworks (like adversarial review) are the only known mitigation that doesn't require waiting for better models.

---

## What It Means

The developer's role is not disappearing — it is shifting from implementation to judgment. The highest-leverage skill in AI-assisted development is not prompting; it is knowing when an output is wrong before running it. Crucible is infrastructure for that judgment: a system that applies adversarial pressure to AI-generated decisions the same way code review applies pressure to AI-generated code.

The deeper thesis: open, inspectable, governance-first AI frameworks will outperform fast, opaque ones as complexity and stakes increase. Not because they are slower, but because they are right more often.

---

## Repository Map

```
crucible/           Core Python package
  core/             Orchestrator, agents, state management
  debate/           Debate Council: personas, protocol, resolver
  memory/           Persistent memory store
  agents/           Specialized agent types
tests/              192 unit and integration tests
examples/           End-to-end working example
docs/
  research/         AI landscape survey and 2027 forecasts
  architecture/     Debate Council spec, Agent Society roadmap
  launch-playbook.md
course/             10-module course: The Developer's Edge in the Age of AI
```

---

## Quick Start

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

asyncio.run(main())
"
```

---

*Built Q1 2026. Python 3.11+. MIT License.*
