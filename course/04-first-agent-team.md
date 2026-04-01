# Module 4: Building Your First Agent Team with Crucible

---

## Learning Objectives

By the end of this module, you will be able to:
1. Install and configure Crucible with an Anthropic API key
2. Run a standalone debate on a real decision you're facing
3. Compose a multi-agent research run against a codebase or topic
4. Interpret debate output: scores, dissenting views, and what close margins mean

---

## 4.1 Installation and Setup

```bash
# Install from PyPI
pip install crucible-ai

# Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# Verify the install
python -c "from crucible import Orchestrator; print('ready')"
```

**Minimum requirements:** Python 3.11+, Anthropic API key with access to claude-opus-4-6.

**Cost note:** The Debate Council runs 4 parallel LLM calls per round × 3 rounds + 1 scoring call = 13 LLM calls per debate. Using claude-opus-4-6 at current pricing, a typical debate costs $0.15-0.40 depending on context length. Budget accordingly.

---

## 4.2 Your First Standalone Debate

The fastest path to useful output:

```python
import asyncio
from crucible import Orchestrator

async def main():
    orch = Orchestrator()

    result = await orch.standalone_debate(
        topic="Should we migrate our auth system to JWTs?",
        options=[
            "yes, migrate to JWTs now",
            "no, stay with session cookies",
            "hybrid: JWTs for API, sessions for web"
        ],
        context="""
        Current: session-based auth, Redis session store.
        Team: 4 engineers, all familiar with sessions, 1 has JWT experience.
        Scale: 200k users, adding mobile app next quarter.
        Pain: Redis sessions are becoming a memory bottleneck.
        """
    )

    print(f"\n=== WINNER: {result.winner.upper()} ===")
    print(f"Score: {result.winner_score:.1f}/10")
    print(f"\nDecision: {result.decision}")
    print(f"\nDissenting views: {result.dissenting_views}")

asyncio.run(main())
```

**What you'll see:** The four personas' positions, cross-examination exchanges, and a scored recommendation with dissenting views preserved.

**Reading the output:**
- `winner`: Which persona produced the winning argument
- `winner_score`: The winning score (0-10). Below 6.5, reconsider the options.
- `decision`: A one-paragraph synthesis of the winning position
- `dissenting_views`: The strongest minority positions (these matter)

---

## 4.3 Interpreting Scores

Score margins are signal:

| Pattern | Interpretation |
|---------|---------------|
| Winner 8.5+, others below 6.0 | Strong consensus. High confidence. |
| Winner 7.5-8.5, gap >1.5 | Clear preference, reasonable confidence. |
| Winner 7.0, second-place 6.8 | Close debate. The margin is within noise. Revisit if context changes. |
| All scores 5.5-6.5 | No clear winner. The options may all be inadequate, or the topic needs reframing. |
| Unexpected persona wins | The debate revealed a dimension you didn't anticipate. Read the winning argument carefully. |

**Close margins (< 0.5 spread) mean the decision is genuinely uncertain.** Don't force false confidence on a close call. Document the margin and set a trigger: "revisit this decision if X happens."

---

## 4.4 Multi-Agent Research Run

A full orchestration run against a codebase or topic:

```python
import asyncio
from crucible import Orchestrator

async def analyze_codebase():
    orch = Orchestrator()

    # Analyze a local repository
    result = await orch.run(
        repo_path="/path/to/your/project",
        topic="Evaluate the architecture of this codebase for scale",
        output_dir="./crucible_output"
    )

    # Access different parts of the result
    print("=== RESEARCH FINDINGS ===")
    for finding in result.research.findings:
        print(f"- [{finding.confidence:.0%}] {finding.claim}")

    print("\n=== PATTERNS IDENTIFIED ===")
    for pattern in result.patterns.recurring:
        print(f"- {pattern.name}: {pattern.description}")

    print("\n=== ARCHITECTURE DECISION ===")
    decision = result.debate
    print(f"Winner: {decision.winner} ({decision.winner_score:.1f}/10)")
    print(f"Decision: {decision.decision}")

    print("\n=== FORECAST ===")
    for scenario in result.forecast.scenarios:
        print(f"- {scenario.name} ({scenario.probability:.0%}): {scenario.summary}")

asyncio.run(analyze_codebase())
```

The output directory will contain:
- `research.json` — structured findings with confidence scores
- `debate_transcript.json` — full debate transcript with all rounds
- `patterns.json` — recurring patterns and anti-patterns
- `forecast.json` — probabilistic scenarios
- `visualizations/` — Mermaid diagrams of architecture, debates, patterns

---

## 4.5 Custom Debate Configuration

```python
from crucible import Orchestrator, DebateConfig

orch = Orchestrator(
    model="claude-opus-4-6",           # orchestrator model
    debate_model="claude-opus-4-6",    # debate council model
    max_tokens=4096,
)

# Override persona weights
config = DebateConfig(
    pragmatist_weights={"feasibility": 0.5, "evidence": 0.2, "consistency": 0.2, "novelty": 0.1},
    # Other personas use defaults
    min_debate_score_threshold=6.0,    # flag debates where winner scores below this
)

result = await orch.standalone_debate(
    topic="Should we add a plugin API?",
    options=["yes, now", "yes, after v1.0", "no, keep it simple"],
    config=config
)
```

---

## 4.6 Common Mistakes

**Mistake 1: Options that aren't really options**

Bad: `options=["do it the right way", "do it the wrong way", "don't do it"]`

The Debate Council can't give useful output when one option is clearly superior by framing. Present genuinely competing options with real tradeoffs.

Good: `options=["REST API with pagination", "GraphQL with cursor-based pagination", "gRPC with streaming"]`

---

**Mistake 2: Context that's too thin**

Bad: `context="We have a web app"`

The personas use context to ground their arguments in your actual situation. Thin context produces generic arguments. Include: team size, technical constraints, timeline, and the specific decision trigger.

---

**Mistake 3: Ignoring the dissent**

The dissenting views field is not a consolation prize. It's the part of the debate that the winner didn't fully address. Read it. If it resonates, the debate may not have reached the right conclusion.

---

**Mistake 4: Debating implementation details**

Debate Council is for decision forks, not implementation. "Should we use a HashMap or ArrayList here?" is not a Debate Council question. "Should we use in-memory caching or Redis?" — maybe, if the decision has real tradeoffs.

---

## 4.7 Using the Decision Log

Every debate is logged to the output directory. Review the log after a week of using Crucible:
- Which debates had the closest margins?
- Which persona wins most often for your decisions?
- Are there patterns in the topics you're debating?

If the Pragmatist wins 80% of your debates, you might be presenting options that are skewed toward pragmatic concerns. If debates are consistently close, your decision-making context might be unusually ambiguous.

---

## Key Concepts

- **Standalone debate:** `orch.standalone_debate(topic, options, context)` for single decisions
- **Full run:** `orch.run(repo_path, topic)` for multi-agent research
- **Score margins:** Close margins (< 0.5) mean genuine uncertainty — document and set a trigger
- **Dissenting views:** The part of the debate the winner didn't fully answer

---

## Hands-On Exercise

**Exercise 4.1: Debate a real decision**

Identify a decision you've made recently (or are currently facing) and run it through the Debate Council. Compare the output to the decision you made or are inclined to make. Did the debate surface anything you hadn't considered?

**Exercise 4.2: Run a codebase analysis**

Point Crucible at a codebase you're familiar with. Review the research findings — are they accurate? What did the agents miss? What surprised you?

**Exercise 4.3: Break the Debate Council**

Deliberately design a debate prompt where you expect the Debate Council to fail — either by producing obvious output, getting the wrong answer, or failing to surface the key consideration. What does this tell you about the system's limitations?

---

## Discussion Questions

1. The Debate Council costs $0.15-0.40 per debate. At what decision frequency does this become prohibitive? At what decision *value* does it always make sense?

2. The full research run analyzes a codebase with multiple specialized agents. How would you verify the quality of the research output? What would a false positive and false negative look like?

3. When the Pragmatist wins most debates, is that a signal about your decision-making context, or about the Pragmatist's inherent advantage on certain types of questions?

4. The dissenting views field preserves losing arguments. Under what circumstances should a team override the winner's recommendation in favor of a dissenting view?

---

## References

- Crucible documentation: [docs/](../docs/)
- Crucible source code: [crucible/](../crucible/)
- Anthropic API documentation
