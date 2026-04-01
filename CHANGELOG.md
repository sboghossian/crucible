# Changelog

All notable changes to Crucible are documented here.

---

## [0.1.0] — 2026-04-01

### Added

**Core framework**
- `Orchestrator` — central coordinator that routes tasks to agents and manages run lifecycle
- `BaseAgent` + `AgentConfig` / `AgentResult` — typed base class for all agents; every result is logged, inspectable, and serializable
- `SharedState` / `RunState` — immutable-ish shared context passed across all agents in a run, with full event log
- `EventBus` — lightweight pub/sub for inter-agent communication without coupling

**Debate Council**
- Four-persona adversarial review protocol: Pragmatist, Visionary, Skeptic, Synthesizer
- Each persona carries a structural bias with explicit scoring weights — engineered differences, not emergent noise
- Three-round debate loop: opening positions → cross-examination → final arguments
- `DebateResolver` — scores arguments on evidence quality, logical consistency, practical feasibility, and novelty; produces a winner with dissenting views preserved
- `standalone_debate()` shortcut on `Orchestrator` for one-call use

**Agent types**
- `ResearchAgent` — retrieves and summarizes evidence from multiple sources
- `ScannerAgent` — static analysis of codebases; identifies structural issues, dependency risks, and quality signals
- `LearningAgent` — wraps any agent with a memory store; accumulates cross-run lessons

**Memory system**
- `MemoryStore` — persistent key-value store for agent memories; supports tagging, similarity search, and access-frequency decay
- Configurable retention policies per memory type

**Tests**
- 192 unit and integration tests across 5 test modules
- Full mock harness for the Anthropic API — no API key required to run tests
- `examples/analyze_projects.py` — end-to-end working example

**Documentation**
- `README.md` — quick start, architecture overview, empirical motivation
- `CONTRIBUTING.md` — contribution guide, code standards, PR process
- `docs/research/ai-coding-landscape-2026.md` — survey of the 2026 AI-assisted development landscape including the METR productivity study, the Claude Code leak, and vibe coding
- `docs/research/forecast-2027.md` — empirically grounded forecasts: the productivity paradox, autonomous agent trajectories, and the governance gap
- `docs/architecture/debate-council-deep-dive.md` — full protocol specification for the Debate Council
- `docs/architecture/agent-society-spec.md` — design spec for the persistent-identity Society layer (roadmap)
- `docs/launch-playbook.md` — distribution and community-building strategy
- `course/` — 10-module course: *The Developer's Edge in the Age of AI*

**CI/CD**
- GitHub Actions workflow: lint (ruff), type-check (mypy), test matrix (Python 3.11, 3.12)
- Issue templates for bugs and feature requests

---

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for the full roadmap with technical details, complexity estimates, and dependencies.

**Phase 1 — Real-Time Experience (v0.2)**
- Streaming output, Web UI, Debate replay and branching

**Phase 2 — Extensibility (v0.3)**
- Plugin API, Custom persona definitions, Template composer, Template versioning and community submissions

**Phase 3 — Intelligence (v0.4)**
- Live web search integration, SQLite memory persistence, Agent Society Phase 2

`v1.0` — PyPI stable release, versioned API contract
