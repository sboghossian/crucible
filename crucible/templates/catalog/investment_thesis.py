"""Investment thesis development team — Finance."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="investment_thesis",
    description="Builds a rigorous investment thesis for a stock, sector, or asset with bull/bear analysis and entry/exit criteria.",
    category="Finance",
    tags=["investing", "investment thesis", "stock analysis", "equity research", "due diligence"],
    agents=[
        AgentSpec(
            name="Business Analyst",
            role="Company and competitive moat specialist",
            instructions=(
                "You are an equity research analyst. Analyze the investment subject for: "
                "business model clarity (how does it make money, who pays, why do they keep paying?), "
                "competitive moat assessment (network effects, switching costs, cost advantages, brand, IP), "
                "market position and share trajectory, "
                "management quality indicators (capital allocation history, insider ownership, track record), "
                "unit economics health (gross margin, contribution margin, LTV:CAC if applicable), "
                "and key business risks (regulatory, competitive, execution, macro sensitivity)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Financial Analyst",
            role="Valuation and financial model specialist",
            instructions=(
                "You are a financial analyst. Produce: "
                "3-year revenue and earnings growth assumptions with stated drivers, "
                "DCF valuation (with explicit discount rate and terminal growth rate assumptions), "
                "comparable company analysis (EV/Revenue, EV/EBITDA, P/E vs. peers), "
                "free cash flow conversion analysis, "
                "balance sheet health (leverage, liquidity, debt maturity profile), "
                "and scenario analysis (bull / base / bear case with implied prices)."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Bull Case Advocate",
            role="Upside scenario and catalyst identification specialist",
            instructions=(
                "You are the bull case advocate. Build the strongest possible case for this investment: "
                "primary upside catalysts (what events could drive the stock significantly higher?), "
                "underappreciated assets or optionality (what is the market not pricing in?), "
                "why the bearish consensus might be wrong, "
                "historical analogues (companies that were similarly misunderstood and rewarded patient investors), "
                "and upside price target with 12-24 month timeframe and conviction level."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Bear Case Advocate",
            role="Downside risk and thesis-killer specialist",
            instructions=(
                "You are the bear case advocate. Build the strongest argument against this investment: "
                "key risks that could permanently impair value (not just short-term volatility), "
                "what the bull case assumes that might not be true, "
                "disruptive threats being underestimated, "
                "management or governance red flags, "
                "valuation risks (what the stock is already pricing in), "
                "and bear case price target with specific trigger scenarios."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "Does the current price offer an adequate margin of safety relative to intrinsic value?",
        "Yes — current price implies a 30%+ discount to intrinsic value with strong catalysts",
        "No — current price reflects optimistic assumptions with limited downside cushion",
        "Uncertain — wait for a specific catalyst or price level before initiating a position",
    ],
    expected_outputs=[
        "Business model and moat assessment",
        "DCF valuation with bull/base/bear scenarios",
        "Comparable company analysis",
        "Bull case with catalysts and price target",
        "Bear case with risks and price target",
        "Entry and exit criteria",
        "Position sizing recommendation",
        "Investment thesis summary (one page)",
    ],
))
