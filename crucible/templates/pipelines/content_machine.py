"""content_machine pipeline: SEO Article → Social Media Campaign → Newsletter."""

from . import _register
from ..composer import PipelineBuilder

_register(
    PipelineBuilder(
        "content_machine",
        description=(
            "Full content marketing pipeline: produces an SEO-optimised article, "
            "repurposes it into a social media campaign, then distills it into a newsletter."
        ),
    )
    .then("seo_article")
    .then(
        "social_media_campaign",
        debate_gate=True,
        gate_topic=(
            "Does the social media campaign align with the article's core message "
            "and provide genuine value to the target audience? "
            "Options: proceed or halt."
        ),
    )
    .then("newsletter")
    .build()
)
