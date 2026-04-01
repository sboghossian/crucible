"""Tests for Agent Society Phase 2 — persistent identity, XP economy."""

from __future__ import annotations

from pathlib import Path

import pytest

from crucible.society.identity import AgentIdentity, Level, xp_to_level
from crucible.society.economy import XPEconomy, XPEvent, XP_REWARDS
from crucible.society.personality import PersonalityDrift, TRAIT_NAMES, MAX_DRIFT_PER_CYCLE
from crucible.society.relationships import AgentRelationship, RelationshipGraph, AUTONOMOUS_TEAM_THRESHOLD
from crucible.society.language import CompressionToken, EmergentLanguage, ADOPTION_THRESHOLD
from crucible.society.skills import Skill, SkillInventory
from crucible.society.store import SocietyStore


# ------------------------------------------------------------------ #
# Fixtures                                                             #
# ------------------------------------------------------------------ #

@pytest.fixture
def tmp_store(tmp_path: Path) -> SocietyStore:
    return SocietyStore(db_path=tmp_path / "test_society.db")


@pytest.fixture
def alice() -> AgentIdentity:
    return AgentIdentity(name="alice", agent_type="researcher")


@pytest.fixture
def bob() -> AgentIdentity:
    return AgentIdentity(name="bob", agent_type="pragmatist")


# ------------------------------------------------------------------ #
# XP Economy                                                           #
# ------------------------------------------------------------------ #

class TestXPEconomy:
    def test_rewards_match_spec(self) -> None:
        assert XP_REWARDS[XPEvent.TEACHING] == 20
        assert XP_REWARDS[XPEvent.LEARNING] == 5
        assert XP_REWARDS[XPEvent.TASK_SUCCESS] == 10
        assert XP_REWARDS[XPEvent.TASK_FAILURE] == 0
        assert XP_REWARDS[XPEvent.DEBATE_WIN] == 8
        assert XP_REWARDS[XPEvent.ACCURATE_PREDICTION] == 8
        assert XP_REWARDS[XPEvent.INACCURATE_PREDICTION] == -2
        assert XP_REWARDS[XPEvent.NOVEL_TOKEN_ADOPTED] == 15

    def test_award_teaching(self) -> None:
        assert XPEconomy.award(XPEvent.TEACHING) == 20

    def test_award_task_failure_is_zero(self) -> None:
        assert XPEconomy.award(XPEvent.TASK_FAILURE) == 0

    def test_compute_transaction_increases_balance(self) -> None:
        tx = XPEconomy.compute_transaction(
            agent_id="test-id",
            event=XPEvent.TASK_SUCCESS,
            current_balance=50,
        )
        assert tx.amount == 10
        assert tx.balance_after == 60

    def test_compute_transaction_no_negative_balance(self) -> None:
        tx = XPEconomy.compute_transaction(
            agent_id="test-id",
            event=XPEvent.INACCURATE_PREDICTION,
            current_balance=0,
        )
        assert tx.balance_after == 0  # clamped, not negative

    def test_transaction_serialisation(self) -> None:
        tx = XPEconomy.compute_transaction("id", XPEvent.TEACHING, 100, "ctx")
        d = tx.to_dict()
        assert d["event"] == "teaching"
        assert d["amount"] == 20
        assert d["balance_after"] == 120


class TestLeveling:
    def test_level_thresholds(self) -> None:
        assert xp_to_level(0) == Level.NOVICE
        assert xp_to_level(99) == Level.NOVICE
        assert xp_to_level(100) == Level.APPRENTICE
        assert xp_to_level(499) == Level.APPRENTICE
        assert xp_to_level(500) == Level.JOURNEYMAN
        assert xp_to_level(1999) == Level.JOURNEYMAN
        assert xp_to_level(2000) == Level.EXPERT
        assert xp_to_level(9999) == Level.EXPERT
        assert xp_to_level(10000) == Level.MASTER
        assert xp_to_level(999_999) == Level.MASTER

    def test_identity_level_property(self, alice: AgentIdentity) -> None:
        assert alice.level == Level.NOVICE
        alice.add_xp(200)
        assert alice.level == Level.APPRENTICE

    def test_xp_to_next_level(self, alice: AgentIdentity) -> None:
        alice.xp = 0
        assert alice.xp_to_next_level == 100
        alice.xp = 10_000
        assert alice.xp_to_next_level is None  # Master

    def test_add_xp_clamps_at_zero(self, alice: AgentIdentity) -> None:
        alice.xp = 0
        alice.add_xp(-999)
        assert alice.xp == 0


# ------------------------------------------------------------------ #
# Personality drift                                                    #
# ------------------------------------------------------------------ #

class TestPersonalityDrift:
    def test_drift_stays_within_bounds(self) -> None:
        traits = {t: 0.5 for t in TRAIT_NAMES}
        for _ in range(1000):
            traits = PersonalityDrift.compute_drift(
                traits, task_succeeded=True, collaborated=True, novel_approach=True
            )
        for v in traits.values():
            assert 0.0 <= v <= 1.0, f"trait out of bounds: {v}"

    def test_max_change_per_cycle(self) -> None:
        traits = {t: 0.5 for t in TRAIT_NAMES}
        new_traits = PersonalityDrift.compute_drift(
            traits, task_succeeded=True, collaborated=False
        )
        change = PersonalityDrift.max_change(traits, new_traits)
        assert change <= MAX_DRIFT_PER_CYCLE + 1e-9

    def test_failure_increases_caution(self) -> None:
        traits = {t: 0.5 for t in TRAIT_NAMES}
        new_traits = PersonalityDrift.compute_drift(
            traits, task_succeeded=False, collaborated=False
        )
        assert new_traits["caution"] > traits["caution"]

    def test_collaboration_increases_collab_trait(self) -> None:
        traits = {t: 0.5 for t in TRAIT_NAMES}
        new_traits = PersonalityDrift.compute_drift(
            traits, task_succeeded=True, collaborated=True
        )
        assert new_traits["collaboration"] > traits["collaboration"]

    def test_novel_approach_raises_creativity(self) -> None:
        traits = {t: 0.5 for t in TRAIT_NAMES}
        new_traits = PersonalityDrift.compute_drift(
            traits, task_succeeded=True, collaborated=False, novel_approach=True
        )
        assert new_traits["creativity"] > traits["creativity"]

    def test_traits_clamped_at_one(self) -> None:
        traits = {t: 1.0 for t in TRAIT_NAMES}
        new_traits = PersonalityDrift.compute_drift(
            traits, task_succeeded=True, collaborated=True, novel_approach=True
        )
        for v in new_traits.values():
            assert v <= 1.0


# ------------------------------------------------------------------ #
# Relationships                                                        #
# ------------------------------------------------------------------ #

class TestRelationships:
    def test_default_trust_is_neutral(self) -> None:
        rel = AgentRelationship(agent_id="a", peer_id="b")
        assert rel.trust == 0.5

    def test_success_raises_trust(self) -> None:
        rel = AgentRelationship(agent_id="a", peer_id="b")
        initial = rel.trust
        rel.record_interaction(success=True)
        assert rel.trust > initial

    def test_failure_lowers_trust(self) -> None:
        rel = AgentRelationship(agent_id="a", peer_id="b")
        initial = rel.trust
        rel.record_interaction(success=False)
        assert rel.trust < initial

    def test_trust_clamped_at_one(self) -> None:
        rel = AgentRelationship(agent_id="a", peer_id="b", trust=0.99)
        for _ in range(10):
            rel.record_interaction(success=True)
        assert rel.trust <= 1.0

    def test_trust_clamped_at_zero(self) -> None:
        rel = AgentRelationship(agent_id="a", peer_id="b", trust=0.01)
        for _ in range(10):
            rel.record_interaction(success=False)
        assert rel.trust >= 0.0

    def test_can_form_team_above_threshold(self) -> None:
        rel = AgentRelationship(agent_id="a", peer_id="b", trust=AUTONOMOUS_TEAM_THRESHOLD)
        assert rel.can_form_team

    def test_cannot_form_team_below_threshold(self) -> None:
        rel = AgentRelationship(agent_id="a", peer_id="b", trust=AUTONOMOUS_TEAM_THRESHOLD - 0.01)
        assert not rel.can_form_team

    def test_success_rate(self) -> None:
        rel = AgentRelationship(agent_id="a", peer_id="b")
        rel.record_interaction(success=True)
        rel.record_interaction(success=True)
        rel.record_interaction(success=False)
        assert abs(rel.success_rate - 2 / 3) < 0.001

    def test_graph_symmetric_storage(self) -> None:
        graph = RelationshipGraph()
        graph.record("alice", "bob", success=True)
        graph.record("bob", "alice", success=False)
        assert graph.get("alice", "bob").trust != graph.get("bob", "alice").trust

    def test_graph_autonomous_teams(self) -> None:
        graph = RelationshipGraph()
        # Push trust above threshold for alice→bob
        for _ in range(5):
            graph.record("alice", "bob", success=True)
        teams = graph.autonomous_teams()
        assert any(a == "alice" and b == "bob" for a, b in teams)


# ------------------------------------------------------------------ #
# Skill acquisition                                                    #
# ------------------------------------------------------------------ #

class TestSkillInventory:
    def test_add_skill(self) -> None:
        inv = SkillInventory("agent-1")
        skill = inv.add("debate", proficiency=0.6)
        assert inv.has("debate")
        assert skill.proficiency == 0.6

    def test_add_keeps_higher_proficiency(self) -> None:
        inv = SkillInventory("agent-1")
        inv.add("debate", proficiency=0.3)
        inv.add("debate", proficiency=0.8)
        assert inv.get("debate").proficiency == 0.8  # type: ignore[union-attr]

    def test_use_increases_proficiency(self) -> None:
        inv = SkillInventory("agent-1")
        inv.add("code_review", proficiency=0.5)
        before = inv.get("code_review").proficiency  # type: ignore[union-attr]
        inv.use("code_review")
        after = inv.get("code_review").proficiency  # type: ignore[union-attr]
        assert after > before

    def test_use_unknown_skill_returns_none(self) -> None:
        inv = SkillInventory("agent-1")
        result = inv.use("nonexistent")
        assert result is None

    def test_observe_creates_skill_with_low_proficiency(self) -> None:
        inv = SkillInventory("learner")
        skill = inv.observe("pattern_analysis", "teacher-bot", proficiency=0.3)
        assert inv.has("pattern_analysis")
        assert skill.proficiency == 0.3
        assert "teacher-bot" in skill.source

    def test_receive_teaching(self) -> None:
        inv = SkillInventory("student")
        skill = inv.receive_teaching("forecasting", "mentor")
        assert inv.has("forecasting")
        assert "mentor" in skill.source

    def test_top_skills(self) -> None:
        inv = SkillInventory("agent-1")
        inv.add("a", proficiency=0.9)
        inv.add("b", proficiency=0.5)
        inv.add("c", proficiency=0.7)
        top = inv.top_skills(n=2)
        assert [s.name for s in top] == ["a", "c"]


# ------------------------------------------------------------------ #
# Compression tokens / emergent language                               #
# ------------------------------------------------------------------ #

class TestEmergentLanguage:
    def test_token_created_on_first_exchange(self) -> None:
        lang = EmergentLanguage()
        tok = lang.exchange("alice", "bob", "debate architecture", cycle=1)
        assert tok.use_count == 1
        assert not tok.is_active  # not yet at threshold

    def test_token_activates_after_threshold(self) -> None:
        lang = EmergentLanguage()
        for i in range(ADOPTION_THRESHOLD):
            tok = lang.exchange("alice", "bob", "microservices", cycle=i)
        assert tok.is_active

    def test_symmetric_pair_same_token(self) -> None:
        lang = EmergentLanguage()
        tok_ab = lang.exchange("alice", "bob", "concept-x", cycle=1)
        tok_ba = lang.exchange("bob", "alice", "concept-x", cycle=2)
        assert tok_ab.token_id == tok_ba.token_id

    def test_decompress_returns_concept(self) -> None:
        lang = EmergentLanguage()
        tok = lang.exchange("a", "b", "full concept description", cycle=1)
        assert tok.decompress() == "full concept description"

    def test_decay(self) -> None:
        lang = EmergentLanguage()
        for i in range(ADOPTION_THRESHOLD):
            tok = lang.exchange("a", "b", "old-concept", cycle=i)
        assert tok.is_active
        pruned = lang.prune_decayed(current_cycle=10_000)
        assert tok in pruned
        assert not tok.is_active

    def test_active_tokens_list(self) -> None:
        lang = EmergentLanguage()
        for i in range(ADOPTION_THRESHOLD):
            lang.exchange("a", "b", "activated", cycle=i)
        lang.exchange("a", "b", "not-yet", cycle=0)  # only 1 use
        active = lang.active_tokens()
        names = [t.concept for t in active]
        assert "activated" in names
        assert "not-yet" not in names


# ------------------------------------------------------------------ #
# SQLite persistence roundtrip                                         #
# ------------------------------------------------------------------ #

class TestSocietyStorePersistence:
    def test_save_and_retrieve_identity(
        self, tmp_store: SocietyStore, alice: AgentIdentity
    ) -> None:
        alice.add_xp(200)
        tmp_store.save_identity(alice)
        retrieved = tmp_store.get_identity(alice.agent_id)
        assert retrieved is not None
        assert retrieved.name == "alice"
        assert retrieved.xp == 200
        assert retrieved.level == Level.APPRENTICE

    def test_creator_anchor_preserved(
        self, tmp_store: SocietyStore, alice: AgentIdentity
    ) -> None:
        alice.creator = "Steph"  # immutable per spec
        tmp_store.save_identity(alice)
        retrieved = tmp_store.get_identity(alice.agent_id)
        assert retrieved is not None
        assert retrieved.creator == "Steph"

    def test_list_identities_ordered_by_xp(
        self, tmp_store: SocietyStore, alice: AgentIdentity, bob: AgentIdentity
    ) -> None:
        alice.add_xp(100)
        bob.add_xp(500)
        tmp_store.save_identity(alice)
        tmp_store.save_identity(bob)
        ids = tmp_store.list_identities()
        assert ids[0].name == "bob"
        assert ids[1].name == "alice"

    def test_xp_transaction_roundtrip(
        self, tmp_store: SocietyStore, alice: AgentIdentity
    ) -> None:
        tmp_store.save_identity(alice)
        tx = XPEconomy.compute_transaction(alice.agent_id, XPEvent.TEACHING, alice.xp)
        tmp_store.save_xp_transaction(tx)
        history = tmp_store.get_xp_history(alice.agent_id)
        assert len(history) == 1
        assert history[0]["event"] == "teaching"
        assert history[0]["amount"] == 20

    def test_relationship_roundtrip(
        self, tmp_store: SocietyStore
    ) -> None:
        rel = AgentRelationship(agent_id="alice", peer_id="bob")
        rel.record_interaction(success=True)
        tmp_store.save_relationship(rel)
        retrieved = tmp_store.get_relationship("alice", "bob")
        assert retrieved is not None
        assert retrieved.trust > 0.5
        assert retrieved.collaboration_count == 1

    def test_skill_roundtrip(
        self, tmp_store: SocietyStore, alice: AgentIdentity
    ) -> None:
        tmp_store.save_identity(alice)
        skill = Skill(name="pattern_analysis", proficiency=0.75, source="self")
        tmp_store.save_skill(alice.agent_id, skill)
        skills = tmp_store.get_skills(alice.agent_id)
        assert len(skills) == 1
        assert skills[0].name == "pattern_analysis"
        assert abs(skills[0].proficiency - 0.75) < 0.001

    def test_compression_token_roundtrip(
        self, tmp_store: SocietyStore
    ) -> None:
        lang = EmergentLanguage()
        for i in range(ADOPTION_THRESHOLD):
            tok = lang.exchange("alice", "bob", "architectural-debt", cycle=i)
        tmp_store.save_token(tok)
        tokens = tmp_store.list_tokens(active_only=True)
        assert len(tokens) == 1
        assert tokens[0].concept == "architectural-debt"
        assert tokens[0].is_active

    def test_personality_snapshot_roundtrip(
        self, tmp_store: SocietyStore, alice: AgentIdentity
    ) -> None:
        from crucible.society.personality import PersonalitySnapshot
        snapshot = PersonalitySnapshot(
            agent_id=alice.agent_id,
            traits={t: 0.5 for t in TRAIT_NAMES},
            cycle=1,
            reason="initial",
        )
        tmp_store.save_personality_snapshot(snapshot)
        history = tmp_store.get_personality_history(alice.agent_id)
        assert len(history) == 1
        assert history[0].reason == "initial"

    def test_reset_clears_all_data(
        self, tmp_store: SocietyStore, alice: AgentIdentity
    ) -> None:
        tmp_store.save_identity(alice)
        assert len(tmp_store.list_identities()) == 1
        tmp_store.reset()
        assert tmp_store.list_identities() == []

    def test_get_identity_by_name(
        self, tmp_store: SocietyStore, alice: AgentIdentity
    ) -> None:
        tmp_store.save_identity(alice)
        retrieved = tmp_store.get_identity_by_name("alice")
        assert retrieved is not None
        assert retrieved.agent_id == alice.agent_id
