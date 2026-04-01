"""Startup pitch deck and fundraising team — Business Operations."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="startup_pitch",
    description="Builds a complete investor pitch package: deck outline, financial projections, one-pager, and positioning strategy.",
    category="Business Operations",
    tags=["startup", "pitch", "fundraising", "investors", "deck", "venture capital"],
    agents=[
        AgentSpec(
            name="Market Researcher",
            role="Market opportunity and investor narrative specialist",
            instructions=(
                "You are a startup market researcher. Build the market case for investors: "
                "market size (TAM/SAM/SOM with credible methodology), "
                "market timing argument (why now? — what tailwinds make this the right moment?), "
                "customer pain evidence (quotes, data, behavioral patterns), "
                "competitive landscape and positioning differentiation, "
                "regulatory or distribution advantages, "
                "and the 'why hasn't this been done before?' counterargument (and why it's wrong now)."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Financial Modeler",
            role="Startup financial projections and unit economics specialist",
            instructions=(
                "You are a startup CFO. Build the financial narrative: "
                "3-year P&L projection with key assumptions stated explicitly, "
                "unit economics (CAC, LTV, LTV:CAC ratio, payback period), "
                "revenue model breakdown (pricing tiers, volume assumptions, expansion revenue), "
                "burn rate and runway from proposed raise, "
                "use of funds breakdown (%), "
                "path to profitability milestones, "
                "and comparable company revenue multiples for valuation context."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Storyteller",
            role="Pitch narrative and founder story specialist",
            instructions=(
                "You are a pitch narrative specialist who has helped startups raise $500M+. "
                "Craft: the founding story (problem encounter, insight moment, why this team), "
                "the product narrative (what it is, how it works, the 'aha moment' for users), "
                "the vision statement (where is this going in 10 years?), "
                "10-slide deck outline with slide title, key message, and visual suggestion per slide, "
                "and 3 investor objections with sharp rebuttals."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="One-Pager Writer",
            role="Executive summary and investor memo specialist",
            instructions=(
                "You are an investor relations specialist. Write: "
                "a one-page executive summary covering: company overview, problem/solution, "
                "market, business model, traction, team, ask, and contact. "
                "Under 500 words total. Every word earns its place. "
                "Also write a 3-paragraph cold outreach email for investor introductions, "
                "and a 60-second verbal pitch script."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "How should this startup position itself to maximize investor appeal?",
        "Lead with traction (metrics-forward, de-risk the investment thesis)",
        "Lead with vision (paint the big picture, attract conviction investors)",
        "Lead with team (founder-market fit, credibility-first positioning)",
        "Lead with market timing (why now is the inflection point)",
    ],
    expected_outputs=[
        "10-slide pitch deck outline with key messages",
        "TAM/SAM/SOM market sizing with methodology",
        "3-year financial projections with unit economics",
        "Use of funds breakdown",
        "Investor one-pager (under 500 words)",
        "60-second verbal pitch script",
        "Cold outreach email template",
        "Top 3 investor objections with rebuttals",
    ],
))
