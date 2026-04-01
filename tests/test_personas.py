"""Tests for custom persona definitions via YAML/JSON."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from crucible.personas import (
    PersonaConfig,
    ScoringWeights,
    config_to_persona,
    filter_personas,
    load_persona_file,
    load_personas_dir,
    validate_persona_dict,
)
from crucible.debate.personas import Persona


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_PERSONA_DICT: dict[str, Any] = {
    "name": "The Economist",
    "role": "Cost-benefit analyst",
    "bias": "Evaluates everything through financial impact and ROI",
    "scoring_weights": {
        "evidence_quality": 0.20,
        "logical_consistency": 0.30,
        "practical_feasibility": 0.40,
        "novelty": 0.10,
    },
    "system_prompt": (
        "You are The Economist. Every argument you make centers on financial "
        "impact, ROI, and resource efficiency."
    ),
    "temperature": 0.7,
    "icon": "📊",
    "color": "#4CAF50",
}

VALID_YAML = textwrap.dedent("""\
    name: "oracle"
    role: "The Oracle"
    bias: "Predicts second-order effects"
    scoring_weights:
      evidence_quality: 0.30
      logical_consistency: 0.30
      practical_feasibility: 0.20
      novelty: 0.20
    system_prompt: |
      You are The Oracle. You reason about second and third-order consequences.
      You challenge the room to think past the obvious.
    temperature: 0.8
    icon: "🔮"
    color: "#673AB7"
""")


# ---------------------------------------------------------------------------
# schema / validator tests
# ---------------------------------------------------------------------------


def test_valid_persona_dict():
    config = validate_persona_dict(VALID_PERSONA_DICT)
    assert isinstance(config, PersonaConfig)
    assert config.name == "the_economist"  # normalised to snake_case
    assert config.role == "Cost-benefit analyst"


def test_scoring_weights_sum_validation():
    bad = {**VALID_PERSONA_DICT, "scoring_weights": {
        "evidence_quality": 0.50,
        "logical_consistency": 0.50,
        "practical_feasibility": 0.50,
        "novelty": 0.50,
    }}
    with pytest.raises(ValueError, match="sum to 1.0"):
        validate_persona_dict(bad)


def test_missing_required_field():
    incomplete = {k: v for k, v in VALID_PERSONA_DICT.items() if k != "system_prompt"}
    with pytest.raises(ValueError, match="Invalid persona config"):
        validate_persona_dict(incomplete)


def test_missing_scoring_weights_key():
    bad = {**VALID_PERSONA_DICT, "scoring_weights": {
        "evidence_quality": 0.50,
        "logical_consistency": 0.50,
        # missing practical_feasibility and novelty
    }}
    with pytest.raises(ValueError):
        validate_persona_dict(bad)


def test_weight_out_of_range():
    bad = {**VALID_PERSONA_DICT, "scoring_weights": {
        "evidence_quality": -0.10,
        "logical_consistency": 0.50,
        "practical_feasibility": 0.40,
        "novelty": 0.20,
    }}
    with pytest.raises(ValueError):
        validate_persona_dict(bad)


def test_temperature_out_of_range():
    bad = {**VALID_PERSONA_DICT, "temperature": 5.0}
    with pytest.raises(ValueError):
        validate_persona_dict(bad)


def test_config_to_persona():
    config = validate_persona_dict(VALID_PERSONA_DICT)
    persona = config_to_persona(config)
    assert isinstance(persona, Persona)
    assert persona.name == "the_economist"
    assert persona.role == "Cost-benefit analyst"
    weights = persona.scoring_weight
    assert abs(sum(weights.values()) - 1.0) < 0.01


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------


def test_load_yaml_file(tmp_path: Path):
    yaml_file = tmp_path / "oracle.yaml"
    yaml_file.write_text(VALID_YAML, encoding="utf-8")
    persona = load_persona_file(yaml_file)
    assert persona.name == "oracle"
    assert persona.role == "The Oracle"
    assert "Oracle" in persona.system_prompt


def test_load_yml_extension(tmp_path: Path):
    yml_file = tmp_path / "oracle.yml"
    yml_file.write_text(VALID_YAML, encoding="utf-8")
    persona = load_persona_file(yml_file)
    assert persona.name == "oracle"


# ---------------------------------------------------------------------------
# JSON loading
# ---------------------------------------------------------------------------


def test_load_json_file(tmp_path: Path):
    json_file = tmp_path / "economist.json"
    json_file.write_text(json.dumps(VALID_PERSONA_DICT), encoding="utf-8")
    persona = load_persona_file(json_file)
    assert persona.name == "the_economist"


# ---------------------------------------------------------------------------
# Directory loading
# ---------------------------------------------------------------------------


def test_load_personas_dir(tmp_path: Path):
    for i, name in enumerate(("alpha", "beta", "gamma")):
        data = {
            **VALID_PERSONA_DICT,
            "name": name,
            "scoring_weights": {
                "evidence_quality": 0.25,
                "logical_consistency": 0.25,
                "practical_feasibility": 0.25,
                "novelty": 0.25,
            },
        }
        (tmp_path / f"{name}.yaml").write_text(
            json.dumps(data).replace("{", "").replace("}", ""),  # not valid yaml, use json ext
            encoding="utf-8",
        )
    # Re-write as proper JSON instead
    for name in ("alpha", "beta", "gamma"):
        (tmp_path / f"{name}.yaml").unlink()
        data = {
            **VALID_PERSONA_DICT,
            "name": name,
            "scoring_weights": {
                "evidence_quality": 0.25,
                "logical_consistency": 0.25,
                "practical_feasibility": 0.25,
                "novelty": 0.25,
            },
        }
        (tmp_path / f"{name}.json").write_text(json.dumps(data), encoding="utf-8")

    personas = load_personas_dir(tmp_path)
    assert len(personas) == 3
    names = {p.name for p in personas}
    assert names == {"alpha", "beta", "gamma"}


def test_load_personas_dir_skips_invalid(tmp_path: Path):
    """Files that fail validation are skipped with a warning, not errors."""
    good_data = {
        **VALID_PERSONA_DICT,
        "name": "good",
        "scoring_weights": {
            "evidence_quality": 0.25,
            "logical_consistency": 0.25,
            "practical_feasibility": 0.25,
            "novelty": 0.25,
        },
    }
    (tmp_path / "good.json").write_text(json.dumps(good_data), encoding="utf-8")
    # Bad file: weights don't sum to 1
    bad_data = {**VALID_PERSONA_DICT, "name": "bad", "scoring_weights": {
        "evidence_quality": 0.99,
        "logical_consistency": 0.99,
        "practical_feasibility": 0.99,
        "novelty": 0.99,
    }}
    (tmp_path / "bad.json").write_text(json.dumps(bad_data), encoding="utf-8")

    personas = load_personas_dir(tmp_path)
    assert len(personas) == 1
    assert personas[0].name == "good"


def test_load_personas_dir_not_a_dir():
    with pytest.raises(NotADirectoryError):
        load_personas_dir("/nonexistent/path/xyz")


def test_load_personas_dir_ignores_non_yaml_json(tmp_path: Path):
    (tmp_path / "readme.txt").write_text("ignore me", encoding="utf-8")
    (tmp_path / "script.py").write_text("# ignore me", encoding="utf-8")
    personas = load_personas_dir(tmp_path)
    assert personas == []


def test_unsupported_extension(tmp_path: Path):
    bad_file = tmp_path / "persona.toml"
    bad_file.write_text("[persona]", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported"):
        load_persona_file(bad_file)


# ---------------------------------------------------------------------------
# filter_personas
# ---------------------------------------------------------------------------


def test_filter_personas_by_name():
    personas = [
        Persona(name="alpha", role="Alpha", system_prompt="A" * 20, scoring_weight={"evidence_quality": 0.25, "logical_consistency": 0.25, "practical_feasibility": 0.25, "novelty": 0.25}),
        Persona(name="beta", role="Beta", system_prompt="B" * 20, scoring_weight={"evidence_quality": 0.25, "logical_consistency": 0.25, "practical_feasibility": 0.25, "novelty": 0.25}),
        Persona(name="gamma", role="Gamma", system_prompt="C" * 20, scoring_weight={"evidence_quality": 0.25, "logical_consistency": 0.25, "practical_feasibility": 0.25, "novelty": 0.25}),
    ]
    selected = filter_personas(personas, ["alpha", "gamma"])
    assert len(selected) == 2
    assert {p.name for p in selected} == {"alpha", "gamma"}


def test_filter_personas_unknown_name_raises():
    personas = [
        Persona(name="alpha", role="Alpha", system_prompt="A" * 20, scoring_weight={"evidence_quality": 0.25, "logical_consistency": 0.25, "practical_feasibility": 0.25, "novelty": 0.25}),
    ]
    with pytest.raises(ValueError, match="Unknown persona"):
        filter_personas(personas, ["nonexistent"])


# ---------------------------------------------------------------------------
# Integration: custom personas work in DebateProtocol
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_custom_personas_in_debate_protocol():
    """Custom personas are used instead of the built-in 4."""
    from crucible.debate.protocol import DebateProtocol

    custom = [
        Persona(
            name="engineer",
            role="The Engineer",
            system_prompt="You are The Engineer. Focus on technical correctness.",
            scoring_weight={"evidence_quality": 0.25, "logical_consistency": 0.25, "practical_feasibility": 0.25, "novelty": 0.25},
        ),
        Persona(
            name="designer",
            role="The Designer",
            system_prompt="You are The Designer. Focus on user experience.",
            scoring_weight={"evidence_quality": 0.25, "logical_consistency": 0.25, "practical_feasibility": 0.25, "novelty": 0.25},
        ),
    ]

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text='{"evidence_quality": 7, "logical_consistency": 7, "practical_feasibility": 7, "novelty": 7}')]

    mock_client = MagicMock()
    mock_client.messages = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_message)

    protocol = DebateProtocol(client=mock_client, personas=custom)
    assert protocol._personas == custom

    transcript = await protocol.run(topic="Test topic")
    # Only 2 personas — 3 rounds * 2 = 6 statements
    assert len([s for s in transcript.statements if s.round == 1]) == 2
    assert len([s for s in transcript.statements if s.round == 2]) == 2
    assert len([s for s in transcript.statements if s.round == 3]) == 2
    assert {s.persona_name for s in transcript.statements} == {"engineer", "designer"}


# ---------------------------------------------------------------------------
# Built-in persona YAML files are valid
# ---------------------------------------------------------------------------


def test_builtin_persona_yaml_files_are_valid():
    """The 8 YAML files in personas/ at repo root all parse and validate."""
    import importlib.util
    import os

    # Find the repo root (2 levels up from tests/)
    tests_dir = Path(__file__).parent
    repo_root = tests_dir.parent
    personas_dir = repo_root / "personas"

    if not personas_dir.exists():
        pytest.skip("personas/ directory not found at repo root")

    personas = load_personas_dir(personas_dir)
    assert len(personas) >= 8, f"Expected at least 8 built-in personas, got {len(personas)}"
    names = {p.name for p in personas}
    expected = {
        "pragmatist", "visionary", "skeptic", "user_advocate",
        "economist", "security_auditor", "devil_advocate", "minimalist",
    }
    assert expected.issubset(names), f"Missing: {expected - names}"
