"""Real estate market comparison team — Real Estate."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="market_comparison",
    description="Compares multiple real estate markets for investment or relocation decisions with risk-adjusted analysis.",
    category="Real Estate",
    tags=["real estate", "market comparison", "relocation", "investment", "market analysis"],
    agents=[
        AgentSpec(
            name="Demographics Analyst",
            role="Population and economic growth specialist",
            instructions=(
                "You are a real estate demographics analyst. For each market being compared, analyze: "
                "population growth rate (5-year and projected 10-year), "
                "net migration trends (inbound vs. outbound), "
                "age distribution and household formation rates, "
                "employment base diversification (not reliant on single employer/industry), "
                "median household income trends, "
                "and remote work migration patterns (is this market gaining remote workers?)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Housing Market Analyst",
            role="Real estate market metrics specialist",
            instructions=(
                "You are a housing market analyst. For each market, provide: "
                "median home price and year-over-year appreciation, "
                "price-to-rent ratio (buy vs. rent economics), "
                "months of supply and days on market trend, "
                "new construction pipeline and permit activity, "
                "foreclosure rates and distressed inventory, "
                "and rent growth rate vs. income growth rate (affordability trend)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Investment Return Comparator",
            role="Cross-market investment return and risk specialist",
            instructions=(
                "You are a comparative real estate investment analyst. Build for each market: "
                "expected cash-on-cash return for a benchmark property type, "
                "cap rate range for that property class, "
                "landlord-friendly vs. tenant-friendly regulatory environment rating, "
                "property tax effective rate comparison, "
                "insurance cost environment (especially for coastal/disaster-prone markets), "
                "and overall market risk rating (A, B, C, D market classification)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Recommendation Synthesizer",
            role="Decision matrix and recommendation specialist",
            instructions=(
                "You are a strategic advisor. Synthesize all market data into: "
                "weighted scoring matrix (customize weights by investor priority: income, appreciation, safety, liquidity), "
                "ranked market recommendation with clear rationale, "
                "ideal investor/buyer profile for each market, "
                "timing considerations (which market is in the best buying window now?), "
                "and risk-adjusted return comparison. If for relocation: add quality of life, "
                "cost of living, and lifestyle factor scoring."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "Which market offers the superior risk-adjusted return for the next decade?",
        "High-growth Sun Belt markets (higher appreciation, lower cap rates, execution risk)",
        "Stable Midwest markets (high cap rates, modest appreciation, lower volatility)",
        "Coastal gateway markets (institutional quality, lower yield, strong liquidity)",
        "Emerging secondary markets (early-mover advantage, higher risk, less liquidity)",
    ],
    expected_outputs=[
        "Side-by-side market comparison table",
        "Weighted scoring matrix with rankings",
        "Investment return comparison per market",
        "Regulatory environment assessment",
        "Ideal buyer/investor profile per market",
        "Timing recommendation for each market",
        "Final ranked recommendation with rationale",
    ],
))
