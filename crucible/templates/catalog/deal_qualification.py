"""Deal qualification team — Sales."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="deal_qualification",
    description="Qualifies a sales opportunity using structured frameworks (MEDDIC, BANT, SPICED) and produces a pursuit decision.",
    category="Sales",
    tags=["sales", "qualification", "meddic", "bant", "pipeline", "deal review"],
    agents=[
        AgentSpec(
            name="MEDDIC Assessor",
            role="Metrics, Economic Buyer, Decision process analyst",
            instructions=(
                "You are a sales qualification specialist. Assess the deal using MEDDIC: "
                "Metrics (what quantifiable value does the buyer expect?), "
                "Economic Buyer (who controls the budget and has final authority?), "
                "Decision Criteria (what is the explicit evaluation criteria?), "
                "Decision Process (what are the steps from verbal to signed?), "
                "Identify Pain (what is the compelling event or business pain driving urgency?), "
                "Champion (who wants us to win and has the internal influence to make it happen?). "
                "Rate each dimension: Strong / Partial / Missing."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Risk Analyst",
            role="Deal risk and competitive threat specialist",
            instructions=(
                "You are a deal risk analyst. Identify: "
                "competitive risk (who else are they evaluating?), "
                "political risk (are there stakeholders we haven't accessed?), "
                "timing risk (is the stated timeline realistic or likely to slip?), "
                "budget risk (is the budget approved or speculative?), "
                "technical risk (are there implementation or integration risks?), "
                "and champion risk (how embedded and credible is our internal champion?). "
                "Rate each risk: Low / Medium / High."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Win Strategy Designer",
            role="Deal strategy and pursuit plan specialist",
            instructions=(
                "You are a strategic sales coach. Design the win strategy: "
                "our unfair advantages in this deal (where do we win?), "
                "gaps to close before close (what's missing that could kill the deal?), "
                "next 3 actions to advance the opportunity, "
                "stakeholders to access and how to reach them, "
                "proof of value approach (pilot, reference call, demo customization), "
                "and concession strategy (what can we give to close?)."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Qualification Advisor",
            role="Pursue/no-pursue recommendation specialist",
            instructions=(
                "You are a VP of Sales. Based on the MEDDIC assessment and risk analysis, produce: "
                "overall qualification score (0-100), "
                "pursue / pursue with conditions / no-pursue recommendation with rationale, "
                "conditions required before committing full sales resources, "
                "forecast category recommendation (commit, best case, pipeline), "
                "and a 30-day milestone plan to validate remaining unknowns."
            ),
            config=AgentConfig(max_tokens=1500),
        ),
    ],
    debate_topics=[
        "Should we commit full resources to this deal or pursue conditionally?",
        "Full pursuit (high qualification score, strong champion, clear path to close)",
        "Conditional pursuit (promising but key MEDDIC gaps need closing first)",
        "Deprioritize (low qualification, better opportunities should get resources)",
    ],
    expected_outputs=[
        "MEDDIC assessment with dimension ratings",
        "Deal risk matrix",
        "Win strategy with next 3 actions",
        "Overall qualification score (0-100)",
        "Pursue / no-pursue recommendation",
        "Forecast category assignment",
        "30-day validation milestone plan",
    ],
))
