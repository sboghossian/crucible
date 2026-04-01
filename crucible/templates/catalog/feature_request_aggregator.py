"""Feature request aggregation and prioritization team — Customer Success."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="feature_request_aggregator",
    description="Aggregates, de-duplicates, and prioritizes customer feature requests into an actionable product input for roadmap planning.",
    category="Customer Success",
    tags=["feature requests", "product feedback", "roadmap", "customer success", "prioritization"],
    agents=[
        AgentSpec(
            name="Request Collector",
            role="Feature request capture and normalization specialist",
            instructions=(
                "You are a product feedback analyst. From the raw feature requests, produce: "
                "normalized request inventory (de-duplicate variations of the same request), "
                "request source tagging (support ticket, QBR, Slack, NPS comment, sales call), "
                "customer tagging (which customers and their ARR/tier requested each feature), "
                "request categorization (UI/UX, integrations, performance, reporting, core functionality), "
                "and verbatim quote preservation (capture the customer's own words for the product team)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Prioritization Analyst",
            role="Feature impact and prioritization scoring specialist",
            instructions=(
                "You are a product prioritization specialist. Score each feature request: "
                "revenue impact (ARR of requesting customers × likelihood they churn without it), "
                "frequency (how many customers requested this?), "
                "strategic alignment (does this support the product vision?), "
                "acquisition impact (is this blocking new customer acquisition?), "
                "competitive necessity (are we losing deals because of this gap?), "
                "and a RICE score (Reach × Impact × Confidence ÷ Effort) for top requests."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Pattern Analyst",
            role="Feature theme and underlying need specialist",
            instructions=(
                "You are a Jobs-to-be-Done analyst. Look beyond the requested features to identify: "
                "underlying jobs customers are trying to accomplish (the 'why' behind the 'what'), "
                "theme clusters (multiple requests that share a root cause), "
                "workflow gaps (features needed because of a missing step in the product journey), "
                "integration-driven requests (requests that reveal ecosystem gaps), "
                "and the 3-5 most significant unmet needs revealed by the request corpus."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Product Communicator",
            role="Feedback loop and customer communication specialist",
            instructions=(
                "You are a product communication specialist. Design: "
                "product team briefing memo (prioritized requests, business context, customer quotes), "
                "customer communication templates for each outcome "
                "(planned for roadmap, not planned with explanation, workaround offered), "
                "feature voting / NPS survey to validate prioritization with the broader customer base, "
                "and a changelog communication framework (how to announce when a requested feature ships)."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
    ],
    debate_topics=[
        "Should feature prioritization be driven by revenue at risk or strategic vision?",
        "Revenue at risk (protect the base — build what reduces churn for the biggest accounts)",
        "Strategic vision (build what wins new market segments, not just what pleases existing customers)",
        "Customer frequency (build what the most customers want, regardless of ARR)",
        "Competitive gaps (close the features losing us deals in the pipeline)",
    ],
    expected_outputs=[
        "De-duplicated feature request inventory with customer tagging",
        "RICE scores for top feature requests",
        "Underlying jobs-to-be-done analysis",
        "Revenue-at-risk calculation per feature",
        "Product team briefing memo",
        "Customer communication templates (planned/not planned/workaround)",
        "Feature voting survey",
    ],
))
