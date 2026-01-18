"""Tests for SQLite storage backend."""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check if aiosqlite is available
pytest.importorskip("aiosqlite")

from sxth_mind.schemas import ConversationMemory, Nudge, ProjectMind, UserMind
from sxth_mind.storage.sqlite import SQLiteStorage


class TestSQLiteStorage:
    """Test SQLite storage backend."""

    @pytest.fixture
    async def storage(self):
        """Create a temporary SQLite storage."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        storage = SQLiteStorage(db_path)
        await storage.initialize()

        yield storage

        # Cleanup
        await storage.close()
        try:
            os.unlink(db_path)
        except OSError:
            pass

    @pytest.mark.asyncio
    async def test_save_and_get_user_mind(self, storage):
        """Should save and retrieve UserMind."""
        user_mind = UserMind(
            id="um_1",
            user_id="user_1",
            trust_score=0.8,
            identity_type="hunter",
        )

        await storage.save_user_mind(user_mind)
        retrieved = await storage.get_user_mind("user_1")

        assert retrieved is not None
        assert retrieved.id == "um_1"
        assert retrieved.user_id == "user_1"
        assert retrieved.trust_score == 0.8
        assert retrieved.identity_type == "hunter"

    @pytest.mark.asyncio
    async def test_get_user_mind_not_found(self, storage):
        """Should return None for unknown user."""
        result = await storage.get_user_mind("unknown")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_user_mind(self, storage):
        """Should update existing UserMind."""
        user_mind = UserMind(id="um_1", user_id="user_1")
        await storage.save_user_mind(user_mind)

        # Update
        user_mind.trust_score = 0.9
        user_mind.identity_type = "farmer"
        await storage.save_user_mind(user_mind)

        # Verify
        retrieved = await storage.get_user_mind("user_1")
        assert retrieved.trust_score == 0.9
        assert retrieved.identity_type == "farmer"

    @pytest.mark.asyncio
    async def test_save_and_get_project_mind(self, storage):
        """Should save and retrieve ProjectMind."""
        # First save user mind
        user_mind = UserMind(id="um_1", user_id="user_1")
        await storage.save_user_mind(user_mind)

        project_mind = ProjectMind(
            id="pm_1",
            user_mind_id="um_1",
            project_id="deal_1",
            journey_stage="prospecting",
            momentum_score=0.7,
        )

        await storage.save_project_mind(project_mind)
        retrieved = await storage.get_project_mind("user_1", "deal_1")

        assert retrieved is not None
        assert retrieved.id == "pm_1"
        assert retrieved.project_id == "deal_1"
        assert retrieved.journey_stage == "prospecting"
        assert retrieved.momentum_score == 0.7

    @pytest.mark.asyncio
    async def test_get_project_mind_not_found(self, storage):
        """Should return None for unknown project."""
        result = await storage.get_project_mind("user_1", "unknown")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_project_minds_for_user(self, storage):
        """Should retrieve all projects for a user."""
        user_mind = UserMind(id="um_1", user_id="user_1")
        await storage.save_user_mind(user_mind)

        pm1 = ProjectMind(id="pm_1", user_mind_id="um_1", project_id="deal_1")
        pm2 = ProjectMind(id="pm_2", user_mind_id="um_1", project_id="deal_2")

        await storage.save_project_mind(pm1)
        await storage.save_project_mind(pm2)

        projects = await storage.get_project_minds_for_user("user_1")
        assert len(projects) == 2
        project_ids = {p.project_id for p in projects}
        assert "deal_1" in project_ids
        assert "deal_2" in project_ids

    @pytest.mark.asyncio
    async def test_save_and_get_memory(self, storage):
        """Should save and retrieve ConversationMemory."""
        memory = ConversationMemory(
            id="mem_1",
            project_mind_id="pm_1",
        )
        memory.add_message("user", "Hello!")
        memory.add_message("assistant", "Hi there!")

        await storage.save_memory(memory)
        retrieved = await storage.get_memory("pm_1")

        assert retrieved is not None
        assert retrieved.id == "mem_1"
        messages = retrieved.get_recent_messages()
        assert len(messages) == 2

    @pytest.mark.asyncio
    async def test_save_and_get_nudge(self, storage):
        """Should save and retrieve Nudge."""
        # First create user and project
        user_mind = UserMind(id="um_1", user_id="user_1")
        await storage.save_user_mind(user_mind)

        project_mind = ProjectMind(id="pm_1", user_mind_id="um_1", project_id="deal_1")
        await storage.save_project_mind(project_mind)

        nudge = Nudge(
            id="nudge_1",
            project_mind_id="pm_1",
            nudge_type="comeback",
            title="Deal going cold?",
            message="No activity in 7 days",
            priority=5,
        )

        await storage.save_nudge(nudge)
        nudges = await storage.get_pending_nudges("user_1")

        assert len(nudges) == 1
        assert nudges[0].id == "nudge_1"
        assert nudges[0].title == "Deal going cold?"

    @pytest.mark.asyncio
    async def test_get_pending_nudges_filters_dismissed(self, storage):
        """Should not return dismissed nudges."""
        # First create user and project
        user_mind = UserMind(id="um_1", user_id="user_1")
        await storage.save_user_mind(user_mind)

        project_mind = ProjectMind(id="pm_1", user_mind_id="um_1", project_id="deal_1")
        await storage.save_project_mind(project_mind)

        nudge1 = Nudge(
            id="nudge_1",
            project_mind_id="pm_1",
            nudge_type="test",
            title="Active",
            message="msg",
            status="pending",
        )
        nudge2 = Nudge(
            id="nudge_2",
            project_mind_id="pm_1",
            nudge_type="test",
            title="Dismissed",
            message="msg",
            status="dismissed",
        )

        await storage.save_nudge(nudge1)
        await storage.save_nudge(nudge2)

        nudges = await storage.get_pending_nudges("user_1")
        assert len(nudges) == 1
        assert nudges[0].id == "nudge_1"

    @pytest.mark.asyncio
    async def test_context_and_progress_data_persisted(self, storage):
        """Should persist context_data and progress_data as JSON."""
        user_mind = UserMind(id="um_1", user_id="user_1")
        await storage.save_user_mind(user_mind)

        project_mind = ProjectMind(
            id="pm_1",
            user_mind_id="um_1",
            project_id="deal_1",
        )
        project_mind.set_context_field("deal_size", "enterprise")
        project_mind.set_progress_field("calls_made", 5)

        await storage.save_project_mind(project_mind)
        retrieved = await storage.get_project_mind("user_1", "deal_1")

        assert retrieved.get_context_field("deal_size") == "enterprise"
        assert retrieved.get_progress_field("calls_made") == 5

    @pytest.mark.asyncio
    async def test_patterns_persisted(self, storage):
        """Should persist patterns dict as JSON."""
        user_mind = UserMind(
            id="um_1",
            user_id="user_1",
            patterns={"outreach": "email-first", "response_time": "slow"},
        )

        await storage.save_user_mind(user_mind)
        retrieved = await storage.get_user_mind("user_1")

        assert retrieved.patterns == {"outreach": "email-first", "response_time": "slow"}


class TestSQLiteStorageInit:
    """Test SQLite storage initialization."""

    @pytest.mark.asyncio
    async def test_creates_tables_on_init(self):
        """Should create tables on initialize()."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Verify we can use it
            user_mind = UserMind(id="um_1", user_id="user_1")
            await storage.save_user_mind(user_mind)
            retrieved = await storage.get_user_mind("user_1")
            assert retrieved is not None

            await storage.close()
        finally:
            os.unlink(db_path)

    @pytest.mark.asyncio
    async def test_close_idempotent(self):
        """Should be safe to call close() multiple times."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Should not raise when called multiple times
            await storage.close()
            await storage.close()
        finally:
            os.unlink(db_path)
