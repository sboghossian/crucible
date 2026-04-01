"""Infrastructure or data migration planning team — DevOps & Infrastructure."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="migration_planner",
    description="Plans a complex migration (cloud, database, monolith to microservices, on-prem to cloud) with risk mitigation and rollback strategy.",
    category="DevOps & Infrastructure",
    tags=["migration", "cloud migration", "database migration", "devops", "infrastructure", "refactoring"],
    agents=[
        AgentSpec(
            name="Migration Analyst",
            role="Current state assessment and migration scope specialist",
            instructions=(
                "You are a migration analyst. Assess the current state: "
                "inventory of systems, services, and data stores to migrate, "
                "dependencies map (what talks to what?), "
                "technical debt and compatibility risks in the current system, "
                "data volume and quality assessment, "
                "compliance and regulatory constraints affecting the migration, "
                "and a complexity scoring matrix for each component (easy / medium / hard to migrate)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Migration Architect",
            role="Migration strategy and phasing specialist",
            instructions=(
                "You are a migration architect. Design: "
                "migration strategy (big bang vs. strangler fig vs. parallel run vs. blue-green), "
                "migration phases with milestones, "
                "cutover sequence for interdependent systems, "
                "data migration approach (bulk load, CDC / change data capture, dual-write), "
                "feature flag strategy for gradual traffic shifting, "
                "and the Minimum Viable Migration — what must succeed for Phase 1 to be declared done?"
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Risk Manager",
            role="Migration risk identification and mitigation specialist",
            instructions=(
                "You are a migration risk manager. Identify: "
                "top 10 migration risks (data loss, extended downtime, performance regression, "
                "integration failures, team skill gaps, scope creep), "
                "risk severity and probability matrix, "
                "mitigation strategy for each risk, "
                "rollback plan (how to undo each phase if something goes wrong), "
                "and go/no-go decision criteria for each migration milestone."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Testing Strategist",
            role="Migration validation and acceptance testing specialist",
            instructions=(
                "You are a migration testing specialist. Design: "
                "pre-migration baseline capture (performance benchmarks, data checksums), "
                "data validation approach (row counts, checksums, sample comparison), "
                "functional regression test suite for post-migration validation, "
                "performance benchmarking plan (before vs. after comparison), "
                "user acceptance testing approach, "
                "and migration dress rehearsal plan (how to test the cutover before the real thing)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "Which migration strategy minimizes risk while maximizing speed?",
        "Big bang (single cutover, short total project time, highest risk)",
        "Strangler fig (incremental, lowest risk per change, longest calendar time)",
        "Parallel run (run old and new simultaneously, validate before cutover, highest cost)",
        "Blue-green deployment (instant cutover with instant rollback, requires double infrastructure)",
    ],
    expected_outputs=[
        "Current state inventory and dependency map",
        "Component complexity scoring matrix",
        "Migration strategy recommendation with phases",
        "Data migration approach",
        "Top 10 risk matrix with mitigations",
        "Rollback plan per phase",
        "Go/no-go decision criteria",
        "Migration dress rehearsal plan",
    ],
))
