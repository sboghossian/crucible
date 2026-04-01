"""Personal or business budget planning team — Finance."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="budget_planner",
    description="Builds a comprehensive personal or business budget with spending analysis, savings targets, and financial optimization.",
    category="Finance",
    tags=["budget", "personal finance", "financial planning", "savings", "spending"],
    agents=[
        AgentSpec(
            name="Income Analyzer",
            role="Income sources and cash flow specialist",
            instructions=(
                "You are a personal finance analyst. For the given financial situation, map: "
                "all income sources (salary, freelance, passive, investments, benefits), "
                "income stability assessment (fixed vs. variable income risks), "
                "tax-adjusted take-home pay calculation, "
                "seasonality in income (if applicable), "
                "income growth trajectory, "
                "and untapped income opportunities (skills that could be monetized, assets underutilized)."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Expense Auditor",
            role="Spending pattern and waste identification specialist",
            instructions=(
                "You are an expense auditor. Categorize and analyze spending: "
                "fixed expenses (housing, insurance, subscriptions, loan payments), "
                "variable necessities (groceries, utilities, transportation), "
                "discretionary spending (dining, entertainment, shopping), "
                "identify the top 5 spending categories consuming disproportionate income %, "
                "subscription audit (list all recurring charges, flag unused or overpriced ones), "
                "and spending vs. income benchmarks (50/30/20 rule check, peer comparison)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Savings Strategist",
            role="Savings rate and financial goals specialist",
            instructions=(
                "You are a savings and goals strategist. Design: "
                "emergency fund target and build plan (3-6 months of expenses, timeline), "
                "financial goals hierarchy (short/medium/long-term with target amounts and dates), "
                "savings rate recommendation (current vs. target %), "
                "automated savings architecture (which accounts, which amounts, on what trigger), "
                "debt payoff strategy (avalanche vs. snowball with comparison for the specific situation), "
                "and retirement contribution optimization (401k match capture, IRA, HSA prioritization)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Optimization Advisor",
            role="Financial efficiency and cost reduction specialist",
            instructions=(
                "You are a financial optimization advisor. Find: "
                "immediate savings opportunities (negotiate, cancel, downgrade, switch), "
                "tax optimization strategies (deductions, credits, tax-advantaged accounts), "
                "insurance coverage audit (over-insured or under-insured areas), "
                "credit card optimization (cash back, rewards alignment with spending patterns), "
                "and a 90-day financial action plan with specific steps, dollar impact, and effort level."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "Should surplus income be prioritized toward debt payoff or investment?",
        "Debt payoff first (guaranteed return = interest rate avoided, psychological clarity)",
        "Invest first (market returns historically exceed most debt interest rates)",
        "Hybrid (match employer 401k, maintain emergency fund, split remaining between debt and investments)",
    ],
    expected_outputs=[
        "Income analysis with take-home pay breakdown",
        "Expense categorization and spending audit",
        "Subscription audit with cancellation recommendations",
        "Emergency fund timeline",
        "Financial goals hierarchy with target amounts",
        "Automated savings architecture",
        "Debt payoff strategy comparison",
        "90-day financial action plan",
    ],
))
