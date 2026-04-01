"""Infrastructure capacity planning team — DevOps & Infrastructure."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="capacity_planning",
    description="Plans infrastructure capacity requirements with demand forecasting, cost optimization, and scaling strategy.",
    category="DevOps & Infrastructure",
    tags=["capacity planning", "devops", "infrastructure", "scaling", "cloud", "cost optimization"],
    agents=[
        AgentSpec(
            name="Demand Forecaster",
            role="Traffic and workload growth specialist",
            instructions=(
                "You are a capacity planning analyst. Forecast demand for: "
                "traffic growth (requests/second, monthly active users, data volume), "
                "seasonal and event-driven spikes (peak multiplier vs. average baseline), "
                "new feature impact on resource consumption, "
                "batch job and background workload projections, "
                "and database growth rate (read/write ratio, storage expansion). "
                "Provide 3-month, 6-month, and 12-month projections with confidence intervals."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Infrastructure Architect",
            role="Scaling architecture and resource sizing specialist",
            instructions=(
                "You are an infrastructure architect. Design: "
                "current vs. projected resource requirements (CPU, memory, storage, network), "
                "horizontal scaling plan (when to add nodes, auto-scaling policies), "
                "vertical scaling considerations (instance right-sizing), "
                "database scaling strategy (read replicas, sharding, partitioning), "
                "CDN and caching layer capacity, "
                "and failover capacity requirements (N+1 or N+2 redundancy planning)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Cost Optimizer",
            role="Cloud cost management and efficiency specialist",
            instructions=(
                "You are a FinOps specialist. Produce: "
                "current infrastructure cost breakdown by service, "
                "cost forecast at projected growth rates, "
                "reserved instance / savings plan recommendation (1-year vs. 3-year analysis), "
                "spot instance opportunity areas (workloads suitable for spot), "
                "waste identification (idle resources, oversized instances, orphaned storage), "
                "and a 90-day cost reduction roadmap with projected savings."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="SLO Guardian",
            role="Reliability targets and capacity buffer specialist",
            instructions=(
                "You are an SRE focused on SLO compliance. Define: "
                "capacity buffers required to maintain SLOs at peak load, "
                "load shedding strategy (what to drop gracefully under extreme load), "
                "circuit breaker thresholds, "
                "performance baselines and degradation triggers, "
                "capacity review cadence recommendation, "
                "and runbook for capacity emergency response."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
    ],
    debate_topics=[
        "Should capacity be provisioned for peak load or rely on auto-scaling?",
        "Pre-provision for peak (predictable cost, instant capacity, higher baseline spend)",
        "Auto-scale aggressively (cost-efficient baseline, risk of scale lag at sudden spikes)",
        "Hybrid: reserved baseline with burst auto-scaling for spikes",
    ],
    expected_outputs=[
        "3/6/12-month demand forecast",
        "Resource requirements per service at projected growth",
        "Auto-scaling policy recommendations",
        "Infrastructure cost forecast and optimization roadmap",
        "Reserved instance / savings plan analysis",
        "SLO-aligned capacity buffer requirements",
        "Load shedding strategy",
    ],
))
