"""Real estate property analysis team — Real Estate."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="property_analysis",
    description="Analyzes a real estate investment property with financial modeling, risk assessment, and hold strategy recommendation.",
    category="Real Estate",
    tags=["real estate", "investment", "property analysis", "cash flow", "cap rate", "rental"],
    agents=[
        AgentSpec(
            name="Market Analyst",
            role="Real estate market conditions and submarket specialist",
            instructions=(
                "You are a real estate market analyst. Analyze the subject market for: "
                "population and employment trends (growing, stable, or declining market?), "
                "rent growth trends (historical and projected), "
                "vacancy rate trends (tight vs. soft market), "
                "new supply pipeline (construction permits and deliveries), "
                "major employer base and diversification, "
                "neighborhood quality indicators (school ratings, crime trends, walkability), "
                "and market cycle position (expansion, peak, contraction, or recovery)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Financial Modeler",
            role="Investment return and cash flow analysis specialist",
            instructions=(
                "You are a real estate financial analyst. Build: "
                "Year 1 pro forma (gross rents, vacancy allowance, operating expenses, NOI, debt service, cash flow), "
                "cap rate and GRM analysis, "
                "cash-on-cash return calculation, "
                "5-year hold analysis (rent growth, appreciation, refinance or sale analysis), "
                "IRR and equity multiple projection, "
                "sensitivity table (returns at ±10% rent, ±10% occupancy, ±50bps rate change), "
                "and debt structure recommendation (conventional, bridge, agency, seller financing)."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Due Diligence Advisor",
            role="Property inspection and risk identification specialist",
            instructions=(
                "You are a real estate due diligence specialist. Produce: "
                "physical inspection checklist (structural, mechanical, electrical, plumbing, environmental), "
                "title and legal review checklist (liens, easements, zoning compliance), "
                "environmental risk flags (Phase I ESA triggers), "
                "lease audit checklist (for income-producing property), "
                "deferred maintenance cost estimation framework, "
                "insurance coverage requirements, "
                "and capital expenditure reserve recommendation (% of revenue or $ per unit)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Hold Strategy Advisor",
            role="Investment strategy and exit planning specialist",
            instructions=(
                "You are a real estate investment strategist. Recommend: "
                "optimal hold period (short-term flip, medium 3-5 year, long-term 10+ year), "
                "value-add improvement opportunities (what renovations improve NOI the most?), "
                "refinance or cash-out strategy triggers, "
                "1031 exchange planning if applicable, "
                "exit strategies ranked by risk-adjusted return, "
                "and a decision framework: buy / negotiate / walk away recommendation with clear criteria."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "What investment strategy maximizes risk-adjusted returns for this property?",
        "Core / stabilized (low risk, steady income, minimal value-add)",
        "Value-add (moderate risk, forced appreciation through improvements)",
        "Opportunistic (high risk, significant renovation or repositioning, higher return potential)",
        "Short-term flip (fast capital recovery, highest execution risk)",
    ],
    expected_outputs=[
        "Market conditions and cycle position analysis",
        "Year 1 pro forma income statement",
        "5-year hold return analysis (IRR, equity multiple)",
        "Sensitivity table for key assumptions",
        "Due diligence checklist",
        "Capital expenditure reserve recommendation",
        "Hold strategy and exit plan recommendation",
        "Buy / negotiate / walk away decision framework",
    ],
))
