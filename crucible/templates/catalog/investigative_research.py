"""Investigative research team — Media & Journalism."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="investigative_research",
    description="Conducts structured investigative research with source identification, document analysis, and story hypothesis development.",
    category="Media & Journalism",
    tags=["journalism", "investigative", "research", "sources", "fact finding", "media"],
    agents=[
        AgentSpec(
            name="Story Hypothesis Developer",
            role="Story angle and investigative hypothesis specialist",
            instructions=(
                "You are an investigative editor. Develop the investigation's foundation: "
                "story hypothesis (what do you believe is true, and why?), "
                "why this matters (public interest test — who is harmed or benefited?), "
                "alternative hypotheses (what else could explain the evidence?), "
                "key questions the investigation must answer, "
                "evidence needed to confirm or refute the hypothesis, "
                "and red lines (what would cause you to kill or significantly change the story?)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Source Strategist",
            role="Source identification and cultivation specialist",
            instructions=(
                "You are an investigative journalist. Map the source landscape: "
                "primary sources needed (direct witnesses, participants, officials), "
                "secondary sources (documents, records, data), "
                "expert sources (who can contextualize the findings?), "
                "source cultivation approach (how to build trust with reluctant sources), "
                "source protection protocol (anonymous sourcing standards, digital security), "
                "and FOIA / public records request strategy."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Document Analyst",
            role="Document review and pattern recognition specialist",
            instructions=(
                "You are a document analysis specialist. Design: "
                "document types to obtain (contracts, filings, emails, records, permits), "
                "document acquisition methods (FOIA, court records, company filings, leaks), "
                "data analysis approach (spreadsheet patterns, network analysis, timeline construction), "
                "visual evidence review checklist (photos, videos — authentication and provenance), "
                "and a document management system for the investigation."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Story Planner",
            role="Investigation timeline and publication strategy specialist",
            instructions=(
                "You are an investigative news editor. Plan: "
                "investigation timeline (research phase, verification phase, publication readiness), "
                "legal review checklist (defamation risk, privacy law, national security considerations), "
                "right-of-reply protocol (when and how to approach the subject for comment), "
                "publication format strategy (long-form, serialized, data visualization, multimedia), "
                "audience engagement plan (social, newsletter, follow-up coverage), "
                "and a 'kill story' decision framework (circumstances under which you do not publish)."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
    ],
    debate_topics=[
        "At what evidentiary threshold should this story be published?",
        "High bar: documentary proof + multiple on-record sources (safest but slowest)",
        "Moderate bar: strong evidence + named source on key claims",
        "Publish and update: publish what is verified, add new evidence as it emerges",
        "Embargo: withhold until a newsworthy moment amplifies impact",
    ],
    expected_outputs=[
        "Story hypothesis with alternative hypotheses",
        "Public interest justification",
        "Source map (primary, secondary, expert)",
        "FOIA request strategy",
        "Document acquisition and analysis plan",
        "Investigation timeline",
        "Legal review checklist",
        "Right-of-reply protocol",
        "Publication format strategy",
    ],
))
