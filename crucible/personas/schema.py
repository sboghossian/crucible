"""Pydantic models for persona configuration (YAML/JSON)."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator


SCORING_KEYS = frozenset(
    {"evidence_quality", "logical_consistency", "practical_feasibility", "novelty"}
)


class ScoringWeights(BaseModel):
    evidence_quality: float = Field(ge=0.0, le=1.0)
    logical_consistency: float = Field(ge=0.0, le=1.0)
    practical_feasibility: float = Field(ge=0.0, le=1.0)
    novelty: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def weights_sum_to_one(self) -> "ScoringWeights":
        total = (
            self.evidence_quality
            + self.logical_consistency
            + self.practical_feasibility
            + self.novelty
        )
        if abs(total - 1.0) > 0.01:
            raise ValueError(
                f"scoring_weights must sum to 1.0, got {total:.3f}"
            )
        return self

    def as_dict(self) -> dict[str, float]:
        return {
            "evidence_quality": self.evidence_quality,
            "logical_consistency": self.logical_consistency,
            "practical_feasibility": self.practical_feasibility,
            "novelty": self.novelty,
        }


class PersonaConfig(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    role: str = Field(min_length=1, max_length=128)
    bias: str = Field(default="", max_length=256)
    scoring_weights: ScoringWeights
    system_prompt: str = Field(min_length=10)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    icon: str = Field(default="🤖", max_length=8)
    color: str = Field(default="#888888", max_length=16)

    @field_validator("name")
    @classmethod
    def name_is_slug(cls, v: str) -> str:
        """Names are used as dict keys — normalise to lowercase, underscores."""
        return v.strip().lower().replace(" ", "_").replace("-", "_")
