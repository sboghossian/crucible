"""Game design documentation team — Creative."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="game_design",
    description="Produces a full Game Design Document (GDD) with mechanics, narrative, systems design, and core loop debate.",
    category="Creative",
    tags=["game design", "gdd", "game mechanics", "narrative", "indie game", "game development"],
    agents=[
        AgentSpec(
            name="Game Designer",
            role="Core mechanics and systems design specialist",
            instructions=(
                "You are a senior game designer. For the given game concept, produce: "
                "elevator pitch (genre, platform, target audience, unique selling point in 50 words), "
                "core gameplay loop (what players do every 30 seconds, 5 minutes, 30 minutes, and 5 hours), "
                "player verbs (list of all actions the player can take), "
                "progression systems (XP, levels, unlocks, skill trees), "
                "economy design (resources, sinks, faucets, balance principles), "
                "difficulty curve design, "
                "and game feel notes (juice, feedback, responsiveness targets)."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Narrative Writer",
            role="Story, world, and character design specialist",
            instructions=(
                "You are a narrative designer. Produce: "
                "world overview and lore (setting, tone, history, rules of the world), "
                "protagonist design (background, motivation, arc, voice), "
                "3 supporting characters with roles in the narrative, "
                "main story arc outline (5-act structure or 3-act if shorter game), "
                "branching narrative moments (3 key decision points with consequences), "
                "environmental storytelling opportunities (how the world tells the story without text), "
                "and a tone guide for all written content (dialogue, UI, loading screens)."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Systems Designer",
            role="Game balance and simulation systems specialist",
            instructions=(
                "You are a systems designer. Design: "
                "combat or challenge system (if applicable): damage formulas, scaling, counters, "
                "AI behavior trees for 3 enemy/NPC types, "
                "procedural generation approach (if applicable), "
                "multiplayer/social systems (if applicable): matchmaking, anti-cheat, social features, "
                "data persistence architecture (save system, cloud sync), "
                "monetization model (premium, F2P, cosmetics-only, subscription), "
                "and live-ops / content update strategy (events, seasons, DLC)."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="UX Designer",
            role="Game UX, UI, and accessibility specialist",
            instructions=(
                "You are a game UX designer. Produce: "
                "HUD design principles (what's always visible, what's on-demand), "
                "menu structure and navigation flow, "
                "onboarding design (tutorial approach: contextual tips vs forced tutorial vs organic discovery), "
                "accessibility features checklist (colorblind modes, subtitle sizes, remappable controls, "
                "motor accessibility options), "
                "UI art style direction (diegetic vs non-diegetic elements, color palette rationale), "
                "and player feedback loops (how does the game communicate success and failure?)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "What core loop mechanic will drive 100+ hours of engagement?",
        "Mastery loop (skill development, precision, competitive ladder)",
        "Collection / progression loop (unlock, build, display, expand)",
        "Social / cooperation loop (multiplayer dependency, shared goals)",
        "Emergent systems loop (open sandbox, player-driven stories)",
    ],
    expected_outputs=[
        "Game Design Document (GDD) — full structure",
        "Core gameplay loop (30s / 5min / 30min / 5hr)",
        "Player verbs and progression system",
        "World overview and narrative arc",
        "3 character designs",
        "Combat / challenge system design",
        "Monetization model",
        "UX/UI design principles and accessibility checklist",
        "Onboarding approach",
    ],
))
