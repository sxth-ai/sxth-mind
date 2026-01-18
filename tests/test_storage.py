"""Tests for storage backends."""

import pytest

from sxth_mind.schemas import ConversationMemory, ProjectMind, UserMind
from sxth_mind.storage import MemoryStorage


class TestMemoryStorage:
    @pytest.fixture
    def storage(self):
        return MemoryStorage()

    @pytest.mark.asyncio
    async def test_user_mind_crud(self, storage):
        # Create
        user_mind = UserMind(user_id="user_1")
        await storage.save_user_mind(user_mind)

        # Read
        loaded = await storage.get_user_mind("user_1")
        assert loaded is not None
        assert loaded.user_id == "user_1"

        # Update
        loaded.trust_score = 0.8
        await storage.save_user_mind(loaded)
        reloaded = await storage.get_user_mind("user_1")
        assert reloaded.trust_score == 0.8

        # Delete
        await storage.delete_user_mind("user_1")
        deleted = await storage.get_user_mind("user_1")
        assert deleted is None

    @pytest.mark.asyncio
    async def test_project_mind_crud(self, storage):
        # First create a user mind
        user_mind = UserMind(id="um_1", user_id="user_1")
        await storage.save_user_mind(user_mind)

        # Create project mind
        project_mind = ProjectMind(
            user_mind_id="um_1",
            project_id="project_1"
        )
        await storage.save_project_mind(project_mind)

        # Read
        loaded = await storage.get_project_mind("user_1", "project_1")
        assert loaded is not None
        assert loaded.project_id == "project_1"

    @pytest.mark.asyncio
    async def test_get_project_minds_for_user(self, storage):
        user_mind = UserMind(id="um_1", user_id="user_1")
        await storage.save_user_mind(user_mind)

        # Create multiple projects
        for i in range(3):
            pm = ProjectMind(user_mind_id="um_1", project_id=f"project_{i}")
            await storage.save_project_mind(pm)

        projects = await storage.get_project_minds_for_user("user_1")
        assert len(projects) == 3

    @pytest.mark.asyncio
    async def test_memory_crud(self, storage):
        memory = ConversationMemory(project_mind_id="pm_1")
        memory.add_message("user", "Hello")
        await storage.save_memory(memory)

        loaded = await storage.get_memory("pm_1")
        assert loaded is not None
        assert len(loaded.messages) == 1

    @pytest.mark.asyncio
    async def test_stats(self, storage):
        stats = storage.stats()
        assert stats["user_minds"] == 0

        await storage.save_user_mind(UserMind(user_id="user_1"))
        stats = storage.stats()
        assert stats["user_minds"] == 1

    @pytest.mark.asyncio
    async def test_clear(self, storage):
        await storage.save_user_mind(UserMind(user_id="user_1"))
        assert storage.stats()["user_minds"] == 1

        storage.clear()
        assert storage.stats()["user_minds"] == 0
