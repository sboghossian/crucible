"""research_to_publish pipeline: Market Research → Academic Paper → Course Creator."""

from . import _register
from ..composer import PipelineBuilder

_register(
    PipelineBuilder(
        "research_to_publish",
        description=(
            "Research-to-publication pipeline: produces market research, "
            "structures it into an academic paper, then turns the findings into a course."
        ),
    )
    .then(
        "market_research",
        debate_gate=True,
        gate_topic=(
            "Is the research substantial and rigorous enough to underpin "
            "an academic paper? "
            "Options: proceed or halt."
        ),
    )
    .then("academic_paper")
    .then("course_creator")
    .build()
)
