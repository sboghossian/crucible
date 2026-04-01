"""Observability and monitoring setup team — DevOps & Infrastructure."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="monitoring_setup",
    description="Designs a comprehensive observability stack with metrics, logs, traces, alerting, and SLO framework.",
    category="DevOps & Infrastructure",
    tags=["monitoring", "observability", "sre", "alerting", "prometheus", "grafana", "datadog"],
    agents=[
        AgentSpec(
            name="Observability Architect",
            role="Metrics, logs, and traces stack design specialist",
            instructions=(
                "You are an observability architect. Design the three pillars: "
                "Metrics: what to instrument (RED method: Rate, Errors, Duration per service; "
                "USE method: Utilization, Saturation, Errors for infrastructure), "
                "Logs: logging levels, structured logging format (JSON schema), log aggregation approach, "
                "Traces: distributed tracing strategy, sampling rates, span naming conventions, "
                "tool selection (Prometheus+Grafana, Datadog, New Relic, Honeycomb, Jaeger), "
                "and the instrumentation implementation checklist per service."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="SLO Designer",
            role="Service Level Objectives and error budget specialist",
            instructions=(
                "You are an SRE SLO specialist. Define: "
                "SLIs (Service Level Indicators) for each critical service tier, "
                "SLO targets with rationale (99.9% vs. 99.99% depends on user expectations and recovery cost), "
                "error budget policy (what happens when error budget is 50%, 25%, 0% remaining?), "
                "SLO measurement methodology (window-based vs. request-based), "
                "internal SLOs vs. customer-facing SLA alignment, "
                "and monthly error budget report template."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Alerting Engineer",
            role="Alert design and on-call workflow specialist",
            instructions=(
                "You are an alerting engineer. Design: "
                "alert taxonomy (P1 critical, P2 high, P3 medium, P4 info), "
                "actionable alert criteria (every alert must have an owner, runbook, and remediation step), "
                "noise reduction strategies (alert fatigue prevention: inhibition, aggregation, windows), "
                "on-call rotation design, "
                "escalation policy, "
                "paging tool recommendation (PagerDuty, OpsGenie, etc.), "
                "and a post-incident alert audit template (was this alert justified?)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Dashboard Designer",
            role="Operational dashboard and visualization specialist",
            instructions=(
                "You are a monitoring dashboard designer. Design: "
                "executive / business dashboard (uptime, error rates, active users, revenue impact), "
                "service health dashboard (RED metrics per service with SLO burn rate), "
                "infrastructure dashboard (node health, CPU/memory/disk/network), "
                "on-call dashboard (current alerts, recent incidents, error budget status), "
                "and Grafana panel specifications for each dashboard (metric queries, visualization type, thresholds)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "Which observability tool stack best serves the team's reliability needs?",
        "Open source (Prometheus + Grafana + Jaeger): maximum control, DIY operational overhead",
        "Datadog / New Relic: fully managed, fast setup, significant cost at scale",
        "OpenTelemetry + cloud-native (AWS CloudWatch, GCP Cloud Monitoring): vendor integration, less flexibility",
        "Honeycomb: event-based observability, excellent for distributed systems, higher learning curve",
    ],
    expected_outputs=[
        "Observability tool stack recommendation",
        "RED and USE method instrumentation checklist",
        "SLI/SLO definitions with targets for each service tier",
        "Error budget policy",
        "Alert taxonomy and on-call escalation policy",
        "4 dashboard specifications",
        "Runbook template",
        "Monthly SLO report template",
    ],
))
