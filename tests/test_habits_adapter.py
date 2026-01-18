"""Tests for HabitCoachAdapter."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.habits import HabitCoachAdapter
from sxth_mind.schemas import ProjectMind, UserMind


class TestHabitCoachAdapter:
    @pytest.fixture
    def adapter(self):
        return HabitCoachAdapter()

    def test_name(self, adapter):
        assert adapter.name == "habits"
        assert adapter.display_name == "Habit Coach"

    def test_identity_types(self, adapter):
        types = adapter.get_identity_types()

        assert len(types) == 4
        assert any(t["key"] == "all_or_nothing" for t in types)
        assert any(t["key"] == "slow_builder" for t in types)

    def test_journey_stages(self, adapter):
        stages = adapter.get_journey_stages()

        assert len(stages) == 5
        stage_keys = [s["key"] for s in stages]
        assert "starting" in stage_keys
        assert "struggling" in stage_keys
        assert "building" in stage_keys
        assert "consistent" in stage_keys
        assert "recovering" in stage_keys

    def test_detect_journey_stage_new_user(self, adapter):
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="habit_1",
            interaction_count=2,
        )

        stage = adapter.detect_journey_stage(project_mind)
        assert stage == "starting"

    def test_detect_journey_stage_consistent(self, adapter):
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="habit_1",
            interaction_count=20,
            momentum_score=0.8,
        )
        project_mind.set_progress_field("current_streak", 14)

        stage = adapter.detect_journey_stage(project_mind)
        assert stage == "consistent"

    def test_detect_journey_stage_recovering(self, adapter):
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="habit_1",
            interaction_count=10,
            days_since_activity=5,
        )
        project_mind.set_progress_field("current_streak", 0)

        stage = adapter.detect_journey_stage(project_mind)
        assert stage == "recovering"

    def test_nudge_templates(self, adapter):
        templates = adapter.get_nudge_templates()

        assert "streak_reminder" in templates
        assert "missed_day" in templates
        assert "comeback" in templates

    def test_update_tracks_blockers(self, adapter):
        user_mind = UserMind(user_id="user_1")
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="habit_1"
        )

        adapter.update_after_interaction(
            user_mind,
            project_mind,
            "I was too tired to exercise",
            "That's understandable. Rest is important too."
        )

        assert "fatigue" in user_mind.patterns.get("common_blockers", [])

    def test_update_tracks_completions(self, adapter):
        user_mind = UserMind(user_id="user_1")
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="habit_1"
        )

        adapter.update_after_interaction(
            user_mind,
            project_mind,
            "I did it! Completed my workout",
            "Great job!"
        )

        assert project_mind.get_progress_field("completions") == 1
        assert project_mind.get_progress_field("current_streak") == 1

    def test_streak_resets_on_skip(self, adapter):
        user_mind = UserMind(user_id="user_1")
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="habit_1"
        )
        project_mind.set_progress_field("current_streak", 5)

        adapter.update_after_interaction(
            user_mind,
            project_mind,
            "I missed yesterday",
            "That's okay, let's get back on track."
        )

        assert project_mind.get_progress_field("current_streak") == 0
