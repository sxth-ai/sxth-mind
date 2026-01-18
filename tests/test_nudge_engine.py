"""Tests for BaselineNudgeEngine."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.habits import HabitCoachAdapter
from examples.sales import SalesAdapter
from sxth_mind.engine import BaselineNudgeEngine
from sxth_mind.schemas import ProjectMind, UserMind
from sxth_mind.storage import MemoryStorage


class TestBaselineNudgeEngine:
    @pytest.fixture
    def storage(self):
        return MemoryStorage()

    @pytest.fixture
    def habits_adapter(self):
        return HabitCoachAdapter()

    @pytest.fixture
    def sales_adapter(self):
        return SalesAdapter()

    @pytest.mark.asyncio
    async def test_no_nudges_for_new_user(self, habits_adapter, storage):
        engine = BaselineNudgeEngine(habits_adapter, storage)

        # Create a new user with no inactivity
        user_mind = UserMind(id="um_1", user_id="user_1")
        await storage.save_user_mind(user_mind)

        project_mind = ProjectMind(
            id="pm_1",
            user_mind_id="um_1",
            project_id="habit_1",
            days_since_activity=0,
        )
        await storage.save_project_mind(project_mind)

        nudges = await engine.check_and_generate("user_1")
        assert len(nudges) == 0

    @pytest.mark.asyncio
    async def test_inactivity_nudge(self, habits_adapter, storage):
        engine = BaselineNudgeEngine(habits_adapter, storage)

        user_mind = UserMind(id="um_1", user_id="user_1")
        await storage.save_user_mind(user_mind)

        project_mind = ProjectMind(
            id="pm_1",
            user_mind_id="um_1",
            project_id="habit_1",
            days_since_activity=8,  # Over threshold
        )
        await storage.save_project_mind(project_mind)

        nudges = await engine.check_and_generate("user_1")
        assert len(nudges) >= 1
        assert any(n.nudge_type == "comeback" for n in nudges)

    @pytest.mark.asyncio
    async def test_streak_reminder(self, habits_adapter, storage):
        engine = BaselineNudgeEngine(habits_adapter, storage)

        user_mind = UserMind(id="um_1", user_id="user_1")
        await storage.save_user_mind(user_mind)

        project_mind = ProjectMind(
            id="pm_1",
            user_mind_id="um_1",
            project_id="habit_1",
            days_since_activity=1,
        )
        project_mind.set_progress_field("current_streak", 5)
        await storage.save_project_mind(project_mind)

        nudges = await engine.check_and_generate("user_1")
        assert any(n.nudge_type == "streak_reminder" for n in nudges)

    @pytest.mark.asyncio
    async def test_respects_nudge_frequency_off(self, habits_adapter, storage):
        engine = BaselineNudgeEngine(habits_adapter, storage)

        user_mind = UserMind(
            id="um_1",
            user_id="user_1",
            nudge_frequency="off",
        )
        await storage.save_user_mind(user_mind)

        project_mind = ProjectMind(
            id="pm_1",
            user_mind_id="um_1",
            project_id="habit_1",
            days_since_activity=30,  # Very inactive
        )
        await storage.save_project_mind(project_mind)

        nudges = await engine.check_and_generate("user_1")
        assert len(nudges) == 0  # No nudges because frequency is off

    @pytest.mark.asyncio
    async def test_momentum_drop_nudge(self, sales_adapter, storage):
        engine = BaselineNudgeEngine(sales_adapter, storage)

        user_mind = UserMind(id="um_1", user_id="user_1")
        await storage.save_user_mind(user_mind)

        project_mind = ProjectMind(
            id="pm_1",
            user_mind_id="um_1",
            project_id="deal_1",
            interaction_count=10,  # Had activity
            momentum_score=0.2,  # But momentum dropped
            days_since_activity=0,
        )
        await storage.save_project_mind(project_mind)

        nudges = await engine.check_and_generate("user_1")
        assert any(n.nudge_type == "momentum_drop" for n in nudges)
