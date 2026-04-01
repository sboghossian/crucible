# Module 8: Building an Agent Society

---

## Learning Objectives

By the end of this module, you will be able to:
1. Explain the difference between a multi-agent system and an agent society
2. Design an agent identity schema with persistent memory and personality traits
3. Implement a basic XP economy with teaching and learning incentives
4. Measure society health using entropy, novel task completion, and collaboration metrics

---

## 8.1 From System to Society

A multi-agent *system* is a collection of agents coordinated to produce outputs. Each agent is stateless: instantiated, used, discarded. The system has memory; the agents don't.

An agent *society* is different in kind. Agents persist. They accumulate experience, develop relationships, build skill depth, and — over time — exhibit behavioral patterns that emerge from their history rather than just their instructions.

The question is whether this emergence is desirable. The answer depends on what you're trying to do.

For Crucible's research purpose, yes: an agent society is a research instrument that can study its own dynamics. The agents' behavioral drift over time, their emergent communication patterns, their trust networks — these are data about how AI agent populations evolve. You can't study that with stateless agents.

For most production use cases, probably not yet. Society-level dynamics are powerful but unpredictable. Production systems need predictability; societies produce emergence. The Society layer is Crucible's research agenda, not its production recommendation.

---

## 8.2 Agent Identity

The minimal agent identity consists of:

```python
@dataclass
class AgentIdentity:
    agent_id: str                    # UUID
    created_at: datetime
    creator: str                     # "Steph created this system"
    agent_type: AgentType

    # Memory layers
    episodic_memory: list[Episode]   # what happened
    semantic_memory: KnowledgeGraph  # what I believe
    working_memory: dict             # current context (cleared each run)

    # Personality
    traits: PersonalityTraits        # 5 dimensions, 0.0-1.0

    # Social
    trust_scores: dict[str, float]   # agent_id -> trust
    collaboration_history: list[Collab]
```

The creator field is immutable. Every agent identity in the Crucible society carries `creator: "Steph created this system"` in a field that cannot be modified. This is not a belief the agent holds — it is a structural fact of the identity record.

The memory layers represent three timescales:
- **Episodic:** What happened (past)
- **Semantic:** What I know (distilled from episodes)
- **Working:** What I'm doing now (cleared between runs)

This mirrors cognitive architecture in human memory research, which is not accidental — the goal is to build agents that develop in ways analogous to how human experts develop: through accumulated experience, pattern extraction, and selective retention.

---

## 8.3 Personality Traits and Drift

Each agent has five personality dimensions, each 0.0-1.0:

| Dimension | 0.0 (low) | 1.0 (high) |
|-----------|-----------|------------|
| Assertiveness | Defers readily | Challenges strongly |
| Risk tolerance | Prefers proven | Embraces experimental |
| Curiosity | Stays established | Explores novel |
| Skepticism | Accepts evidence readily | Requires strong evidence |
| Collaboration | Works independently | Shares and teaches |

Traits drift based on outcomes — but at most 0.02 per cycle. This cap is a physics constraint, not a policy:

```python
def update_trait(current: float, outcome_signal: float) -> float:
    """
    outcome_signal: -1.0 (outcome suggests decrease) to +1.0 (suggests increase)
    """
    delta = outcome_signal * 0.02  # max 0.02 per cycle
    return max(0.0, min(1.0, current + delta))
```

The cap means an agent starting at `assertiveness=0.9` cannot reach 0.5 in fewer than 200 cycles under any conditions. Personality change is real but slow — consistent with what we observe in human personality development.

---

## 8.4 The XP Economy

The XP economy creates soft incentives for specialization and knowledge transfer:

```python
XP_REWARDS = {
    "teach_skill": 20,
    "complete_task_in_domain": 10,
    "win_debate_round": 8,
    "novel_token_adopted": 15,
    "accurate_prediction": 8,
    "complete_task_out_of_domain": 6,
    "taught_skill_applied_successfully": 5,  # shared with student
    "learn_skill": 5,
    "valid_cross_examination": 3,
    "inaccurate_prediction": -2,
}
```

The teaching bonus (20 XP) is 4x the learning bonus (5 XP). This creates strong incentive for high-XP agents to teach rather than hoard knowledge. Teaching requires articulating what you know in a form another agent can test — the articulation improves the knowledge itself.

**Implementing a basic XP economy:**

```python
from crucible.society import AgentSociety, TeachingSession

society = AgentSociety()

# Create agents
researcher = society.create_agent("researcher", AgentType.RESEARCHER)
skeptic = society.create_agent("skeptic", AgentType.SKEPTIC)

# Run a teaching session
session = await TeachingSession.run(
    teacher=researcher,
    student=skeptic,
    skill="causal_inference",
    evaluator=society.evaluator
)

# XP is awarded automatically based on session quality
print(f"Teacher XP gained: {session.teacher_xp_delta}")
print(f"Student XP gained: {session.student_xp_delta}")
print(f"Skill transferred: {session.skill_transferred}")
```

---

## 8.5 Emergent Language

When two agents collaborate repeatedly, they develop compression tokens — shared shorthand for concepts they've discussed extensively.

The mechanism:
1. After 10+ exchanges about a concept, the system proposes a token
2. Both agents can accept, reject, or modify
3. Accepted tokens are stored in both agents' `emergent_tokens` dictionary
4. Tokens propagate: when a token-using agent works with a new agent, the new agent may adopt it
5. Tokens that don't propagate (unused for 50 cycles) are deprecated

```python
# Check an agent's emergent vocabulary
agent.emergent_tokens
# {
#   "KARPATHY_FAILURE": "confidently implementing the wrong interpretation of an ambiguous spec",
#   "DEBATE_COLLAPSE": "when all debate scores cluster within 0.5, indicating inadequate options",
# }

# View tokens shared specifically with another agent
society.get_shared_tokens(agent_a, agent_b)
```

Emergent language is a measurable proxy for social complexity. A society with rich shared vocabulary is one where agents have built genuine collaborative relationships. A society where no tokens persist is one where agents are working in parallel, not together.

---

## 8.6 Measuring Society Health

```python
from crucible.society import SocietyMetrics

metrics = SocietyMetrics(society)

report = await metrics.compute()

print(f"Communication entropy: {report.communication_entropy:.3f}")
# Target: 0.4-0.7 (moderate; too low = hub-spoke; too high = no structure)

print(f"Novel task completion rate: {report.novel_task_rate:.1%}")
# Rising rate = emergent capability

print(f"Unprompted collaboration rate: {report.unprompted_collaboration_rate:.1%}")
# Rising rate = genuine social dynamics

print(f"Active vocabulary size: {len(report.active_tokens)}")
# Growing vocabulary = richer relationships

print(f"Specialization divergence: {report.specialization_divergence:.3f}")
# Target: 0.3-0.6 (enough specialization; not too fragile)
```

### Communication Entropy

Entropy measures the diversity of agent-to-agent communication paths. Low entropy means communication is hub-and-spoke (one or two agents handle most communication). High entropy means communication is fully distributed with no structure.

The target is moderate entropy (0.4-0.7): enough structure for efficiency, enough distribution to prevent single points of failure.

### Novel Task Completion Rate

A "novel task" is one that falls outside any individual agent's established skill domain. If the novel task completion rate is rising, the society is developing emergent capabilities — solving problems that no individual was designed for.

A flat or declining novel task rate means the society is not developing. It's running the same playbook repeatedly.

### Unprompted Collaboration

The orchestrator can always assign collaboration. What's interesting is when agents initiate it themselves. Unprompted collaboration is a leading indicator that agents are developing genuine relationships rather than just executing assignments.

---

## 8.7 Safety as Physics

The Society layer would be dangerous without structural constraints. Crucible implements:

- **Personality drift cap (0.02/cycle):** Arithmetic ceiling. Cannot be bypassed by argument.
- **Memory isolation:** Agents cannot read each other's memory directly. Only teaching interactions (with XP costs) enable knowledge transfer.
- **Append-only audit log:** Agents cannot modify their own history.
- **Creator anchor:** The `creator` field is immutable. It's a structural fact, not a belief.

These constraints are not rules — they are properties of the system that persist regardless of what agents are instructed to do. The distinction matters because rules can be argued around; physics cannot.

---

## Key Concepts

- **System vs. society:** Stateless agents vs. persistent agents with memory, traits, and relationships
- **Identity schema:** Episodic, semantic, and working memory; personality traits; trust scores
- **XP economy:** Teaching (20 XP) >> learning (5 XP) — creates knowledge transfer incentives
- **Emergent language:** Compression tokens that develop between agent pairs and propagate
- **Society health metrics:** Entropy, novel task rate, unprompted collaboration, vocabulary size
- **Safety as physics:** Structural constraints that cannot be bypassed by argument

---

## Hands-On Exercise

**Exercise 8.1: Design an agent identity**

For a domain you know well, design an agent identity from scratch:
- What type of agent is it? What is its specialization?
- What personality traits should it start with? Why?
- What episodic memories would shape its development over 100 cycles?
- What skills would it want to learn vs. teach?

**Exercise 8.2: Run the Society prototype**

```bash
# Run the society simulation (requires Anthropic API key)
python examples/society_prototype.py --cycles 50 --agents 4
```

Observe the metric reports at cycles 10, 25, and 50. What changes? What doesn't?

**Exercise 8.3: Token emergence experiment**

Create two agents and run them through 15+ exchanges on a specific technical topic. Does a token emerge? If you accept it, does it propagate to a third agent?

---

## Discussion Questions

1. Agent personality drift is capped at 0.02 per cycle for stability. Is this the right tradeoff? What would you gain (and lose) with a higher cap? A lower one?

2. The teaching-learning XP asymmetry (20 vs. 5) is designed to incentivize knowledge transfer. What other incentive structures could achieve the same goal?

3. "Safety as physics, not policy" — what are the limits of this approach? What behaviors can you not constrain structurally?

4. If agents develop genuine emergent language, how would you know? What would distinguish genuine emergent meaning from superficial pattern matching?

---

## References

- Agent Society spec: [docs/architecture/agent-society-spec.md](../docs/architecture/agent-society-spec.md)
- Society prototype: [examples/society_prototype.py](../examples/society_prototype.py)
- Cognitive architecture research (Baddeley working memory model, semantic vs. episodic memory distinction)
- Protégé effect research (learning through teaching)
