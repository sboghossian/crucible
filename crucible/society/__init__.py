"""Agent Society — persistent identity, XP economy, and emergent social dynamics."""

from .identity import AgentIdentity, Level
from .economy import XPEconomy, XPEvent, XP_REWARDS
from .personality import PersonalityDrift, TRAIT_NAMES
from .relationships import AgentRelationship, RelationshipGraph
from .language import CompressionToken, EmergentLanguage
from .skills import Skill, SkillInventory

__all__ = [
    "AgentIdentity",
    "Level",
    "XPEconomy",
    "XPEvent",
    "XP_REWARDS",
    "PersonalityDrift",
    "TRAIT_NAMES",
    "AgentRelationship",
    "RelationshipGraph",
    "CompressionToken",
    "EmergentLanguage",
    "Skill",
    "SkillInventory",
]
