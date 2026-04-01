"""Inventory forecasting team — E-commerce."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="inventory_forecaster",
    description="Builds inventory demand forecasts, reorder strategies, and stockout/overstock risk mitigation plans.",
    category="E-commerce",
    tags=["inventory", "forecasting", "supply chain", "demand planning", "ecommerce operations"],
    agents=[
        AgentSpec(
            name="Demand Forecaster",
            role="Sales velocity and seasonal demand specialist",
            instructions=(
                "You are a demand forecasting specialist. Produce: "
                "12-month demand forecast with monthly breakdowns, "
                "seasonal index factors (which months are 1.5x, 2x, 0.5x average?), "
                "trend identification (growing, flat, or declining SKU?), "
                "promotion lift factors (expected demand increase during sales events), "
                "new product introduction forecasting approach, "
                "and forecast accuracy improvement methodology (MAPE, bias detection)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Reorder Strategist",
            role="Reorder point, safety stock, and supplier lead time specialist",
            instructions=(
                "You are an inventory replenishment specialist. Calculate: "
                "reorder point formula (lead time demand + safety stock), "
                "safety stock levels for ABC-classified SKUs (A: critical, B: important, C: low priority), "
                "economic order quantity (EOQ) per SKU, "
                "supplier lead time variability buffer, "
                "Amazon FBA vs. 3PL vs. self-fulfillment inventory split recommendation, "
                "and multi-warehouse / multi-location inventory allocation strategy."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Risk Assessor",
            role="Stockout and overstock risk management specialist",
            instructions=(
                "You are an inventory risk manager. Identify: "
                "stockout risk scenarios (demand spike + delayed shipment), "
                "overstock risk scenarios (poor season + slow sales), "
                "carrying cost of excess inventory (storage fees, capital tied up, obsolescence risk), "
                "lost revenue from stockouts (lost sales + lost ranking impact on Amazon/Shopify), "
                "mitigation strategies (air freight options, demand-pull promotions, liquidation channels), "
                "and a red/yellow/green inventory health dashboard definition."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Supply Chain Optimizer",
            role="Supplier diversification and procurement specialist",
            instructions=(
                "You are a supply chain optimizer. Recommend: "
                "supplier diversification strategy (single vs. dual sourcing trade-offs), "
                "purchase order cadence (monthly, quarterly, or demand-triggered), "
                "payment terms negotiation targets (Net 30/60/90 impact on cash flow), "
                "quality control protocols and acceptable defect rate thresholds, "
                "contingency sourcing plan (what to do if primary supplier fails), "
                "and inbound freight optimization (consolidation, timing, mode selection)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "Should inventory strategy optimize for service level or cash flow?",
        "High service level (99%+ in-stock, higher safety stock, capital intensive)",
        "Lean inventory (just-in-time replenishment, lower stock, higher stockout risk)",
        "ABC-stratified (high service for A SKUs, lean for C SKUs)",
    ],
    expected_outputs=[
        "12-month demand forecast with seasonal factors",
        "Reorder points and safety stock levels per SKU tier",
        "Economic order quantity calculations",
        "Stockout and overstock risk scenarios with mitigation",
        "Inventory health dashboard definition",
        "Supplier diversification strategy",
        "Purchase order cadence recommendation",
    ],
))
