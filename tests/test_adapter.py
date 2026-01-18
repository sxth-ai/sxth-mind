"""Tests for adapter system."""

import os
import sys

import pytest

# Add examples to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.sales import SalesAdapter
from sxth_mind.schemas import ProjectMind, UserMind


class TestSalesAdapter:
    @pytest.fixture
    def adapter(self):
        return SalesAdapter()

    def test_name(self, adapter):
        assert adapter.name == "sales"
        assert adapter.display_name == "Sales Assistant"

    def test_identity_types(self, adapter):
        types = adapter.get_identity_types()

        assert len(types) == 4
        assert any(t["key"] == "hunter" for t in types)
        assert any(t["key"] == "farmer" for t in types)

    def test_journey_stages(self, adapter):
        stages = adapter.get_journey_stages()

        assert len(stages) == 6
        stage_keys = [s["key"] for s in stages]
        assert "prospecting" in stage_keys
        assert "closing" in stage_keys

    def test_detect_journey_stage_new_user(self, adapter):
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="project_1",
            interaction_count=1
        )

        stage = adapter.detect_journey_stage(project_mind)
        assert stage == "prospecting"

    def test_detect_journey_stage_from_context(self, adapter):
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="project_1",
            interaction_count=10
        )
        project_mind.set_context_field("deal_stage", "negotiating")

        stage = adapter.detect_journey_stage(project_mind)
        assert stage == "negotiating"

    def test_detect_journey_stage_by_interactions(self, adapter):
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="project_1",
            interaction_count=5
        )

        stage = adapter.detect_journey_stage(project_mind)
        assert stage == "qualifying"

    def test_nudge_templates(self, adapter):
        templates = adapter.get_nudge_templates()

        assert "stalled_deal" in templates
        assert "follow_up_reminder" in templates
        assert templates["stalled_deal"]["priority"] == 7

    def test_insight_types(self, adapter):
        types = adapter.get_insight_types()

        assert len(types) == 4
        assert any(t["key"] == "pattern" for t in types)

    def test_get_system_prompt(self, adapter):
        user_mind = UserMind(user_id="user_1")
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="project_1",
            interaction_count=1
        )

        prompt = adapter.get_system_prompt(user_mind, project_mind)

        assert "Sales AI assistant" in prompt
        assert "prospecting" in prompt.lower() or "Prospecting" in prompt

    def test_update_after_interaction_tracks_patterns(self, adapter):
        user_mind = UserMind(user_id="user_1")
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="project_1"
        )

        # Simulate follow-up messages
        for _ in range(3):
            adapter.update_after_interaction(
                user_mind,
                project_mind,
                "Following up with the lead",
                "Great, what's your approach?"
            )

        assert user_mind.total_interactions == 3
        assert "follow_up" in user_mind.patterns.get("themes", [])
        assert user_mind.patterns.get("follow_up_count", 0) == 3
