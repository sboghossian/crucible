"""Quarterly Business Review (QBR) preparation team — Customer Success."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="qbr_prep",
    description="Prepares a compelling QBR for a B2B customer with business reviews, ROI documentation, and expansion planning.",
    category="Customer Success",
    tags=["qbr", "business review", "customer success", "renewal", "expansion", "b2b"],
    agents=[
        AgentSpec(
            name="Data Gatherer",
            role="Customer usage and value realization analyst",
            instructions=(
                "You are a customer analytics specialist. Compile: "
                "product usage summary (active users, feature adoption, engagement trends vs. prior quarter), "
                "value delivered metrics (outcomes achieved against stated success criteria), "
                "support ticket summary (volume, resolution time, recurring issues), "
                "ROI achieved vs. promised at sale, "
                "and benchmark data (how does this customer compare to peers using the same solution?)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Agenda Designer",
            role="QBR structure and narrative specialist",
            instructions=(
                "You are a QBR facilitation expert. Design: "
                "60-90 minute QBR agenda (welcome, their business update, what's working, "
                "what needs work, roadmap preview, expansion conversation, Q&A, next steps), "
                "slide deck outline (10-12 slides: cover, agenda, their goals recap, progress, "
                "value summary, challenges and responses, product roadmap, growth opportunities, next steps), "
                "customer business update questions (ask before the meeting to customize the agenda), "
                "and facilitator notes for each section."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Value Storyteller",
            role="ROI documentation and success story specialist",
            instructions=(
                "You are a customer value documentation specialist. Create: "
                "value realization narrative (from initial problem → implementation → results), "
                "quantified ROI statement with before/after comparison, "
                "customer success story outline (for internal marketing with their permission), "
                "quote extraction guide (how to identify and request a testimonial quote during the QBR), "
                "and a case study template pre-populated with available data."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Expansion Planner",
            role="Upsell and cross-sell opportunity specialist",
            instructions=(
                "You are a CS expansion strategist. Identify: "
                "expansion signals in the account (growing team, new use cases mentioned, feature requests), "
                "upsell opportunities (tier upgrade, additional seats, premium features), "
                "cross-sell opportunities (adjacent products or services they're not using), "
                "expansion talk track (how to introduce growth conversation without it feeling like a sales pitch), "
                "expansion proposal structure (if ready to formalize), "
                "and multi-year renewal incentive framework."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
    ],
    debate_topics=[
        "What should be the primary objective of this QBR?",
        "Secure the renewal (health is at risk, renewal is the priority conversation)",
        "Drive expansion (healthy account, focus on growing the footprint)",
        "Strengthen the relationship (new champion, rebuild trust and demonstrate value)",
        "Capture a case study (maximize reference and marketing value from a successful account)",
    ],
    expected_outputs=[
        "60-90 minute QBR agenda",
        "10-12 slide deck outline",
        "Usage and value realization summary",
        "Quantified ROI statement",
        "Success story narrative",
        "Expansion opportunity plan",
        "Renewal conversation talk track",
        "Post-QBR follow-up email template",
    ],
))
