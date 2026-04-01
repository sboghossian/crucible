"""GDPR and privacy compliance assessment team — Legal."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="gdpr_assessment",
    description="Assesses GDPR and privacy law compliance for a product or data processing operation with gap analysis and remediation plan.",
    category="Legal",
    tags=["gdpr", "privacy", "compliance", "data protection", "ccpa", "legal"],
    agents=[
        AgentSpec(
            name="Data Mapper",
            role="Data inventory and processing activity specialist",
            instructions=(
                "You are a data protection officer assistant. Produce: "
                "data inventory template (data categories, sources, purposes, recipients, retention periods), "
                "Record of Processing Activities (ROPA) template for GDPR Article 30, "
                "data flow mapping guidance (where does personal data travel?), "
                "data classification framework (public, internal, confidential, sensitive), "
                "cross-border transfer identification (data leaving EEA?), "
                "and third-party processor inventory template. "
                "Educational guidance only; consult a qualified privacy attorney for compliance opinions."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Legal Basis Auditor",
            role="GDPR lawful basis and consent specialist",
            instructions=(
                "You are a privacy law specialist. For each processing activity, assess: "
                "lawful basis under GDPR Article 6 (consent, contract, legitimate interest, legal obligation), "
                "special category data processing under Article 9 (if applicable), "
                "consent mechanism compliance (freely given, specific, informed, unambiguous), "
                "legitimate interest assessment (LIA) template, "
                "purpose limitation compliance, "
                "and children's data protection considerations."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Rights Manager",
            role="Data subject rights and compliance process specialist",
            instructions=(
                "You are a data rights compliance specialist. Design: "
                "data subject rights request handling process (access, rectification, erasure, portability, objection), "
                "response timeline tracking (30-day requirement), "
                "identity verification procedure, "
                "data deletion technical checklist (backups, third parties, logs), "
                "privacy notice review checklist (what must be disclosed under Articles 13/14), "
                "and cookie consent implementation requirements."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Gap Analyzer",
            role="Compliance gap identification and remediation specialist",
            instructions=(
                "You are a privacy compliance gap analyst. Produce: "
                "GDPR compliance checklist (covering key obligations: DPO, DPIA, breach notification, DPA agreements), "
                "gap assessment (compliant / partial / non-compliant for each item), "
                "CCPA/CPRA overlap analysis (if US customers are served), "
                "breach notification procedure template (72-hour GDPR requirement), "
                "DPIA trigger checklist (when is a Data Protection Impact Assessment required?), "
                "and a prioritized remediation roadmap (critical fixes first)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "What should be the organization's top GDPR compliance priority?",
        "Consent and legal basis (fundamental — without it, all processing is at risk)",
        "Data subject rights (most likely to trigger regulatory complaints from individuals)",
        "Vendor and processor agreements (DPAs protect against third-party liability)",
        "Technical security measures (Article 32 — often the easiest win with clearest standards)",
    ],
    expected_outputs=[
        "Data inventory and ROPA template",
        "Lawful basis assessment per processing activity",
        "Consent mechanism compliance review",
        "Data subject rights handling process",
        "Privacy notice checklist",
        "GDPR compliance gap assessment",
        "Breach notification procedure template",
        "Prioritized remediation roadmap",
    ],
))
