"""Churn prediction and prevention team — Customer Success."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="churn_predictor",
    description="Identifies churn risk signals, builds a prediction framework, and designs intervention playbooks to save at-risk accounts.",
    category="Customer Success",
    tags=["churn", "customer success", "retention", "saas", "health score", "intervention"],
    agents=[
        AgentSpec(
            name="Risk Signal Analyst",
            role="Churn signal and health score design specialist",
            instructions=(
                "You are a customer success analyst. Define: "
                "leading indicators of churn (product usage decline, support ticket spike, champion departure, "
                "NPS drop, missed QBRs, slow response to outreach, contract stage mismatch), "
                "lagging indicators (non-renewal stated intent, competitor mentions, payment delays), "
                "customer health score formula (which signals, weights, and scoring thresholds), "
                "health score tiers (Red: churning, Yellow: at risk, Green: healthy), "
                "and data sources required for each signal (product analytics, CRM, support, billing)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Segmentation Strategist",
            role="Churn pattern and customer segment specialist",
            instructions=(
                "You are a revenue analytics specialist. Segment churn patterns: "
                "churn by customer size (SMB, mid-market, enterprise often churn for different reasons), "
                "churn by product usage pattern (power users rarely churn; what defines at-risk usage?), "
                "churn by tenure (first 90 days vs. renewal risk vs. long-tail churn), "
                "churn by industry or use case, "
                "voluntary vs. involuntary churn (cancellation vs. payment failure), "
                "and contraction analysis (downgrades before full churn)."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Intervention Designer",
            role="Churn prevention playbook specialist",
            instructions=(
                "You are a customer success playbook designer. Build: "
                "playbook for Red accounts (urgent: executive escalation, custom success plan, exec sponsor engagement), "
                "playbook for Yellow accounts (proactive: QBR acceleration, champion building, value realization review), "
                "early warning response protocol (who gets alerted, when, with what context), "
                "save offer framework (what to offer at risk of churn: discount, professional services, feature access), "
                "and post-churn win-back sequence (30/60/90-day re-engagement cadence)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Metrics Designer",
            role="Retention metrics and reporting specialist",
            instructions=(
                "You are a CS operations analyst. Design: "
                "retention metrics dashboard (gross retention, net retention, churn rate by cohort), "
                "cohort analysis framework (how does retention evolve from Month 1 to Month 24?), "
                "forecasted churn impact on ARR (at-risk ARR calculation), "
                "CS capacity planning (how many accounts per CSM based on churn risk?), "
                "and a monthly churn review cadence with agenda and stakeholder participants."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
    ],
    debate_topics=[
        "What is the highest-leverage churn reduction intervention?",
        "Improve onboarding (time-to-value reduction prevents early churn, which is hardest to recover)",
        "Proactive health score monitoring with automated alerts (catch churn before it's decided)",
        "Executive relationship building (champions change jobs; relationships prevent churn)",
        "Product stickiness features (usage-based retention is the most durable)",
    ],
    expected_outputs=[
        "Customer health score formula with signal weights",
        "Health score tiers (Red / Yellow / Green thresholds)",
        "Churn segmentation analysis framework",
        "Red account intervention playbook",
        "Yellow account proactive playbook",
        "Save offer framework",
        "Post-churn win-back sequence",
        "Retention metrics dashboard specification",
    ],
))
