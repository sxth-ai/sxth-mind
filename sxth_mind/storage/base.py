"""
Base Storage Interface

Abstract interface for persistence. Implement this to store minds
in your preferred backend (memory, SQLite, Postgres, etc.)
"""

from abc import ABC, abstractmethod

from sxth_mind.schemas import ConversationMemory, Nudge, ProjectMind, UserMind


class BaseStorage(ABC):
    """
    Abstract interface for persistence.

    Implement this to store minds in your preferred backend.

    Example implementations:
    - MemoryStorage: In-memory (default, for testing/demos)
    - SQLiteStorage: SQLite database
    - PostgresStorage: PostgreSQL database
    """

    # ═══════════════════════════════════════════════════════════════
    # UserMind Operations
    # ═══════════════════════════════════════════════════════════════

    @abstractmethod
    async def get_user_mind(self, user_id: str) -> UserMind | None:
        """Get a UserMind by user_id."""
        pass

    @abstractmethod
    async def save_user_mind(self, user_mind: UserMind) -> None:
        """Save a UserMind."""
        pass

    @abstractmethod
    async def delete_user_mind(self, user_id: str) -> None:
        """Delete a UserMind and all related data."""
        pass

    # ═══════════════════════════════════════════════════════════════
    # ProjectMind Operations
    # ═══════════════════════════════════════════════════════════════

    @abstractmethod
    async def get_project_mind(
        self, user_id: str, project_id: str
    ) -> ProjectMind | None:
        """Get a ProjectMind by user_id and project_id."""
        pass

    @abstractmethod
    async def save_project_mind(self, project_mind: ProjectMind) -> None:
        """Save a ProjectMind."""
        pass

    @abstractmethod
    async def get_project_minds_for_user(self, user_id: str) -> list[ProjectMind]:
        """Get all ProjectMinds for a user."""
        pass

    @abstractmethod
    async def delete_project_mind(self, user_id: str, project_id: str) -> None:
        """Delete a ProjectMind."""
        pass

    # ═══════════════════════════════════════════════════════════════
    # ConversationMemory Operations
    # ═══════════════════════════════════════════════════════════════

    @abstractmethod
    async def get_memory(self, project_mind_id: str) -> ConversationMemory | None:
        """Get conversation memory for a project."""
        pass

    @abstractmethod
    async def save_memory(self, memory: ConversationMemory) -> None:
        """Save conversation memory."""
        pass

    # ═══════════════════════════════════════════════════════════════
    # Nudge Operations
    # ═══════════════════════════════════════════════════════════════

    @abstractmethod
    async def get_pending_nudges(self, user_id: str) -> list[Nudge]:
        """Get pending nudges for a user."""
        pass

    @abstractmethod
    async def save_nudge(self, nudge: Nudge) -> None:
        """Save a nudge."""
        pass

    # ═══════════════════════════════════════════════════════════════
    # Lifecycle
    # ═══════════════════════════════════════════════════════════════

    async def initialize(self) -> None:
        """Initialize storage (create tables, etc.). Override if needed."""
        pass

    async def close(self) -> None:
        """Close storage connections. Override if needed."""
        pass
