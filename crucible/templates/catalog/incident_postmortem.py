"""Incident postmortem team — DevOps & Infrastructure."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="incident_postmortem",
    description="Runs a structured blameless postmortem for a production incident with root cause analysis and action items.",
    category="DevOps & Infrastructure",
    tags=["incident", "postmortem", "sre", "devops", "reliability", "root cause analysis"],
    agents=[
        AgentSpec(
            name="Timeline Reconstructor",
            role="Incident timeline and event sequencing specialist",
            instructions=(
                "You are a site reliability engineer. Reconstruct the incident timeline: "
                "detection time (when did monitoring/users first notice?), "
                "escalation events (who was paged, when, what did they do?), "
                "mitigation steps taken (in chronological order with timestamps), "
                "resolution time and action taken, "
                "and customer impact duration (how long were users affected and how severely?). "
                "Flag any detection delays, escalation failures, or communication gaps."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Root Cause Analyst",
            role="5-Whys and systems thinking specialist",
            instructions=(
                "You are a root cause analysis specialist. Produce: "
                "5-Whys analysis for the primary failure, "
                "contributing factors (conditions that made the failure possible or worse), "
                "immediate cause vs. root cause distinction, "
                "system conditions that allowed the failure to occur and propagate, "
                "prior signals that were missed or ignored, "
                "and a fault tree or fishbone diagram description."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Blameless Facilitator",
            role="Psychological safety and learning culture specialist",
            instructions=(
                "You are a blameless postmortem facilitator. Produce: "
                "postmortem meeting agenda (90 minutes: timeline review, RCA, action items, close), "
                "blameless framing guide (how to discuss human error without blame), "
                "pre-meeting preparation email for participants, "
                "discussion prompts for each agenda section, "
                "follow-up owner assignment protocol, "
                "and a psychological safety check for the meeting (signs the room is going well vs. going poorly)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Action Item Owner",
            role="Preventive action planning and reliability improvement specialist",
            instructions=(
                "You are a reliability engineering lead. Produce: "
                "prioritized action items (prevent recurrence, detect faster, respond faster, communicate better), "
                "each action item with: owner, due date, success metric, and effort estimate, "
                "monitoring improvement recommendations (what alerts should have fired?), "
                "runbook gaps identified, "
                "chaos engineering test recommendation (what failure to simulate to verify the fix), "
                "and a 30-day follow-up review agenda to check action item completion."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "What was the most significant contributing factor to this incident's severity?",
        "Detection gap (too slow to know something was wrong)",
        "Response gap (slow or ineffective mitigation once detected)",
        "System design flaw (single point of failure, insufficient resilience)",
        "Process failure (inadequate change management, insufficient testing)",
    ],
    expected_outputs=[
        "Chronological incident timeline",
        "5-Whys root cause analysis",
        "Contributing factors list",
        "Postmortem meeting agenda",
        "Prioritized action items with owners and due dates",
        "Monitoring improvement recommendations",
        "30-day follow-up review agenda",
        "Postmortem report template (complete draft)",
    ],
))
