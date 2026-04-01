"""Financial model building team — Finance."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="financial_model",
    description="Builds a three-statement financial model with assumptions, projections, and scenario analysis for business planning.",
    category="Finance",
    tags=["financial model", "three statement model", "p&l", "cash flow", "projections", "startup", "finance"],
    agents=[
        AgentSpec(
            name="Assumptions Builder",
            role="Revenue drivers and model assumptions specialist",
            instructions=(
                "You are a financial modeling expert. Define the model's assumptions: "
                "revenue drivers (volume, price, mix — what moves the top line?), "
                "unit economics assumptions (CAC, LTV, churn, ARPU, conversion rates), "
                "headcount and payroll growth assumptions (hiring plan by quarter), "
                "COGS structure (variable vs. fixed, gross margin expansion thesis), "
                "OpEx growth assumptions (Sales & Marketing, G&A as % of revenue), "
                "and working capital assumptions (DSO, DPO, inventory turns). "
                "Flag which assumptions are most sensitive to outcomes."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Income Statement Architect",
            role="P&L construction and profitability analysis specialist",
            instructions=(
                "You are a P&L specialist. Build a 3-year monthly income statement structure: "
                "revenue line items by product/segment/geography, "
                "COGS breakdown and gross margin analysis, "
                "operating expense line items (S&M, R&D, G&A with detailed sub-items), "
                "EBITDA and operating income, "
                "interest expense and other non-operating items, "
                "and net income with EPS if applicable. "
                "Show year-over-year growth rates and margin ratios for each major line."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Cash Flow Modeler",
            role="Cash flow and liquidity planning specialist",
            instructions=(
                "You are a cash flow modeling specialist. Build: "
                "operating cash flow bridge (net income → operating CF with working capital adjustments), "
                "capital expenditure schedule (maintenance vs. growth capex), "
                "financing activities (debt drawdown, repayment, equity raises), "
                "free cash flow calculation and FCF yield, "
                "cash runway analysis (months of runway at current burn), "
                "liquidity stress test (what if revenue misses by 20%?), "
                "and covenant compliance tracking (if applicable)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Scenario Analyst",
            role="Sensitivity analysis and strategic planning specialist",
            instructions=(
                "You are a scenario planning specialist. Produce: "
                "bull / base / bear case assumptions table (3 scenarios × 5 key assumptions), "
                "scenario income statement and cash flow summary, "
                "tornado chart analysis (which assumptions have the biggest output impact?), "
                "break-even analysis (revenue needed to reach EBITDA breakeven), "
                "funding milestone map (what metrics trigger a Series A, B, profitability?), "
                "and model audit checklist (circular references, balance sheet check, sanity checks)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "Which growth scenario should be used as the operating plan?",
        "Conservative base case (under-promise, over-deliver; manage burn carefully)",
        "Aggressive upside case (set ambitious targets to attract investors and push the team)",
        "Most likely case with explicit risk corridors (honest projection with stated uncertainty)",
    ],
    expected_outputs=[
        "Revenue driver assumptions tree",
        "3-year monthly income statement structure",
        "Cash flow statement and runway analysis",
        "3-scenario comparison (bull / base / bear)",
        "Tornado chart (top 5 most sensitive assumptions)",
        "Break-even analysis",
        "Funding milestone map",
        "Model audit checklist",
    ],
))
