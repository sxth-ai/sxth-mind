"""
EvidenceSource Interface

A read-mostly port over the raw substrate sxth-mind does NOT own. Back it with
the app's own database, a memory vendor (Mem0, Zep), or the bundled
LocalEvidenceSource for dev/demo use.

sxth-mind reads evidence to (a) assemble generation context and (b) feed belief
extraction/consolidation. It is the system of record for BELIEFS
(UserMind/ProjectMind), not for the raw bytes — "own the beliefs, rent the
bytes." Implementations therefore must support reading; writing back
(``append``) is optional, since many apps already log their own events.
"""

from abc import ABC, abstractmethod

from sxth_mind.schemas.evidence import Event


class EvidenceSource(ABC):
    """Abstract source of raw evidence (messages, actions, signals)."""

    @abstractmethod
    async def recent(
        self, user_id: str, project_id: str | None = None, limit: int = 10
    ) -> list[Event]:
        """Return the most recent events for a user (optionally project-scoped),
        oldest-first, suitable for building conversation context."""
        pass

    @abstractmethod
    async def search(
        self,
        user_id: str,
        query: str,
        project_id: str | None = None,
        limit: int = 10,
    ) -> list[Event]:
        """Return events relevant to ``query`` (most relevant first). The bundled
        local source does naive substring matching; production sources back this
        with semantic/vector search."""
        pass

    async def append(self, event: Event) -> None:
        """Append an event to the substrate.

        Optional: the default is a no-op, because many integrations point
        sxth-mind at a substrate the app already writes to. Override when you
        want sxth-mind to capture raw turns itself (e.g. the local source).
        """
        return None
