# Module 3: Multi-Agent Systems — Theory to Practice

---

## Learning Objectives

By the end of this module, you will be able to:
1. Explain the core problem that multi-agent systems are designed to solve (and create)
2. Compare LangGraph, CrewAI, AutoGen, and OpenHands with accurate capability and limitation data
3. Identify the right framework for a given use case
4. Explain why shared priors in multi-agent systems are a fundamental design challenge

---

## 3.1 Why Multi-Agent?

A single AI agent has a context limit. It has a fixed model with fixed priors. It cannot parallelize. And it cannot check its own work in any meaningful sense — it lacks the epistemic diversity to be its own critic.

Multi-agent systems address these limitations through **specialization and parallelism**. Instead of one agent trying to do everything, you have multiple agents, each optimized for a specific task, running in parallel or in sequence, with their outputs combined.

The theoretical promise: a team of specialized agents should outperform a single generalist agent on complex tasks, for the same reason that a team of specialized humans outperforms a single generalist.

The actual challenge: AI agents don't naturally disagree with each other.

---

## 3.2 The Shared Priors Problem

When you instantiate four agents from the same model, you get four agents with:
- Similar world models (same training data)
- Similar heuristics (same RLHF tuning)
- Similar blind spots (same gaps in training)
- Similar communication styles (same model)

Ask them to collaborate on a decision, and they will tend to converge. Not because the answer is right, but because their priors are aligned. This is not consensus based on evidence — it's correlation based on shared training.

The shared priors problem has a specific failure mode: confident agreement on wrong answers. A system where agents agree with each other is not demonstrating quality — it may be demonstrating synchronized hallucination.

This is the founding insight of Crucible's design: genuine multi-agent systems require engineered epistemic diversity, not just multiple instantiations of the same model.

---

## 3.3 The Framework Landscape

### LangGraph

**Architecture:** Graph-based state machine. You define nodes (agent functions) and edges (conditional routing between them). State flows through the graph; each node reads from and writes to the shared state.

**Strengths:**
- Explicit, auditable control flow
- Strong ecosystem (100+ LangChain tool integrations)
- Production-tested (LangSmith has telemetry from significant production deployments)
- Good for workflows where the sequence of agent operations matters

**Weaknesses:**
- The graph mental model adds significant cognitive overhead
- Teams not already using LangChain face an adoption cost
- Debugging complex graphs is non-trivial (traces help, but the graph itself can be hard to reason about)

**Best for:** Production workflows with complex, conditional routing and a team already in the LangChain ecosystem.

---

### CrewAI

**Architecture:** Role-based agent teams. You define agents with natural language descriptions of their roles, goals, and backstories, then define tasks and assign them to agents. A crew orchestrates the execution.

**Strengths:**
- Accessible API: non-ML engineers can define agent teams without deep ML knowledge
- One of the most-forked AI repos on GitHub through 2025 — large community
- Role definition in natural language is fast to iterate on

**Weaknesses:**
- The abstraction layer limits fine-grained control
- The opinionated structure is a bad fit for non-standard workflows
- At scale, the "role" abstraction can become unclear: what exactly does "role" mean for an AI agent?

**Best for:** Getting a multi-agent prototype running quickly, especially for teams with limited ML engineering depth.

---

### AutoGen (Microsoft)

**Architecture:** Conversational multi-agent. Agents communicate by sending messages to each other, like a chat. An agent is a participant in a conversation; its actions are messages; its inputs are messages it receives.

**Strengths:**
- Strong research pedigree (Microsoft Research)
- The conversational metaphor is intuitive for many developers
- `AutoGen 0.4` introduced event-driven, asynchronous communication — significant architecture improvement
- Well-suited for human-in-the-loop patterns

**Weaknesses:**
- The conversational metaphor breaks down at scale: debugging a 10-agent conversation is extremely difficult
- Message passing overhead can be significant for high-throughput applications
- Asynchronous event-driven patterns in 0.4 are more powerful but more complex to reason about

**Best for:** Workflows where the human needs to interact with agents during execution, or where a conversational pattern is genuinely natural to the problem.

---

### OpenHands (formerly OpenDevin)

**Architecture:** AI software development agent in a sandboxed environment. The agent has access to a terminal, browser, and code editor — the same tools a human developer uses. It operates by executing shell commands, writing files, and browsing the web.

**Key data:**
- **188+ contributors** as of Q1 2026 — the largest open-source multi-agent development project
- The most direct open-source analog to Devin
- Reproducible evaluation on SWE-bench (provides a credible open-source comparison)

**Strengths:**
- The real environment (not a simulated one) improves generalization
- Active contributor community driving rapid improvement
- Open-source and reproducible — you can run the same evaluations they publish

**Weaknesses:**
- Requires significant infrastructure (Docker, sandboxed environments) to run reliably
- The full-environment approach is slower and more expensive than lighter-weight alternatives
- Security model is complex: giving an AI agent shell access is a meaningful security decision

**Best for:** Software development automation tasks where real environment interaction matters (running tests, installing dependencies, debugging runtime errors).

---

## 3.4 Choosing a Framework

The right framework depends on three factors:

**1. What kind of task?**

| Task type | Best fit |
|-----------|----------|
| Complex conditional workflows with many branching paths | LangGraph |
| Team-based tasks with clear role assignments | CrewAI |
| Human-in-the-loop or conversational coordination | AutoGen |
| Real software development (write/run/debug cycle) | OpenHands |
| Decision-making with adversarial review | Crucible |

**2. What's your team's background?**
LangChain familiarity → LangGraph. Python-fluent non-ML → CrewAI. Research background → AutoGen. Wants to contribute OSS → OpenHands.

**3. What are your observability requirements?**
If you need to audit every decision and understand why an agent took an action, LangGraph and Crucible are the strongest choices. If you need to understand what agents said to each other, AutoGen's message log is useful. CrewAI and OpenHands have improving but still limited observability.

---

## 3.5 The Composability Insight

Crucible is not a replacement for these frameworks — it's composable with them. The Debate Council pattern (4 personas, 3 rounds, adversarial scoring) could be embedded within a LangGraph workflow as a decision node. OpenHands could use Crucible to adjudicate ambiguous task interpretations before executing.

The pattern Crucible introduces — adversarial review at decision points — is applicable to any multi-agent system. The specific implementation in Crucible is one realization of that pattern.

---

## Key Concepts

- **Shared priors problem:** Multiple agents from the same model → correlated agreement, not independent verification
- **LangGraph:** Graph-based state machine; explicit control flow; best for complex conditional workflows
- **CrewAI:** Role-based teams; accessible API; best for rapid prototyping
- **AutoGen:** Conversational agents; human-in-the-loop; best when conversation is natural to the problem
- **OpenHands:** Real environment; 188+ contributors; best for development automation
- **Framework selection:** Task type, team background, and observability requirements drive the choice

---

## Hands-On Exercise

**Exercise 3.1: Diagram an existing workflow**

Take a workflow you do manually (a code review process, a research task, a deployment checklist) and diagram it as a multi-agent system:
- What are the specialized agents?
- What state do they share?
- What are the decision forks?
- Where would adversarial review add value?

**Exercise 3.2: Framework comparison**

Pick one of the four frameworks and run their "hello world" example. Document:
- Time to first working output
- What you had to understand to get there
- What you couldn't do that you wanted to

---

## Discussion Questions

1. The shared priors problem suggests that multi-agent systems built on the same base model may not provide genuine diversity. What would genuine epistemic diversity look like in an AI agent system?

2. OpenHands gives an AI agent shell access. What is the right threat model for this? What can go wrong? What mitigations make sense?

3. All four frameworks are open-source. What does that mean for their development trajectories? What are the incentive structures?

4. Crucible introduces "adversarial review" as a complement to these frameworks. What are the conditions under which adversarial review adds value vs. just adds cost?

---

## References

- LangGraph documentation and LangSmith blog (2025)
- CrewAI GitHub repository and documentation
- AutoGen 0.4 architecture documentation (Microsoft Research)
- OpenHands GitHub repository, contributor statistics Q1 2026
- Cognition AI Devin performance data (January 2026)
