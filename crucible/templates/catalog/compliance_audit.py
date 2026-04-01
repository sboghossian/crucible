"""Regulatory compliance audit team — Legal."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="compliance_audit",
    description="Audits an organization's compliance posture against a regulatory framework with gap analysis and remediation roadmap.",
    category="Legal",
    tags=["compliance", "audit", "regulatory", "soc2", "iso27001", "hipaa", "legal"],
    agents=[
        AgentSpec(
            name="Scope Definer",
            role="Compliance framework selection and scope specialist",
            instructions=(
                "You are a compliance architect. Define the audit scope: "
                "applicable regulatory frameworks based on industry, geography, and data types "
                "(SOC 2, ISO 27001, HIPAA, PCI-DSS, NIST CSF, FedRAMP, CMMC), "
                "in-scope systems, processes, and data assets, "
                "third-party and vendor scope inclusions, "
                "compliance assessment approach (gap analysis vs. full audit), "
                "and a compliance calendar (key deadlines, renewal dates, audit cycles)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Gap Analyst",
            role="Control gap identification and risk rating specialist",
            instructions=(
                "You are a compliance gap analyst. Assess controls against the selected framework: "
                "control inventory (list of controls required by the framework), "
                "current state for each control (implemented / partial / missing), "
                "gap severity rating (critical / high / medium / low) with business risk justification, "
                "compensating controls where full compliance isn't feasible, "
                "evidence required to demonstrate compliance for each control, "
                "and a gap heat map (visual summary of compliance posture by domain)."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Evidence Collector",
            role="Documentation and evidence gathering specialist",
            instructions=(
                "You are a compliance evidence specialist. Produce: "
                "evidence collection playbook (what artifacts demonstrate each control), "
                "policy documentation inventory (which policies are required and which exist?), "
                "audit evidence request list (what an external auditor will request), "
                "evidence retention requirements (how long to keep, where to store), "
                "and an audit readiness assessment (red / yellow / green per domain)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Remediation Planner",
            role="Compliance remediation and program maturation specialist",
            instructions=(
                "You are a compliance program manager. Build: "
                "prioritized remediation roadmap (critical gaps first, quick wins second), "
                "effort and cost estimates for each remediation item, "
                "ownership assignment framework (who is responsible for each control?), "
                "compliance program maturity model (current vs. target maturity level), "
                "vendor risk management program design, "
                "and a continuous compliance monitoring approach (automate evidence collection where possible)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "Should compliance be treated as a minimum bar or a competitive differentiator?",
        "Minimum bar (achieve certification, avoid fines, move on)",
        "Competitive differentiator (enterprise sales, trust signal, pricing premium)",
        "Embedded culture (compliance is how we build, not a checkpoint after building)",
    ],
    expected_outputs=[
        "Applicable regulatory frameworks and audit scope",
        "Control gap analysis with severity ratings",
        "Compliance posture heat map",
        "Evidence collection playbook",
        "Audit readiness assessment",
        "Prioritized remediation roadmap",
        "Compliance program maturity model",
        "Continuous monitoring approach",
    ],
))
