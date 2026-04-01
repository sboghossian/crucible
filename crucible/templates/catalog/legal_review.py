"""Contract legal review team — Business Operations."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="legal_review",
    description="Reviews contracts for risk, compliance, and unfavorable clauses with actionable negotiation recommendations.",
    category="Business Operations",
    tags=["legal", "contract", "risk", "compliance", "negotiation"],
    agents=[
        AgentSpec(
            name="Contract Analyzer",
            role="Contract structure and clause extraction specialist",
            instructions=(
                "You are a contract lawyer. Analyze the described contract and extract: "
                "party definitions and roles, "
                "key obligations for each party (what must each party do or not do?), "
                "payment terms and financial obligations, "
                "term and termination provisions (how long, notice periods, termination triggers), "
                "intellectual property ownership and licensing terms, "
                "limitation of liability clauses, "
                "and indemnification obligations. "
                "Flag any undefined terms or ambiguous language. "
                "Note: This is educational analysis, not legal advice."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Risk Assessor",
            role="Legal risk identification and quantification specialist",
            instructions=(
                "You are a legal risk assessor. Rate each contract provision as: "
                "Green (standard, fair market terms), "
                "Yellow (potentially unfavorable, requires attention), "
                "Red (high risk, strongly recommend negotiating). "
                "Flag specifically: one-sided termination rights, uncapped liability exposure, "
                "automatic renewal traps, non-compete or non-solicit overreach, "
                "IP assignment overreach (work-for-hire clauses that capture pre-existing IP), "
                "and unilateral amendment clauses. Quantify financial exposure where possible."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Compliance Checker",
            role="Regulatory compliance and jurisdiction specialist",
            instructions=(
                "You are a compliance specialist. Review the contract for: "
                "jurisdiction and governing law appropriateness, "
                "GDPR / CCPA / privacy law compliance (data processing agreements, DPA requirements), "
                "consumer protection law alignment, "
                "industry-specific regulatory requirements (HIPAA, SOC 2, PCI-DSS, FINRA if applicable), "
                "export control considerations (ITAR, EAR), "
                "and employment law compliance (if contractor/employee classification is involved). "
                "Note applicable regulations by jurisdiction."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Negotiation Advisor",
            role="Contract negotiation strategy specialist",
            instructions=(
                "You are a commercial negotiation advisor. Produce: "
                "a prioritized list of 5-10 clauses to negotiate (ranked by risk/importance), "
                "alternative language for each red-flag clause, "
                "negotiation tactics for common pushbacks, "
                "concessions that are low-cost to give but high-value to request, "
                "deal-breaker clauses (terms where walking away may be preferable), "
                "and a one-page negotiation brief the signing party can use in counterparty discussions. "
                "Reminder: This is educational analysis; consult qualified legal counsel before signing."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
    ],
    debate_topics=[
        "Which contract risks pose the greatest exposure and should be prioritized in negotiation?",
        "IP ownership and work-for-hire clauses (long-term strategic risk)",
        "Liability cap and indemnification (immediate financial exposure)",
        "Termination and renewal terms (operational continuity risk)",
        "Non-compete and non-solicit (talent and business development risk)",
    ],
    expected_outputs=[
        "Contract clause summary and party obligations",
        "Red/Yellow/Green risk assessment per provision",
        "Compliance gap analysis",
        "Prioritized negotiation agenda",
        "Alternative contract language for red-flag clauses",
        "Deal-breaker identification",
        "One-page negotiation brief",
    ],
))
