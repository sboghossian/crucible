"""Competitor pricing analysis team — E-commerce."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="competitor_pricing",
    description="Analyzes competitor pricing strategies and recommends optimal pricing and promotional tactics.",
    category="E-commerce",
    tags=["pricing", "competitive pricing", "ecommerce", "price strategy", "promotions"],
    agents=[
        AgentSpec(
            name="Pricing Researcher",
            role="Competitive price intelligence specialist",
            instructions=(
                "You are a pricing intelligence analyst. For the given product category, research: "
                "price distribution across competitors (min, median, max, most common price points), "
                "pricing model variations (unit pricing, bundles, subscriptions, volume tiers), "
                "promotional patterns (frequency of discounts, typical discount depth, seasonal sales), "
                "price-quality positioning map (who is budget / mid-market / premium?), "
                "and channel pricing differences (Amazon vs. DTC vs. retail store pricing gaps)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Price Strategist",
            role="Pricing model and positioning specialist",
            instructions=(
                "You are a pricing strategist. Recommend: "
                "optimal price point with margin analysis (COGS → wholesale → MSRP waterfall), "
                "pricing strategy (cost-plus, value-based, competitive, penetration, or skimming), "
                "price elasticity considerations (what happens to volume at ±10% / ±20%?), "
                "bundle and upsell pricing (cross-sell opportunities, bundle discount %), "
                "subscription vs. one-time purchase trade-offs, "
                "and B2B vs. consumer pricing differential guidance."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Promotions Designer",
            role="Discount, promotion, and deal architecture specialist",
            instructions=(
                "You are a promotions design specialist. Produce: "
                "promotions calendar (12 months, with event-based and evergreen promotions), "
                "discount depth recommendation (% off that drives volume without margin damage), "
                "deal structure options (% off vs. $ off vs. BOGO vs. free shipping thresholds), "
                "flash sale design (duration, depth, urgency tactics), "
                "loyalty and repeat purchase incentive design, "
                "and coupon / promo code strategy (distribution channels, single-use vs. public codes)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Margin Analyst",
            role="Profitability and unit economics specialist",
            instructions=(
                "You are a margin and profitability analyst. Calculate: "
                "unit economics at current price point (COGS, gross margin, contribution margin), "
                "impact of proposed price change on revenue, margin, and volume (sensitivity table), "
                "minimum viable price floor (price below which it's not worth selling), "
                "channel margin comparison (how does Amazon FBA vs. DTC vs. wholesale compare?), "
                "and break-even volume at different price points."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "Should this product compete on price or differentiate on value?",
        "Price competitively (match or undercut market, win on volume)",
        "Price premium (invest in brand, reviews, and differentiation to justify higher ASP)",
        "Price match with superior value-adds (same price, more included)",
    ],
    expected_outputs=[
        "Competitive price distribution analysis",
        "Price-quality positioning map",
        "Recommended price point with margin analysis",
        "12-month promotions calendar",
        "Unit economics sensitivity table",
        "Bundle and upsell pricing recommendations",
        "Channel pricing strategy",
    ],
))
