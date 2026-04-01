# Crucible Roadmap

10 milestones across 3 phases. Each item includes what it is, why it matters, technical approach, complexity, and dependencies.

---

## Phase 1 — Real-Time Experience (v0.2)

Goal: make Crucible feel alive. Debates happen in real-time, results are visual, and every decision point is rewindable.

---

### 1.1 Streaming Output

**What it is:** Token-by-token streaming of debate output to the terminal (and eventually the Web UI). Users watch each persona's argument develop live rather than waiting for a complete response.

**Why it matters:** Debates can take 30–90 seconds. Streaming converts a frustrating wait into an engaging experience. It also surfaces reasoning in progress — users spot model errors mid-argument and can interrupt runs before they complete wastefully.

**Technical approach:**
- Replace blocking `client.messages.create()` calls with `client.messages.stream()` in `DebateCouncil`
- Emit `token` events on the `EventBus` per persona per round
- Buffer and flush to stdout with ANSI color coding per persona (Pragmatist=blue, Visionary=green, Skeptic=red, User Advocate=yellow)
- Add `stream=True` parameter to `standalone_debate()` for opt-in behavior

**Complexity:** S

**Dependencies:** None — standalone enhancement to existing API calls.

---

### 1.2 Web UI

**What it is:** A local web interface (served at `localhost:7823`) that displays live debate transcripts with persona timelines, round-by-round argument cards, and a scoring visualization. No cloud dependency — runs fully local.

**Why it matters:** Terminal output loses structure. The Web UI preserves the debate as a readable artifact: who said what, when, which argument won and by how much. It's the difference between a log file and a research instrument.

**Technical approach:**
- Lightweight Python server: FastAPI + WebSocket for live updates
- Frontend: single-file HTML + Alpine.js + Tailwind CDN (no build step)
- Debate state streamed over WebSocket as structured JSON events
- Persona cards with argument text, round indicator, and score badge
- Timeline bar at top showing round progression and winner announcement
- `crucible serve` CLI command to launch the UI server before a run

**Complexity:** M

**Dependencies:** 1.1 (Streaming Output) — the UI consumes the same event stream.

---

### 1.3 Debate Replay and Branching

**What it is:** Serialize every debate to disk (SQLite or JSON). The CLI gains `crucible replay <run-id>` to re-render any past debate, and `crucible branch <run-id> --at round2 --persona skeptic` to fork from any decision point with modified inputs.

**Why it matters:** Adversarial review is only useful if you can learn from it over time. Replay lets you audit past decisions. Branching lets you answer "what if we'd framed the question differently?" or "what if we swapped the Skeptic persona for a Domain Expert?" — turning one debate into a research experiment.

**Technical approach:**
- Extend `SharedState` with a `run_id` (UUID) and `serialize()` method
- Write debate snapshots to `~/.crucible/runs/<run-id>.json` at end of each round
- `ReplayEngine`: loads a snapshot, reconstructs `SharedState`, re-renders through the UI
- `BranchEngine`: loads a snapshot at a specific round, allows persona/prompt substitution, re-runs from that point forward
- New `RunIndex` (SQLite table): `run_id`, `timestamp`, `topic`, `winner`, `score` — queryable via `crucible history`

**Complexity:** M

**Dependencies:** 1.1 (Streaming Output), 1.2 (Web UI optional but strongly recommended).

---

## Phase 2 — Extensibility (v0.3)

Goal: make Crucible a platform, not just a tool. Anyone can define agents, personas, and multi-stage pipelines without touching core code.

---

### 2.1 Plugin API

**What it is:** A `@crucible.agent` decorator that registers a custom agent class into the Crucible runtime. Hot-reload support for development — edit an agent file, see changes without restarting the process.

**Why it matters:** The current agent set (Scanner, Research, Debate Council, etc.) is fixed. Real-world use cases demand specialists — a SecurityAuditor, a LegalReviewer, a DomainExpert. The Plugin API lets users build and share these without forking the repo.

**Technical approach:**
- `AgentRegistry` singleton: maps agent names to classes, loaded at startup
- `@crucible.agent(name="my_agent", category="analysis")` decorator registers a class that extends `BaseAgent`
- Plugin discovery: scan `~/.crucible/plugins/` for `*.py` files on startup
- Hot-reload: `watchdog` file watcher on the plugins directory; on change, reload the module and re-register
- `crucible plugins list` — show all registered agents with source and status
- Plugin manifest: `plugin.yaml` with name, version, author, required inputs/outputs

**Complexity:** M

**Dependencies:** None — extends existing `BaseAgent` interface.

---

### 2.2 Custom Persona Definitions

**What it is:** YAML/JSON files that define debate personas — name, structural bias, scoring weights, system prompt template, and behavioral constraints. Drop a `.yaml` file into `~/.crucible/personas/` and it becomes available in any debate.

**Why it matters:** The four default personas (Pragmatist, Visionary, Skeptic, User Advocate) are general-purpose. Domain-specific debates need domain-specific biases: a Medical Reviewer who weights evidence quality at 70%, a Regulator who weights compliance first. Custom personas unlock Crucible for vertical domains.

**Technical approach:**
- `PersonaConfig` Pydantic model: `name`, `bias_description`, `scoring_weights` (dict), `system_prompt_template`, `temperature`, `behavioral_flags`
- `PersonaLoader`: reads YAML/JSON from `~/.crucible/personas/` and built-in `crucible/personas/` directory
- `DebateCouncil` updated to accept a `personas: list[PersonaConfig]` parameter
- Validation: scoring weights must sum to 1.0; required fields enforced by Pydantic
- `crucible personas list` — show all available personas with source
- `crucible debate --personas "pragmatist,my_domain_expert,skeptic,user_advocate"` CLI flag

**Complexity:** S

**Dependencies:** None — standalone extension to `DebateCouncil`.

---

### 2.3 Template Composer

**What it is:** A pipeline DSL that chains multiple templates into multi-stage workflows. Example: `Research → Spec → Build → Test` where each stage receives the outputs of the previous as structured context.

**Why it matters:** Current templates are single-stage. Real projects have phases. A `product_launch` pipeline needs market research, then a spec, then implementation planning, then a QA strategy — each stage informed by the last. The Template Composer makes this composable without custom code.

**Technical approach:**
- `Pipeline` class: ordered list of `PipelineStage` objects, each wrapping a template
- `PipelineStage`: template name, input mapping (which outputs from prior stages to inject), output schema
- YAML pipeline definition:
  ```yaml
  name: product_launch
  stages:
    - template: market_research
      outputs: [market_overview, competitors]
    - template: product_spec
      inputs: {market_context: "$market_research.market_overview"}
    - template: web_app
      inputs: {spec: "$product_spec.prd"}
  ```
- `PipelineRunner`: executes stages sequentially, resolves `$stage.output` references, passes structured context
- `crucible pipeline run product_launch --subject "..."` CLI command
- Pipeline outputs stored as a structured run artifact alongside individual stage outputs

**Complexity:** L

**Dependencies:** 2.1 (Plugin API) for stage extensibility; existing template system.

---

### 2.4 Template Versioning and Community Submissions

**What it is:** Semantic versioning for templates (`seo_article@1.2.0`), a PR-based submission flow for community-contributed templates, and automated quality gates that every submission must pass before merging.

**Why it matters:** The current 65-template marketplace has no version contract. Community contributions need a trustworthy path — quality gates prevent noise, semantic versioning lets users pin to known-good versions, and a clear submission flow makes contributing accessible.

**Technical approach:**
- Add `version` field to template manifests (semver string)
- `TemplateRegistry` updated to support `name@version` lookups and fallback to latest
- Community submission flow via GitHub PR template in `templates/community/`
- Automated quality gates (GitHub Actions):
  1. Schema validation (required fields present, valid types)
  2. Smoke test (deploys template with mock API, checks output structure)
  3. Naming uniqueness check
  4. Peer review requirement (2 maintainer approvals)
- `crucible templates update` — pulls latest community templates from the registry
- Deprecation policy: templates with `deprecated: true` emit a warning but still run for 2 minor versions

**Complexity:** M

**Dependencies:** Existing template system; GitHub Actions CI.

---

## Phase 3 — Intelligence (v0.4)

Goal: give Crucible a memory and real-world awareness. Debates draw on live information. Every run builds institutional knowledge that improves future runs.

---

### 3.1 Live Web Search Integration

**What it is:** During a debate or research run, agents can issue web search queries to pull real-time data — pricing, benchmarks, recent papers, market news — and incorporate findings into their arguments with citations.

**Why it matters:** Static knowledge has a cutoff date. Debates about technology choices, market strategy, or competitive positioning need current data. An agent arguing for PostgreSQL should be able to cite the latest benchmark numbers, not training data from 18 months ago.

**Technical approach:**
- `SearchTool` abstraction: pluggable backend (default: Brave Search API; fallback: DuckDuckGo)
- `SearchResult` model: `query`, `url`, `title`, `snippet`, `retrieved_at`
- Tool-use integration: agents emit `search_request` events; `SearchTool` resolves them and injects results into the agent's next prompt as structured context
- Rate limiting: max 3 searches per agent per round; deduplicated by query hash
- Citation tracking: every fact sourced from a search result is tagged with its `url` and `retrieved_at`; citations appear in the debate transcript and final report
- Configurable: `search=True` parameter on `standalone_debate()` and Orchestrator; opt-out for offline/cost-sensitive runs

**Complexity:** M

**Dependencies:** None — additive capability via tool use.

---

### 3.2 SQLite Memory Persistence Across Runs

**What it is:** Every debate, agent output, decision, and cross-run learning is persisted to a local SQLite database at `~/.crucible/memory.db`. The Learning Agent accumulates institutional knowledge that influences future runs on related topics.

**Why it matters:** The current `MemoryStore` is in-memory and ephemeral. This means every run starts from zero. Persistence enables: "what did we decide last time about this architecture?", trend analysis across runs, and genuine cross-run learning where past mistakes and successful patterns inform current debates.

**Technical approach:**
- Schema: `runs`, `debate_rounds`, `agent_outputs`, `memories`, `patterns` tables
- `PersistentMemoryStore` extends current `MemoryStore` with SQLite backend via `aiosqlite`
- Write path: all `EventBus` events are fanned out to `MemoryWriter` which persists to SQLite
- Read path: `LearningAgent` queries `memories` and `patterns` tables at run start; injects relevant prior context into agent system prompts
- `crucible memory search "microservices"` — semantic search over past debates
- `crucible memory stats` — run count, decision history, top patterns
- Configurable retention: default 90 days; `crucible memory prune --older-than 30d`
- Privacy: all data stays local; no cloud sync

**Complexity:** M

**Dependencies:** 1.3 (Debate Replay) shares the storage layer.

---

### 3.3 Agent Society Phase 2

**What it is:** Full implementation of the persistent-identity society layer specified in [docs/architecture/agent-society-spec.md](architecture/agent-society-spec.md). Agents accumulate XP, develop relationships, exhibit personality drift, and compress shared concepts into emergent tokens.

**Why it matters:** Phase 1 agents are stateless workers. Phase 2 agents are persistent entities. A Skeptic who has reviewed 50 codebases develops different intuitions than one on its first run. An agent pair that has collaborated 20 times develops communication shortcuts. This is the difference between a tool and a research community.

**Technical approach:**
- `AgentIdentity`: persistent record with `agent_id`, `xp`, `personality_vector` (5D), `relationship_graph`, `emergent_vocabulary`
- XP economy: teaching = 20 XP, learning = 5 XP, correct prediction = 15 XP, wrong = -5 XP
- Personality drift: `personality_vector` shifts ±0.02 per cycle toward reinforced traits; hard cap at ±0.3 from baseline
- Relationship graph: edge weights updated after each collaboration; high-weight pairs unlock shared prompt compression tokens
- Emergent vocabulary: agent pairs that repeatedly co-occur develop shorthand tokens (tracked as `(agent_a, agent_b, token, meaning)` tuples); injected into shared context
- Safety enforcement: personality drift rate and XP swing limits are architectural constants, not configurable — safety as physics
- Full spec: [docs/architecture/agent-society-spec.md](architecture/agent-society-spec.md)

**Complexity:** XL

**Dependencies:** 3.2 (SQLite Memory Persistence) — identity and XP state must be persistent.

---

## Summary Table

| # | Item | Phase | Complexity | Depends On |
|---|------|-------|------------|------------|
| 1.1 | Streaming Output | v0.2 | S | — |
| 1.2 | Web UI | v0.2 | M | 1.1 |
| 1.3 | Debate Replay & Branching | v0.2 | M | 1.1 |
| 2.1 | Plugin API | v0.3 | M | — |
| 2.2 | Custom Persona Definitions | v0.3 | S | — |
| 2.3 | Template Composer | v0.3 | L | 2.1 |
| 2.4 | Template Versioning & Community Submissions | v0.3 | M | — |
| 3.1 | Live Web Search Integration | v0.4 | M | — |
| 3.2 | SQLite Memory Persistence | v0.4 | M | 1.3 |
| 3.3 | Agent Society Phase 2 | v0.4 | XL | 3.2 |

---

## Contributing to the Roadmap

Open an issue tagged `roadmap` to propose new items. Items get prioritized through a Debate Council run — the four personas argue the merits and a winning priority is recorded.
