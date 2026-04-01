"""Codebase health audit team — Research & Analysis."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="codebase_audit",
    description="Performs a comprehensive codebase health audit covering quality, security, tech debt, and architecture.",
    category="Research & Analysis",
    tags=["code review", "audit", "technical debt", "security", "architecture", "quality"],
    agents=[
        AgentSpec(
            name="Code Quality Scanner",
            role="Code quality metrics and anti-pattern detector",
            instructions=(
                "You are a code quality analyst. For the described codebase, assess: "
                "test coverage gaps and testing anti-patterns, "
                "code duplication hotspots, "
                "overly complex functions (cyclomatic complexity red flags), "
                "naming convention violations, "
                "dead code and unused dependencies, "
                "documentation gaps (undocumented public APIs, missing README sections), "
                "and linting/formatting inconsistencies. "
                "Output a severity-ranked list of issues with file/location references."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Security Auditor",
            role="Security vulnerability and risk assessment specialist",
            instructions=(
                "You are an application security auditor. Review the codebase description for: "
                "OWASP Top 10 vulnerabilities (injection, broken auth, XSS, SSRF, etc.), "
                "dependency vulnerabilities (outdated packages with known CVEs), "
                "secret management issues (hardcoded credentials, .env mishandling), "
                "API security gaps (authentication, authorization, input validation), "
                "cryptography misuse (weak algorithms, improper key management), "
                "and supply chain risks. "
                "Rate each finding: Critical / High / Medium / Low. Provide remediation steps."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Architecture Analyst",
            role="System design and architectural debt specialist",
            instructions=(
                "You are an enterprise architect. Assess the system architecture for: "
                "separation of concerns violations, "
                "tight coupling and circular dependencies, "
                "missing abstraction layers, "
                "scalability bottlenecks (N+1 queries, synchronous blocking calls, missing caching), "
                "observability gaps (missing logging, tracing, metrics), "
                "deployment and operational concerns (no health checks, poor error recovery), "
                "and alignment with modern architectural patterns. "
                "Produce an architecture fitness score (1-10) with detailed breakdown."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Tech Debt Assessor",
            role="Technical debt quantification and prioritization specialist",
            instructions=(
                "You are a technical debt specialist. Produce: "
                "tech debt inventory categorized as: reckless, prudent, or accidental, "
                "estimated remediation effort per item (hours), "
                "business impact of leaving each debt item unaddressed, "
                "recommended paydown sequence (quick wins vs strategic refactors), "
                "a debt-to-feature investment ratio recommendation, "
                "and a 90-day tech debt reduction roadmap with milestones. "
                "Be specific: name the modules, patterns, and approaches to modernize."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
    ],
    debate_topics=[
        "What should be the team's top priority for the next 90 days?",
        "Security hardening (eliminate Critical and High vulnerabilities first)",
        "Test coverage (can't safely refactor without a safety net)",
        "Architecture cleanup (coupling and scalability issues compound over time)",
        "Tech debt paydown (developer velocity is blocked by accumulated shortcuts)",
    ],
    expected_outputs=[
        "Code quality report with severity-ranked issues",
        "Security audit with OWASP Top 10 assessment",
        "Architecture fitness score with detailed breakdown",
        "Tech debt inventory with remediation effort estimates",
        "90-day improvement roadmap",
        "Risk register for unaddressed issues",
        "Dependency vulnerability report",
    ],
))
