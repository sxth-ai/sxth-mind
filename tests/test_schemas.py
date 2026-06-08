"""Tests for schema models."""

from datetime import timedelta

from sxth_mind._time import utcnow
from sxth_mind.schemas import ProjectMind, UserMind


class TestUserMind:
    def test_create_with_defaults(self):
        user_mind = UserMind(user_id="test_user")

        assert user_mind.user_id == "test_user"
        assert user_mind.trust_score == 0.5
        assert user_mind.total_interactions == 0
        assert user_mind.preferred_tone == "balanced"
        assert user_mind.identity_data == {}
        assert user_mind.patterns == {}

    def test_identity_field_access(self):
        user_mind = UserMind(user_id="test_user")

        # Set and get identity fields
        user_mind.set_identity_field("style", "hunter")
        assert user_mind.get_identity_field("style") == "hunter"
        assert user_mind.get_identity_field("missing", "default") == "default"

    def test_pattern_access(self):
        user_mind = UserMind(user_id="test_user")

        user_mind.set_pattern("outreach", {"avg_touches": 4})
        assert user_mind.get_pattern("outreach") == {"avg_touches": 4}

    def test_increment_interactions(self):
        user_mind = UserMind(user_id="test_user")

        assert user_mind.total_interactions == 0
        user_mind.increment_interactions()
        assert user_mind.total_interactions == 1
        assert user_mind.last_interaction is not None

    def test_trust_grows_with_interactions(self):
        user_mind = UserMind(user_id="test_user")

        start = user_mind.trust_score
        for _ in range(5):
            user_mind.increment_interactions()

        # Trust should climb toward 1.0 but never exceed it.
        assert user_mind.trust_score > start
        assert user_mind.trust_score <= 1.0


class TestProjectMind:
    def test_create_with_defaults(self):
        project_mind = ProjectMind(
            user_mind_id="user_mind_1",
            project_id="project_1"
        )

        assert project_mind.project_id == "project_1"
        assert project_mind.momentum_score == 0.5
        assert project_mind.interaction_count == 0
        assert project_mind.journey_stage is None
        assert project_mind.context_data == {}

    def test_context_field_access(self):
        project_mind = ProjectMind(
            user_mind_id="user_mind_1",
            project_id="project_1"
        )

        project_mind.set_context_field("deal_stage", "negotiating")
        assert project_mind.get_context_field("deal_stage") == "negotiating"

    def test_increment_interactions(self):
        project_mind = ProjectMind(
            user_mind_id="user_mind_1",
            project_id="project_1"
        )

        assert project_mind.interaction_count == 0
        project_mind.increment_interactions()
        assert project_mind.interaction_count == 1

    def test_update_momentum(self):
        project_mind = ProjectMind(
            user_mind_id="user_mind_1",
            project_id="project_1",
            momentum_score=0.5,
            days_since_activity=5
        )

        project_mind.update_momentum()
        assert project_mind.days_since_activity == 0
        assert project_mind.momentum_score == 0.6  # 0.5 + 0.1

    def test_refresh_inactivity_from_last_interaction(self):
        project_mind = ProjectMind(
            user_mind_id="user_mind_1",
            project_id="project_1",
            last_interaction=utcnow() - timedelta(days=4),
        )

        assert project_mind.refresh_inactivity() == 4
        assert project_mind.days_since_activity == 4

    def test_refresh_inactivity_preserves_value_without_timestamp(self):
        # No last_interaction set: keep whatever was provided (don't clobber to 0).
        project_mind = ProjectMind(
            user_mind_id="user_mind_1",
            project_id="project_1",
            days_since_activity=9,
        )

        assert project_mind.refresh_inactivity() == 9

    def test_momentum_decays_with_inactivity(self):
        project_mind = ProjectMind(
            user_mind_id="user_mind_1",
            project_id="project_1",
            momentum_score=0.9,
            days_since_activity=5,
        )

        project_mind.apply_momentum_decay()
        # 0.9 - 0.1 * 5 = 0.4, clamped at 0.0 floor.
        assert project_mind.momentum_score == 0.4

    def test_trust_grows_with_interactions(self):
        project_mind = ProjectMind(
            user_mind_id="user_mind_1",
            project_id="project_1",
        )

        start = project_mind.trust_score
        for _ in range(5):
            project_mind.increment_interactions()

        assert project_mind.trust_score > start
        assert project_mind.trust_score <= 1.0

    def test_derived_conversation_fields_are_owned_belief_state(self):
        # summary/topics are the OWNED derived view; raw messages live in the
        # EvidenceSource, not on ProjectMind.
        project_mind = ProjectMind(user_mind_id="user_mind_1", project_id="project_1")

        assert project_mind.conversation_summary is None
        assert project_mind.topics == []
        assert not hasattr(project_mind, "messages")
