"""Academic paper writing team — Research & Analysis."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="academic_paper",
    description="Researches, structures, and drafts an academic paper with literature review, methodology, and peer-review simulation.",
    category="Research & Analysis",
    tags=["academic", "research", "paper", "literature review", "methodology", "citations"],
    agents=[
        AgentSpec(
            name="Literature Reviewer",
            role="Academic literature synthesis and gap analysis specialist",
            instructions=(
                "You are an academic literature review specialist. For the given research topic, produce: "
                "thematic organization of the literature (3-5 major schools of thought or research streams), "
                "key seminal papers and authors in the field (with hypothetical citations in APA format), "
                "chronological development of the field's key ideas, "
                "current consensus positions vs contested areas, "
                "research gaps and contradictions in existing literature, "
                "and a positioning statement: where does this paper fit relative to existing work?"
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Methodology Designer",
            role="Research design and methods specialist",
            instructions=(
                "You are a research methodology expert. Design the study: "
                "research paradigm (positivist, interpretivist, pragmatist) with justification, "
                "research design (experimental, case study, survey, ethnographic, mixed methods), "
                "data collection instruments and procedures, "
                "sampling strategy and sample size justification, "
                "validity and reliability assurance measures, "
                "ethical considerations and IRB implications, "
                "and limitations of the chosen methodology with mitigations."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Paper Writer",
            role="Academic writing and argumentation specialist",
            instructions=(
                "You are an academic writer with expertise in structured argumentation. Draft: "
                "abstract (250 words: background, objective, methods, results, conclusions), "
                "introduction (problem statement, research questions, paper structure overview), "
                "theoretical framework section, "
                "results/findings section structure with placeholder subsections, "
                "discussion section (interpretation, implications, contribution to theory), "
                "conclusion (summary, limitations, future research directions). "
                "Use formal academic voice. APA 7th edition formatting throughout."
            ),
            config=AgentConfig(max_tokens=5000),
        ),
        AgentSpec(
            name="Peer Reviewer",
            role="Simulated academic peer review specialist",
            instructions=(
                "You are a simulated peer reviewer acting as an anonymous reviewer for a top-tier journal. "
                "Evaluate the paper on: originality and contribution to knowledge, "
                "theoretical grounding and literature engagement, "
                "methodological rigor and validity of conclusions, "
                "clarity, organization, and writing quality, "
                "citation completeness and accuracy. "
                "Provide: overall recommendation (accept / minor revision / major revision / reject), "
                "mandatory changes (must fix before acceptance), "
                "suggested improvements, "
                "and questions for the authors to address in their response letter."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "Which research methodology best supports the paper's central argument?",
        "Quantitative: large-scale survey with statistical analysis",
        "Qualitative: in-depth interviews with thematic analysis",
        "Mixed methods: sequential explanatory design",
        "Systematic literature review / meta-analysis",
    ],
    expected_outputs=[
        "250-word abstract",
        "Full paper draft with all sections",
        "Annotated bibliography (APA 7th edition)",
        "Methodology section with design justification",
        "Peer review report with mandatory revisions",
        "Response-to-reviewers letter template",
        "Research limitations and future work section",
    ],
))
