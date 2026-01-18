"""Tests for the Mind class."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.sales import SalesAdapter
from sxth_mind import Mind
from sxth_mind.providers.base import BaseLLMProvider, LLMResponse
from sxth_mind.storage import MemoryStorage


class MockProvider(BaseLLMProvider):
    """Mock LLM provider for testing."""

    def __init__(self, response: str = "Mock response"):
        self.response = response
        self.calls = []

    @property
    def default_model(self) -> str:
        return "mock-model"

    async def chat(self, messages, model=None, tools=None, temperature=0.7, max_tokens=None):
        self.calls.append({"messages": messages, "model": model})
        return LLMResponse(content=self.response, model="mock-model")

    async def chat_stream(self, messages, model=None, tools=None, temperature=0.7, max_tokens=None):
        self.calls.append({"messages": messages, "model": model, "stream": True})
        for word in self.response.split():
            yield word + " "


class TestMindInit:
    """Test Mind initialization."""

    def test_init_with_adapter_only(self):
        """Mind should work with just an adapter."""
        mind = Mind(adapter=SalesAdapter())
        assert mind.adapter is not None
        assert isinstance(mind.storage, MemoryStorage)
        assert mind._provider is None

    def test_init_with_all_components(self):
        """Mind should accept all components."""
        adapter = SalesAdapter()
        storage = MemoryStorage()
        provider = MockProvider()

        mind = Mind(adapter=adapter, storage=storage, provider=provider)

        assert mind.adapter is adapter
        assert mind.storage is storage
        assert mind._provider is provider

    def test_no_provider_set_initially(self):
        """Mind should have no provider set initially."""
        mind = Mind(adapter=SalesAdapter())
        # Provider is lazy-loaded, so _provider is None initially
        assert mind._provider is None


class TestMindChat:
    """Test Mind.chat()."""

    @pytest.fixture
    def mind(self):
        """Create a Mind with mock provider."""
        return Mind(
            adapter=SalesAdapter(),
            storage=MemoryStorage(),
            provider=MockProvider("Hello from the assistant!"),
        )

    @pytest.mark.asyncio
    async def test_chat_returns_response(self, mind):
        """chat() should return the LLM response."""
        response = await mind.chat("user_1", "Hello!")
        assert response == "Hello from the assistant!"

    @pytest.mark.asyncio
    async def test_chat_creates_user_mind(self, mind):
        """chat() should create UserMind for new users."""
        await mind.chat("user_1", "Hello!")

        user_mind = await mind.storage.get_user_mind("user_1")
        assert user_mind is not None
        assert user_mind.user_id == "user_1"

    @pytest.mark.asyncio
    async def test_chat_creates_project_mind(self, mind):
        """chat() should create ProjectMind for new projects."""
        await mind.chat("user_1", "Hello!")

        user_mind = await mind.storage.get_user_mind("user_1")
        project_mind = await mind.storage.get_project_mind("user_1", "default")

        assert project_mind is not None
        assert project_mind.project_id == "default"
        assert project_mind.user_mind_id == user_mind.id

    @pytest.mark.asyncio
    async def test_chat_with_custom_project_id(self, mind):
        """chat() should use custom project_id."""
        await mind.chat("user_1", "Hello!", project_id="my_project")

        project_mind = await mind.storage.get_project_mind("user_1", "my_project")
        assert project_mind is not None
        assert project_mind.project_id == "my_project"

    @pytest.mark.asyncio
    async def test_chat_updates_interaction_count(self, mind):
        """chat() should increment interaction counts."""
        await mind.chat("user_1", "Hello!")
        await mind.chat("user_1", "How are you?")

        user_mind = await mind.storage.get_user_mind("user_1")
        project_mind = await mind.storage.get_project_mind("user_1", "default")

        assert user_mind.total_interactions == 2
        assert project_mind.interaction_count == 2

    @pytest.mark.asyncio
    async def test_chat_builds_messages_with_system_prompt(self, mind):
        """chat() should include system prompt in messages."""
        provider = mind._provider
        await mind.chat("user_1", "Hello!")

        # Check that system message was included
        messages = provider.calls[0]["messages"]
        assert messages[0].role == "system"
        assert "Sales" in messages[0].content or "pipeline" in messages[0].content.lower()

    @pytest.mark.asyncio
    async def test_chat_includes_user_message(self, mind):
        """chat() should include the user's message."""
        provider = mind._provider
        await mind.chat("user_1", "Working on a deal with Acme")

        messages = provider.calls[0]["messages"]
        user_messages = [m for m in messages if m.role == "user"]
        assert len(user_messages) == 1
        assert "Acme" in user_messages[0].content

    @pytest.mark.asyncio
    async def test_chat_saves_to_memory(self, mind):
        """chat() should save messages to conversation memory."""
        await mind.chat("user_1", "Hello!")

        project_mind = await mind.storage.get_project_mind("user_1", "default")
        memory = await mind.storage.get_memory(project_mind.id)

        assert memory is not None
        messages = memory.get_recent_messages()
        assert len(messages) == 2  # user + assistant
        assert messages[0].role == "user"
        assert messages[0].content == "Hello!"
        assert messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_chat_includes_conversation_history(self, mind):
        """chat() should include previous messages in context."""
        provider = mind._provider
        await mind.chat("user_1", "First message")
        await mind.chat("user_1", "Second message")

        # Check second call includes history
        messages = provider.calls[1]["messages"]
        user_messages = [m.content for m in messages if m.role == "user"]

        assert "First message" in user_messages
        assert "Second message" in user_messages


class TestMindChatStream:
    """Test Mind.chat_stream()."""

    @pytest.fixture
    def mind(self):
        return Mind(
            adapter=SalesAdapter(),
            storage=MemoryStorage(),
            provider=MockProvider("Hello from streaming!"),
        )

    @pytest.mark.asyncio
    async def test_chat_stream_yields_tokens(self, mind):
        """chat_stream() should yield response tokens."""
        tokens = []
        async for token in mind.chat_stream("user_1", "Hello!"):
            tokens.append(token)

        assert len(tokens) > 0
        full_response = "".join(tokens)
        assert "Hello" in full_response

    @pytest.mark.asyncio
    async def test_chat_stream_updates_state(self, mind):
        """chat_stream() should update state after completion."""
        async for _ in mind.chat_stream("user_1", "Hello!"):
            pass

        user_mind = await mind.storage.get_user_mind("user_1")
        assert user_mind.total_interactions == 1


class TestMindGetState:
    """Test Mind.get_state()."""

    @pytest.fixture
    def mind(self):
        return Mind(
            adapter=SalesAdapter(),
            storage=MemoryStorage(),
            provider=MockProvider(),
        )

    @pytest.mark.asyncio
    async def test_get_state_returns_none_for_unknown_user(self, mind):
        """get_state() should return None for unknown users."""
        state = await mind.get_state("unknown_user")
        assert state["user_mind"] is None

    @pytest.mark.asyncio
    async def test_get_state_returns_user_mind(self, mind):
        """get_state() should return user mind data."""
        await mind.chat("user_1", "Hello!")

        state = await mind.get_state("user_1")
        assert state["user_mind"] is not None
        assert state["user_mind"]["user_id"] == "user_1"

    @pytest.mark.asyncio
    async def test_get_state_with_project_id(self, mind):
        """get_state() should return project mind when specified."""
        await mind.chat("user_1", "Hello!", project_id="proj_1")

        state = await mind.get_state("user_1", project_id="proj_1")
        assert state["project_mind"] is not None
        assert state["project_mind"]["project_id"] == "proj_1"


class TestMindExplainState:
    """Test Mind.explain_state()."""

    @pytest.fixture
    def mind(self):
        return Mind(
            adapter=SalesAdapter(),
            storage=MemoryStorage(),
            provider=MockProvider(),
        )

    @pytest.mark.asyncio
    async def test_explain_state_unknown_user(self, mind):
        """explain_state() should handle unknown users."""
        explanation = await mind.explain_state("unknown_user")
        assert "No state found" in explanation

    @pytest.mark.asyncio
    async def test_explain_state_returns_readable_summary(self, mind):
        """explain_state() should return human-readable summary."""
        await mind.chat("user_1", "Hello!")
        await mind.chat("user_1", "Working on a deal")

        explanation = await mind.explain_state("user_1")

        assert "user_1" in explanation
        assert "interactions" in explanation.lower()
        assert "2" in explanation  # total interactions

    @pytest.mark.asyncio
    async def test_explain_state_includes_project_info(self, mind):
        """explain_state() should include project info."""
        await mind.chat("user_1", "Hello!", project_id="deal_acme")

        explanation = await mind.explain_state("user_1", project_id="deal_acme")

        assert "deal_acme" in explanation


class TestMindGetPendingNudges:
    """Test Mind.get_pending_nudges()."""

    @pytest.fixture
    def mind(self):
        return Mind(
            adapter=SalesAdapter(),
            storage=MemoryStorage(),
            provider=MockProvider(),
        )

    @pytest.mark.asyncio
    async def test_get_pending_nudges_empty(self, mind):
        """get_pending_nudges() should return empty list for new users."""
        nudges = await mind.get_pending_nudges("user_1")
        assert nudges == []


class TestMindBuildMessages:
    """Test Mind._build_messages()."""

    @pytest.fixture
    def mind(self):
        return Mind(
            adapter=SalesAdapter(),
            storage=MemoryStorage(),
            provider=MockProvider(),
        )

    @pytest.mark.asyncio
    async def test_format_context(self, mind):
        """_format_context() should format dict as readable text."""
        context = {
            "identity_type": "hunter",
            "total_interactions": 10,
            "empty_dict": {},
            "none_value": None,
        }

        formatted = mind._format_context(context)

        assert "Identity Type: hunter" in formatted
        assert "Total Interactions: 10" in formatted
        assert "empty_dict" not in formatted.lower()
        assert "none" not in formatted.lower()

    @pytest.mark.asyncio
    async def test_format_context_empty(self, mind):
        """_format_context() should handle empty context."""
        assert mind._format_context({}) == ""
        assert mind._format_context(None) == ""
