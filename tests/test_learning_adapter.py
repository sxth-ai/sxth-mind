"""Tests for LearningAdapter."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.learning import LearningAdapter
from sxth_mind.schemas import ProjectMind, UserMind


class TestLearningAdapter:
    @pytest.fixture
    def adapter(self):
        return LearningAdapter()

    def test_name(self, adapter):
        assert adapter.name == "learning"
        assert adapter.display_name == "Learning Coach"

    def test_identity_types(self, adapter):
        types = adapter.get_identity_types()

        assert len(types) == 4
        assert any(t["key"] == "conceptual" for t in types)
        assert any(t["key"] == "hands_on" for t in types)
        assert any(t["key"] == "structured" for t in types)
        assert any(t["key"] == "explorer" for t in types)

    def test_journey_stages(self, adapter):
        stages = adapter.get_journey_stages()

        assert len(stages) == 6
        stage_keys = [s["key"] for s in stages]
        assert "exploring" in stage_keys
        assert "foundations" in stage_keys
        assert "practicing" in stage_keys
        assert "applying" in stage_keys
        assert "deepening" in stage_keys
        assert "stuck" in stage_keys

    def test_detect_journey_stage_new_user(self, adapter):
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="learn_python",
            interaction_count=2,
        )

        stage = adapter.detect_journey_stage(project_mind)
        assert stage == "exploring"

    def test_detect_journey_stage_practicing(self, adapter):
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="learn_python",
            interaction_count=15,
        )
        project_mind.set_progress_field("exercises_completed", 8)
        project_mind.set_progress_field("projects_completed", 0)

        stage = adapter.detect_journey_stage(project_mind)
        assert stage == "practicing"

    def test_detect_journey_stage_stuck(self, adapter):
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="learn_python",
            interaction_count=10,
        )
        project_mind.set_progress_field("stuck_count", 3)

        stage = adapter.detect_journey_stage(project_mind)
        assert stage == "stuck"

    def test_nudge_templates(self, adapter):
        templates = adapter.get_nudge_templates()

        assert "practice_reminder" in templates
        assert "stuck_help" in templates
        assert "milestone" in templates

    def test_update_tracks_stuck(self, adapter):
        user_mind = UserMind(user_id="user_1")
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="learn_python"
        )

        adapter.update_after_interaction(
            user_mind,
            project_mind,
            "I don't understand this at all, I'm so confused",
            "Let me try explaining it differently..."
        )

        assert project_mind.get_progress_field("stuck_count") == 1

    def test_update_tracks_completions(self, adapter):
        user_mind = UserMind(user_id="user_1")
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="learn_python"
        )

        adapter.update_after_interaction(
            user_mind,
            project_mind,
            "Got it! That makes sense now",
            "Great job understanding that concept!"
        )

        assert project_mind.get_progress_field("exercises_completed") == 1

    def test_update_detects_learning_preference(self, adapter):
        user_mind = UserMind(user_id="user_1")
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="learn_python"
        )

        adapter.update_after_interaction(
            user_mind,
            project_mind,
            "Can you show me an example?",
            "Sure, here's an example..."
        )

        assert user_mind.patterns.get("preferred_explanations") == "examples"
