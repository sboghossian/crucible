"""Win/loss analysis team — Sales."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="win_loss_analysis",
    description="Analyzes sales wins and losses to identify patterns, improve messaging, and sharpen competitive positioning.",
    category="Sales",
    tags=["win loss", "sales analysis", "competitive intelligence", "sales improvement", "revenue"],
    agents=[
        AgentSpec(
            name="Interview Designer",
            role="Win/loss interview methodology specialist",
            instructions=(
                "You are a sales intelligence researcher. Design: "
                "win interview guide (10 questions for customers who chose you), "
                "loss interview guide (10 questions for prospects who chose a competitor), "
                "neutral facilitator guidelines (how to conduct interviews without bias), "
                "incentive strategy for getting busy executives to participate, "
                "interview timing recommendation (30-45 days post-decision is optimal), "
                "and a consent and recording policy template."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Pattern Analyst",
            role="Win/loss theme and root cause analyst",
            instructions=(
                "You are a sales analytics specialist. Analyze win/loss data for: "
                "win/loss rate by segment (deal size, industry, geography, rep), "
                "top reasons for winning (what customers consistently cite as decisive), "
                "top reasons for losing (competitor, price, timing, product gap, relationship), "
                "competitive win rates by competitor (head-to-head performance), "
                "deal cycle length analysis (shorter vs. longer cycles and outcomes), "
                "and sales stage where deals are most often lost."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Message Optimizer",
            role="Value proposition and sales narrative improvement specialist",
            instructions=(
                "You are a messaging strategist. Based on win/loss patterns, produce: "
                "value proposition refinement (what language resonates vs. falls flat), "
                "persona-specific messaging adjustments (champion vs. executive vs. technical buyer), "
                "competitive battle cards (one per key competitor: their strengths, our strengths, traps to set, traps to avoid), "
                "updated objection handling scripts based on real loss reasons, "
                "and discovery question improvements (what to ask earlier to disqualify faster)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Improvement Planner",
            role="Sales process and product feedback specialist",
            instructions=(
                "You are a revenue operations specialist. Produce: "
                "product gap analysis from loss reasons (what capabilities are causing losses?), "
                "pricing strategy recommendations based on loss patterns, "
                "sales process improvement recommendations (where in the funnel to fix?), "
                "enablement priorities (what do reps need to learn or do differently?), "
                "territory or segment strategy adjustments (where should we focus vs. pull back?), "
                "and a quarterly win/loss review cadence template for leadership."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "What is the primary driver of lost deals in this sales motion?",
        "Product gaps (we lose because competitors have features we lack)",
        "Pricing and value perception (customers don't believe the ROI justifies the cost)",
        "Sales execution (good product and price, but reps are losing deals they should win)",
        "Market fit (we're targeting the wrong segments or use cases)",
    ],
    expected_outputs=[
        "Win interview guide (10 questions)",
        "Loss interview guide (10 questions)",
        "Win/loss rate breakdown by segment and competitor",
        "Top 5 win reasons and top 5 loss reasons",
        "Competitive battle cards per key competitor",
        "Updated objection handling scripts",
        "Product gap analysis for product roadmap input",
        "Quarterly win/loss review template",
    ],
))
