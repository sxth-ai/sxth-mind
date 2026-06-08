"""
Memory Storage

In-memory storage implementation. Good for testing and demos.
Data is lost when the process exits.
"""

from uuid import uuid4

from sxth_mind.schemas import Nudge, ProjectMind, UserMind
from sxth_mind.storage.base import BaseStorage


class MemoryStorage(BaseStorage):
    """
    In-memory storage implementation.

    Stores all data in Python dictionaries. Fast and simple,
    but data is lost when the process exits.

    Usage:
        storage = MemoryStorage()
        mind = Mind(adapter=MyAdapter(), storage=storage)
    """

    def __init__(self) -> None:
        self._user_minds: dict[str, UserMind] = {}
        self._project_minds: dict[str, ProjectMind] = {}  # key: f"{user_id}:{project_id}"
        self._nudges: dict[str, list[Nudge]] = {}  # key: user_id

    def _project_key(self, user_id: str, project_id: str) -> str:
        return f"{user_id}:{project_id}"

    # ═══════════════════════════════════════════════════════════════
    # UserMind Operations
    # ═══════════════════════════════════════════════════════════════

    async def get_user_mind(self, user_id: str) -> UserMind | None:
        stored = self._user_minds.get(user_id)
        return stored.model_copy(deep=True) if stored else None

    async def save_user_mind(self, user_mind: UserMind) -> None:
        if not user_mind.id:
            user_mind.id = str(uuid4())
        # Store an isolated snapshot so later mutation of the caller's object
        # doesn't silently change persisted state (matches SQLite semantics).
        self._user_minds[user_mind.user_id] = user_mind.model_copy(deep=True)

    async def delete_user_mind(self, user_id: str) -> None:
        # Delete user mind
        if user_id in self._user_minds:
            del self._user_minds[user_id]

        # Delete all project minds for this user
        keys_to_delete = [k for k in self._project_minds if k.startswith(f"{user_id}:")]
        for key in keys_to_delete:
            del self._project_minds[key]

        # Delete nudges
        if user_id in self._nudges:
            del self._nudges[user_id]

    # ═══════════════════════════════════════════════════════════════
    # ProjectMind Operations
    # ═══════════════════════════════════════════════════════════════

    async def get_project_mind(
        self, user_id: str, project_id: str
    ) -> ProjectMind | None:
        key = self._project_key(user_id, project_id)
        stored = self._project_minds.get(key)
        return stored.model_copy(deep=True) if stored else None

    async def save_project_mind(self, project_mind: ProjectMind) -> None:
        if not project_mind.id:
            project_mind.id = str(uuid4())

        # Get user_id from the user_mind_id
        user_id = None
        for uid, um in self._user_minds.items():
            if um.id == project_mind.user_mind_id:
                user_id = uid
                break

        if user_id:
            key = self._project_key(user_id, project_mind.project_id)
            self._project_minds[key] = project_mind.model_copy(deep=True)

    async def get_project_minds_for_user(self, user_id: str) -> list[ProjectMind]:
        return [
            pm.model_copy(deep=True)
            for key, pm in self._project_minds.items()
            if key.startswith(f"{user_id}:")
        ]

    async def delete_project_mind(self, user_id: str, project_id: str) -> None:
        key = self._project_key(user_id, project_id)
        if key in self._project_minds:
            del self._project_minds[key]

    # ═══════════════════════════════════════════════════════════════
    # Nudge Operations
    # ═══════════════════════════════════════════════════════════════

    async def get_pending_nudges(self, user_id: str) -> list[Nudge]:
        nudges = self._nudges.get(user_id, [])
        return [n.model_copy(deep=True) for n in nudges if n.status == "pending"]

    async def save_nudge(self, nudge: Nudge) -> None:
        if not nudge.id:
            nudge.id = str(uuid4())

        # Find user_id from project_mind
        user_id = None
        for key, pm in self._project_minds.items():
            if pm.id == nudge.project_mind_id:
                user_id = key.split(":")[0]
                break

        if user_id:
            stored = nudge.model_copy(deep=True)
            if user_id not in self._nudges:
                self._nudges[user_id] = []
            # Update existing or append
            for i, n in enumerate(self._nudges[user_id]):
                if n.id == nudge.id:
                    self._nudges[user_id][i] = stored
                    return
            self._nudges[user_id].append(stored)

    async def update_nudge_status(self, nudge_id: str, status: str) -> bool:
        for nudges in self._nudges.values():
            for nudge in nudges:
                if nudge.id == nudge_id:
                    nudge.set_status(status)
                    return True
        return False

    # ═══════════════════════════════════════════════════════════════
    # Debug/Testing Helpers
    # ═══════════════════════════════════════════════════════════════

    def clear(self) -> None:
        """Clear all stored data."""
        self._user_minds.clear()
        self._project_minds.clear()
        self._nudges.clear()

    def stats(self) -> dict[str, int]:
        """Get storage stats."""
        return {
            "user_minds": len(self._user_minds),
            "project_minds": len(self._project_minds),
            "nudges": sum(len(n) for n in self._nudges.values()),
        }
