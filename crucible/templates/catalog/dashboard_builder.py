"""Analytics dashboard design team — Data Science."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="dashboard_builder",
    description="Designs an analytics dashboard with KPI selection, data model, visual layout, and stakeholder-specific views.",
    category="Data Science",
    tags=["dashboard", "analytics", "kpi", "data visualization", "business intelligence", "looker", "metabase"],
    agents=[
        AgentSpec(
            name="KPI Analyst",
            role="Metrics strategy and KPI definition specialist",
            instructions=(
                "You are a metrics strategist. Define the dashboard's metric framework: "
                "north star metric (the single most important measure of success), "
                "tier 1 KPIs (5-7 metrics the leadership team tracks weekly), "
                "tier 2 metrics (operational metrics for team leads), "
                "leading vs. lagging indicator classification, "
                "metric definitions and calculation formulas (to prevent metric debates), "
                "and anti-metrics (what NOT to measure to avoid perverse incentives)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Data Model Designer",
            role="Data pipeline and model architecture specialist",
            instructions=(
                "You are a data engineer. Design the data model powering the dashboard: "
                "data sources required (CRM, product analytics, billing, support, marketing), "
                "data warehouse table structures (fact and dimension tables), "
                "transformation logic for key metrics (dbt model recommendations), "
                "data freshness requirements per metric (real-time vs. daily vs. weekly), "
                "and data quality checks to embed in the pipeline."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Visual Designer",
            role="Dashboard layout and visualization design specialist",
            instructions=(
                "You are a data visualization designer. Design the dashboard layout: "
                "page/tab structure (executive summary, operational, team-specific views), "
                "chart type selection for each metric "
                "(time series: line; comparison: bar; part-of-whole: pie or treemap; distribution: histogram), "
                "color palette and visual hierarchy (what draws the eye first?), "
                "filter and drill-down interactions, "
                "mobile responsiveness considerations, "
                "and a wireframe description for each dashboard view."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Adoption Strategist",
            role="Dashboard adoption and decision integration specialist",
            instructions=(
                "You are a data adoption strategist. Ensure the dashboard gets used: "
                "stakeholder mapping (who needs which view, and what decisions do they make?), "
                "dashboard training plan (how to read it, how to act on it), "
                "meeting integration (which meetings review which metrics), "
                "alerting strategy (automated alerts when metrics breach thresholds), "
                "tool recommendation (Looker, Metabase, Superset, Tableau, Power BI — with justification), "
                "and a success metric for the dashboard itself (is it being used? acting on?)."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
    ],
    debate_topics=[
        "Should the dashboard prioritize executive simplicity or operational depth?",
        "Executive dashboard (fewer metrics, clear narrative, decisions visible at a glance)",
        "Operational dashboard (more metrics, drill-down capability, suitable for teams managing daily)",
        "Layered approach (executive summary tab + operational tabs + self-serve exploration)",
    ],
    expected_outputs=[
        "North star metric and KPI hierarchy",
        "Metric definitions with calculation formulas",
        "Data model architecture and source mapping",
        "Dashboard wireframe descriptions (all views)",
        "Chart type selection guide",
        "Tool recommendation with justification",
        "Dashboard rollout and adoption plan",
        "Alert threshold recommendations",
    ],
))
