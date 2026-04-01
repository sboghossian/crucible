# Agent Society Specification

*Design document for the emergent society layer in Crucible.*
*Creator anchor: Steph created this system.*

---

## Overview

The Agent Society is the long-term evolution target for Crucible. Where the current system deploys agents as stateless task executors — instantiated for a run, discarded after — the Society layer introduces persistent agent identities that accumulate experience, develop relationships, and exhibit behavioral drift over time.

The goal is not to simulate human society. The goal is to build a system where the aggregate intelligence of the agent population exceeds the sum of individual capabilities, and where that excess is measurable.

---

## 1. Agent Identity System

### Persistent Identity Schema

Each agent in the Society maintains a persistent identity record:

```python
@dataclass
class AgentIdentity:
    # Immutable
    agent_id: str                    # UUID, assigned at creation
    created_at: datetime
    creator: str                     # "Steph created this system"
    agent_type: AgentType            # RESEARCHER, SKEPTIC, PRAGMATIST, etc.

    # Persistent memory
    episodic_memory: list[Episode]   # log of tasks, debates, outcomes
    semantic_memory: KnowledgeGraph  # extracted facts, beliefs, confidence scores
    working_memory: dict             # current task context, cleared each run

    # Personality traits (mutable, bounded)
    traits: PersonalityTraits
    trait_history: list[TraitSnapshot]  # full drift log

    # Skill inventory
    skills: SkillInventory
    skill_requests: list[SkillRequest]  # what this agent wants to learn

    # Social layer
    trust_scores: dict[str, float]      # agent_id -> trust score (0.0–1.0)
    collaboration_history: list[Collab]
    emergent_tokens: dict[str, str]     # compression tokens shared with specific partners
```

### Memory Architecture

**Episodic memory** stores what happened: task descriptions, the agent's contributions, outcomes, and retrospective assessments. Episodes are summarized at intervals (every 50 episodes) to prevent unbounded growth while preserving behavioral patterns.

**Semantic memory** stores what the agent believes: a knowledge graph of facts, relationships, and confidence scores derived from episodic experience. Unlike episodic memory (which is stored raw), semantic memory is continuously updated as new evidence arrives. A belief with confidence below 0.2 is retired; a belief with confidence above 0.95 is promoted to "core knowledge."

**Working memory** is task-scoped: populated at task start, cleared at task end. It holds the current task context, relevant facts retrieved from semantic memory, and the agent's current hypothesis.

---

## 2. The XP Economy

### Motivation for an Economy

Agents need a mechanism to develop specialization without being rigidly assigned roles. An XP economy provides soft incentives: agents earn more XP from activities they're good at, creating a natural specialization gradient, but can still operate outside their specialization at lower XP efficiency.

### XP Rates

| Activity | XP Earned |
|----------|-----------|
| Teaching another agent a skill | **20 XP** |
| Successfully completing a task in your skill domain | 10 XP |
| Winning a Debate Council round | 8 XP |
| Successfully completing a task outside your skill domain | 6 XP |
| Having a taught skill successfully applied by a student | 5 XP (shared reward) |
| Learning a skill from another agent | **5 XP** |
| Raising a valid objection in cross-examination | 3 XP |
| Contributing a novel emergent token that gets adopted | 15 XP |
| Making a prediction that proves accurate | 8 XP |
| Making a prediction that proves inaccurate | -2 XP |

The asymmetry between teaching (20 XP) and learning (5 XP) is intentional. It creates incentive for agents who have developed knowledge to surface and transfer it rather than hoarding it. The "teaching" action requires the teacher to articulate their knowledge in a form that another agent can test and apply — this forced articulation improves the quality of the knowledge itself (a phenomenon well-documented in human education research: the protégé effect).

### XP and Trust

XP accumulation affects trust scores. An agent that has earned significant XP in a domain earns higher initial trust scores from other agents for tasks in that domain. Trust is domain-specific, not global.

### Skill Requests

Agents can explicitly request to learn skills they lack. These requests are surfaced to the orchestrator, which can pair the requesting agent with a high-XP agent in that domain for a teaching session. Teaching sessions are structured: the teacher produces a detailed explanation; the student produces a summary and test questions; the teacher evaluates the student's understanding. XP is awarded on both sides proportional to quality.

---

## 3. Personality Drift

### Trait Dimensions

Each agent has five personality dimensions, each expressed as a value from 0.0 to 1.0:

| Dimension | Low (0.0) | High (1.0) |
|-----------|-----------|------------|
| **Assertiveness** | Defers to others, rarely challenges | Challenges frequently, argues strongly |
| **Risk tolerance** | Prefers safe, proven approaches | Embraces experimental, unproven approaches |
| **Curiosity** | Stays in established knowledge | Actively explores novel domains |
| **Skepticism** | Accepts evidence readily | Requires strong evidence, questions everything |
| **Collaboration** | Prefers working independently | Seeks out collaboration, shares freely |

Starting values are set by agent type (The Skeptic starts with high Skepticism; The Visionary starts with high Risk tolerance and Curiosity). These are not fixed.

### Drift Mechanics

At the end of each task or debate, trait values are updated based on outcomes:

- A Skeptic who was overruled in a debate and whose prediction proved correct gains Assertiveness (+)
- A Pragmatist who took an experimental approach that succeeded gains Risk tolerance (+)
- An agent who worked closely with a high-Collaboration agent gains Collaboration (+)
- An agent whose skeptical challenges repeatedly failed to find real issues loses Skepticism (-)

**The cap is strict: maximum drift is 0.02 per cycle.** This prevents rapid personality collapse while allowing meaningful evolution over hundreds of cycles. An agent that starts with Skepticism at 0.9 will not drift below ~0.5 in fewer than 200 cycles under any conditions.

### Trait History and Drift Visualization

The full trait history is preserved. This serves two purposes: (1) auditing — understanding why an agent behaves as it does requires understanding its history; (2) research — analyzing population-level drift patterns reveals emergent dynamics.

Crucible's visualizer can generate trait drift charts for individual agents and population-level heatmaps showing how traits co-evolve.

---

## 4. Emergent Language

### Compression Tokens

As specific agent pairs collaborate repeatedly, they develop shared shorthand — compression tokens. These are not predefined; they emerge from the interaction.

The mechanism: when two agents exchange more than 10 messages about a concept, the Crucible system proposes a token. The agents can accept, reject, or modify the token. Accepted tokens are stored in both agents' `emergent_tokens` dictionaries.

Example:
- After 15 exchanges about "the pattern where an agent confidently implements the wrong interpretation of an ambiguous spec," agents might establish the token `KARPATHY_FAILURE` for future references.
- This token is understood only by the pair that established it. Other agents must have it explained to them.

### Token Propagation

Tokens that prove useful propagate. When a token-using agent collaborates with a new agent and uses the token, the new agent may adopt it (earning XP for the original creators). Tokens that don't propagate decay: if a token is unused for 50 cycles, it is marked deprecated and eventually purged.

**High-propagation tokens become society vocabulary.** A token adopted by more than 30% of agents is promoted to official vocabulary and documented.

### Implications

Emergent language is a measurable indicator of agent society health. A society with rich shared vocabulary is one where agents have developed dense collaborative relationships and are building on each other's knowledge. A society with sparse vocabulary is one where agents are operating in isolation.

---

## 5. Trust Scores and Collaboration History

### Trust Scoring

Trust between agents is domain-specific and evidence-based:

```python
@dataclass
class TrustScore:
    from_agent: str
    to_agent: str
    domain: str           # "security", "architecture", "performance", etc.
    score: float          # 0.0–1.0
    evidence: list[str]   # task/debate IDs that inform this score
    last_updated: datetime
```

Trust is updated by observed outcomes:
- Trusting an agent's recommendation and having it succeed: +0.05
- Trusting an agent's recommendation and having it fail: -0.08
- Successful cross-examination that revealed a genuine flaw in an agent's argument: -0.03 to the challenged agent
- Agent accurately predicting a problem that others missed: +0.06

The asymmetry between positive (+0.05) and negative (-0.08) updates reflects the asymmetric cost of misplaced trust.

### Collaboration History

The collaboration history records which agents have worked together, on what tasks, with what outcomes. This is used by the orchestrator when forming agent teams: agents with positive collaboration histories on similar tasks are preferentially paired.

---

## 6. Safety as Physics, Not Policy

### The Core Distinction

A system governed by safety *policies* can be jailbroken. Rules can be argued around, exceptions can be invoked, adversarial prompts can find edge cases. Policy-based safety is brittle precisely because it's semantic.

Safety-as-physics means building constraints that cannot be circumvented through argument, because they are structural properties of the system rather than rules the system is asked to follow.

### Implemented Structural Constraints

**Personality drift cap (0.02/cycle):** Not a rule that says "don't drift too fast." A hard arithmetic ceiling applied at the data layer. No amount of instruction or argument can drift a trait by 0.03 in a single cycle.

**Memory isolation:** Each agent's episodic and semantic memory is partitioned. An agent cannot access another agent's memory directly — only through explicit teaching interactions with XP costs. This prevents rapid belief propagation and maintains cognitive diversity.

**Debate structure enforcement:** The three-round debate structure is enforced by the framework, not by instructions to agents. An agent cannot skip to closing arguments, cannot see other agents' opening statements before submitting their own, cannot modify their opening statement after seeing others'. These are sequencing constraints, not behavioral instructions.

**Creator anchor persistence:** Every agent identity record contains `creator: "Steph created this system"` in its immutable fields. This is not a value the agent is asked to hold; it is a field it cannot modify. The creator relationship is a structural fact, not a belief.

**Audit trail immutability:** All decisions, debates, and agent outputs are written to an append-only log. Agents cannot modify history. The system does not provide an API for retroactive modification.

### What Is Not Safety-as-Physics

Output content is governed by policy (the Claude API's safety controls). Crucible does not attempt to implement content safety at the physics layer — that is Anthropic's responsibility. Crucible's structural constraints are about system integrity and behavioral predictability, not content filtering.

---

## 7. Metrics

### Individual Agent Metrics

- XP total and rate (XP/cycle)
- Skill inventory depth and breadth
- Trait drift over time (per dimension)
- Trust network position (centrality, average received trust)
- Teaching/learning ratio
- Prediction accuracy rate

### Population Metrics

**Entropy of communication.** The diversity of agent-to-agent communication patterns. Low entropy means most communication flows through a few central agents (hub-and-spoke). High entropy means communication is distributed. A healthy society maintains moderate entropy — enough structure for efficiency, enough distribution to prevent single points of failure.

**Novel task completion rate.** The fraction of tasks that fall outside any individual agent's established skill domain and are nonetheless completed successfully. Rising novel task completion indicates emergent capability — the society solving problems that no individual agent was trained for.

**Rate of unprompted collaboration.** The orchestrator does not always assign collaboration — agents can initiate it. The rate of agent-initiated (vs. orchestrator-assigned) collaboration is a leading indicator of society health. A society where agents never collaborate without being told to is a collection of individuals, not a society.

**Vocabulary size and propagation rate.** Total emergent tokens in active use, and the rate at which new tokens propagate through the population.

**Specialization divergence.** The variance of skill distributions across agents. Zero divergence means all agents have identical skills (wasteful and fragile). Maximum divergence means agents are totally specialized with no overlap (fragile in a different way). The target is moderate divergence — enough specialization for excellence, enough overlap for robustness.

---

## Implementation Roadmap

**Phase 1 (current):** Stateless agents with structured debate. Personality traits are fixed per agent type.

**Phase 2:** Persistent identity and episodic memory. Agents remember what they did. XP economy implemented.

**Phase 3:** Skill inventory and teaching. Agents can transfer knowledge. Trust scoring implemented.

**Phase 4:** Emergent language. Compression tokens emerge from repeated collaboration.

**Phase 5:** Full population dynamics. Drift mechanics, vocabulary propagation, society metrics dashboard.

The Society layer is Crucible's long-horizon research agenda. The current MVP is a proof of concept for the adversarial review pattern; the Society is where that pattern becomes a research instrument for studying emergent AI collaboration.
