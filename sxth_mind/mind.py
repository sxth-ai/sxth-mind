"""
Mind - The Core Abstraction

The Mind is the central interface for sxth-mind. It coordinates:
- Adapter (domain-specific behavior)
- Provider (LLM calls)
- Storage (persistence)

And exposes a simple API: chat, get_state, get_nudges.
"""

from collections.abc import AsyncIterator
from uuid import uuid4

from sxth_mind.adapters.base import BaseAdapter
from sxth_mind.providers.base import BaseLLMProvider, Message
from sxth_mind.schemas import ConversationMemory, ProjectMind, UserMind
from sxth_mind.storage.base import BaseStorage
from sxth_mind.storage.memory import MemoryStorage


class Mind:
    """
    The Mind is the core abstraction for sxth-mind.

    It accumulates state, detects patterns, and adapts over time.

    Usage:
        from sxth_mind import Mind
        from sxth_mind.examples import SalesAdapter

        mind = Mind(adapter=SalesAdapter())

        # Chat (creates/updates cognitive state automatically)
        response = await mind.chat("user_123", "Following up with the enterprise lead")

        # Later...
        response = await mind.chat("user_123", "Following up with the enterprise lead again")
        # → Mind notices pattern and responds differently

    The Mind:
    - Creates UserMind/ProjectMind on first interaction
    - Updates state after each interaction
    - Builds context-aware prompts using the adapter
    - Persists everything via the storage backend
    """

    def __init__(
        self,
        adapter: BaseAdapter,
        provider: BaseLLMProvider | None = None,
        storage: BaseStorage | None = None,
    ):
        """
        Initialize a Mind.

        Args:
            adapter: Domain adapter (required) - defines identity, stages, nudges
            provider: LLM provider (optional) - defaults to OpenAI if available
            storage: Storage backend (optional) - defaults to in-memory
        """
        self.adapter = adapter
        self.storage = storage or MemoryStorage()
        self._provider = provider

    @property
    def provider(self) -> BaseLLMProvider:
        """Get the LLM provider, initializing if needed."""
        if self._provider is None:
            self._provider = self._get_default_provider()
        return self._provider

    def _get_default_provider(self) -> BaseLLMProvider:
        """Get default provider based on what's installed."""
        try:
            from sxth_mind.providers.openai import OpenAIProvider
            return OpenAIProvider()
        except ImportError:
            pass

        raise ImportError(
            "No LLM provider available. Install one with:\n"
            "  pip install sxth-mind[openai]     # OpenAI\n"
            "  pip install sxth-mind[agno]       # Agno\n"
            "Or pass a custom provider to Mind()"
        )

    # ═══════════════════════════════════════════════════════════════
    # Core API
    # ═══════════════════════════════════════════════════════════════

    async def chat(
        self,
        user_id: str,
        message: str,
        project_id: str | None = None,
    ) -> str:
        """
        Chat with the Mind.

        This is the primary interface. The Mind:
        1. Loads or creates UserMind and ProjectMind
        2. Builds context-aware prompt using the adapter
        3. Calls the LLM
        4. Updates state based on the interaction
        5. Returns the response

        Args:
            user_id: Your user's ID
            message: The user's message
            project_id: Optional project ID (defaults to "default")

        Returns:
            The assistant's response
        """
        project_id = project_id or "default"

        # Load or create minds
        user_mind = await self._get_or_create_user_mind(user_id)
        project_mind = await self._get_or_create_project_mind(user_mind, project_id)

        # Load conversation memory
        memory = await self._get_or_create_memory(project_mind)

        # Build messages with context
        messages = self._build_messages(user_mind, project_mind, memory, message)

        # Call LLM
        response = await self.provider.chat(messages)

        # Update state
        await self._update_after_interaction(
            user_mind, project_mind, memory, message, response.content
        )

        return response.content

    async def chat_stream(
        self,
        user_id: str,
        message: str,
        project_id: str | None = None,
    ) -> AsyncIterator[str]:
        """
        Stream a chat response.

        Same as chat(), but yields tokens as they're generated.

        Args:
            user_id: Your user's ID
            message: The user's message
            project_id: Optional project ID

        Yields:
            Response tokens
        """
        project_id = project_id or "default"

        # Load or create minds
        user_mind = await self._get_or_create_user_mind(user_id)
        project_mind = await self._get_or_create_project_mind(user_mind, project_id)

        # Load conversation memory
        memory = await self._get_or_create_memory(project_mind)

        # Build messages
        messages = self._build_messages(user_mind, project_mind, memory, message)

        # Stream response and collect full content
        full_response = ""
        async for token in self.provider.chat_stream(messages):
            full_response += token
            yield token

        # Update state after streaming completes
        await self._update_after_interaction(
            user_mind, project_mind, memory, message, full_response
        )

    # ═══════════════════════════════════════════════════════════════
    # State Introspection
    # ═══════════════════════════════════════════════════════════════

    async def get_state(self, user_id: str, project_id: str | None = None) -> dict:
        """
        Get the current cognitive state for a user.

        Returns a dict with user_mind and optionally project_mind.
        Useful for debugging and introspection.
        """
        user_mind = await self.storage.get_user_mind(user_id)
        if not user_mind:
            return {"user_mind": None, "project_mind": None}

        result = {"user_mind": user_mind.model_dump()}

        if project_id:
            project_mind = await self.storage.get_project_mind(user_id, project_id)
            result["project_mind"] = project_mind.model_dump() if project_mind else None

        return result

    async def explain_state(self, user_id: str, project_id: str | None = None) -> str:
        """
        Get a human-readable explanation of the user's state.

        Useful for debugging and understanding what the Mind knows.
        """
        state = await self.get_state(user_id, project_id)

        if not state["user_mind"]:
            return f"No state found for user {user_id}"

        um = state["user_mind"]
        lines = [
            f"User: {user_id}",
            f"Total interactions: {um['total_interactions']}",
            f"Trust score: {um['trust_score']:.2f}",
            f"Identity type: {um.get('identity_type', 'not set')}",
        ]

        if um.get("patterns"):
            lines.append(f"Patterns detected: {list(um['patterns'].keys())}")

        if state.get("project_mind"):
            pm = state["project_mind"]
            lines.extend([
                f"\nProject: {pm['project_id']}",
                f"Journey stage: {pm.get('journey_stage', 'not set')}",
                f"Interactions: {pm['interaction_count']}",
                f"Momentum: {pm['momentum_score']:.2f}",
            ])

        return "\n".join(lines)

    # ═══════════════════════════════════════════════════════════════
    # Nudges
    # ═══════════════════════════════════════════════════════════════

    async def get_pending_nudges(self, user_id: str) -> list:
        """Get pending nudges for a user."""
        return await self.storage.get_pending_nudges(user_id)

    # ═══════════════════════════════════════════════════════════════
    # Internal Methods
    # ═══════════════════════════════════════════════════════════════

    async def _get_or_create_user_mind(self, user_id: str) -> UserMind:
        """Load or create a UserMind."""
        user_mind = await self.storage.get_user_mind(user_id)
        if not user_mind:
            user_mind = UserMind(
                id=str(uuid4()),
                user_id=user_id,
            )
            await self.storage.save_user_mind(user_mind)
        return user_mind

    async def _get_or_create_project_mind(
        self, user_mind: UserMind, project_id: str
    ) -> ProjectMind:
        """Load or create a ProjectMind."""
        project_mind = await self.storage.get_project_mind(user_mind.user_id, project_id)
        if not project_mind:
            project_mind = ProjectMind(
                id=str(uuid4()),
                user_mind_id=user_mind.id,
                project_id=project_id,
            )
            # Detect initial journey stage
            project_mind.journey_stage = self.adapter.detect_journey_stage(project_mind)
            await self.storage.save_project_mind(project_mind)
        return project_mind

    async def _get_or_create_memory(self, project_mind: ProjectMind) -> ConversationMemory:
        """Load or create conversation memory."""
        memory = await self.storage.get_memory(project_mind.id)
        if not memory:
            memory = ConversationMemory(
                id=str(uuid4()),
                project_mind_id=project_mind.id,
            )
            await self.storage.save_memory(memory)
        return memory

    def _build_messages(
        self,
        user_mind: UserMind,
        project_mind: ProjectMind,
        memory: ConversationMemory,
        new_message: str,
    ) -> list[Message]:
        """Build the message list for the LLM."""
        # Get system prompt from adapter
        system_prompt = self.adapter.get_system_prompt(user_mind, project_mind)

        # Build context section
        context = self.adapter.get_context_for_prompt(user_mind, project_mind)
        context_str = self._format_context(context)

        if context_str:
            system_prompt += f"\n\n## User Context\n{context_str}"

        messages = [Message(role="system", content=system_prompt)]

        # Add conversation history
        for msg in memory.get_recent_messages(limit=10):
            messages.append(Message(role=msg.role, content=msg.content))

        # Add new message
        messages.append(Message(role="user", content=new_message))

        return messages

    def _format_context(self, context: dict) -> str:
        """Format context dict as readable text for the prompt."""
        if not context:
            return ""

        lines = []
        for key, value in context.items():
            if value is not None and value != {} and value != []:
                # Format key nicely
                label = key.replace("_", " ").title()
                lines.append(f"- {label}: {value}")

        return "\n".join(lines)

    async def _update_after_interaction(
        self,
        user_mind: UserMind,
        project_mind: ProjectMind,
        memory: ConversationMemory,
        message: str,
        response: str,
    ) -> None:
        """Update state after an interaction."""
        # Add to memory
        memory.add_message("user", message)
        memory.add_message("assistant", response)

        # Let adapter update state
        self.adapter.update_after_interaction(user_mind, project_mind, message, response)

        # Persist
        await self.storage.save_user_mind(user_mind)
        await self.storage.save_project_mind(project_mind)
        await self.storage.save_memory(memory)
