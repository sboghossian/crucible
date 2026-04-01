"""Customer onboarding playbook team — Customer Success."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="onboarding_playbook",
    description="Designs a structured customer onboarding playbook that drives fast time-to-value and sets the foundation for long-term retention.",
    category="Customer Success",
    tags=["onboarding", "customer success", "time to value", "saas", "implementation", "retention"],
    agents=[
        AgentSpec(
            name="Journey Mapper",
            role="Customer onboarding journey and milestone specialist",
            instructions=(
                "You are a customer success architect. Map the ideal onboarding journey: "
                "onboarding phases (kickoff → setup → first value → adoption → graduation), "
                "milestone definitions (what observable event marks each phase transition?), "
                "time-to-value target (how many days/weeks to first meaningful outcome?), "
                "customer-side roles needed for successful onboarding, "
                "common onboarding failure modes (and early warning signs), "
                "and a 'graduation' checklist (criteria for transitioning from onboarding to ongoing CSM)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Kickoff Designer",
            role="Onboarding kickoff and expectation-setting specialist",
            instructions=(
                "You are an onboarding kickoff specialist. Design: "
                "kickoff call agenda (60 minutes: introductions, business goals, success metrics, "
                "implementation plan, stakeholder mapping, Q&A), "
                "pre-kickoff survey to gather context before the call, "
                "kickoff deck outline (10 slides), "
                "RACI matrix template for the implementation, "
                "and mutual success plan template (goals, milestones, owners, target dates, done criteria)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Enablement Designer",
            role="Customer education and self-service specialist",
            instructions=(
                "You are a customer education specialist. Build: "
                "onboarding email sequence (Day 1, 3, 7, 14, 21, 30 — each with specific action and value), "
                "product tour checklist (key features to adopt in the first 30 days), "
                "self-service resource library structure (getting started guides, videos, FAQs), "
                "in-app onboarding flow recommendations (tooltips, checklists, empty states), "
                "training session agenda for the admin and end users, "
                "and a 'champion enablement kit' to help the internal champion drive adoption."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Health Tracker",
            role="Onboarding health monitoring specialist",
            instructions=(
                "You are an onboarding analytics specialist. Design: "
                "onboarding health metrics (adoption milestones completed %, login frequency, feature activation), "
                "at-risk onboarding signals (no login in 7 days, kickoff missed, champion unresponsive), "
                "automated alert triggers for CSM intervention, "
                "EBR (Executive Business Review) trigger for stalled onboardings, "
                "and a 30/60/90-day onboarding report template for the customer."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
    ],
    debate_topics=[
        "Should onboarding be high-touch human-led or low-touch product-led?",
        "High-touch (CSM-led calls and check-ins — best for enterprise, complex implementations)",
        "Product-led (in-app guidance and email sequences — scalable, best for SMB)",
        "Segment-based (enterprise gets high-touch, SMB gets PLG, mid-market gets hybrid)",
    ],
    expected_outputs=[
        "Onboarding journey map with phase definitions",
        "Time-to-value target and graduation criteria",
        "Kickoff call agenda and pre-kickoff survey",
        "Mutual success plan template",
        "Day 1-30 onboarding email sequence",
        "In-app onboarding flow recommendations",
        "Onboarding health metrics and alert triggers",
        "30/60/90-day onboarding report template",
    ],
))
