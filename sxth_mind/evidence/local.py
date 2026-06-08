"""
LocalEvidenceSource

In-memory, dependency-free EvidenceSource for development and demos. Keeps raw
events in a dict keyed by (user_id, project_id). Search is naive substring
matching — swap in a Mem0/Zep/app-DB source for production.
"""

from uuid import uuid4

from sxth_mind.evidence.base import EvidenceSource
from sxth_mind.schemas.evidence import Event


class LocalEvidenceSource(EvidenceSource):
    """Process-local evidence store. Data is lost when the process exits."""

    def __init__(self) -> None:
        self._events: dict[tuple[str, str | None], list[Event]] = {}

    async def recent(
        self, user_id: str, project_id: str | None = None, limit: int = 10
    ) -> list[Event]:
        events = self._events.get((user_id, project_id), [])
        return [e.model_copy(deep=True) for e in events[-limit:]]

    async def search(
        self,
        user_id: str,
        query: str,
        project_id: str | None = None,
        limit: int = 10,
    ) -> list[Event]:
        q = query.lower()
        hits: list[Event] = []
        for (uid, pid), events in self._events.items():
            if uid != user_id:
                continue
            if project_id is not None and pid != project_id:
                continue
            hits.extend(e for e in events if q in e.content.lower())
        hits.sort(key=lambda e: e.timestamp, reverse=True)
        return [e.model_copy(deep=True) for e in hits[:limit]]

    async def append(self, event: Event) -> None:
        if not event.id:
            event.id = str(uuid4())
        key = (event.user_id, event.project_id)
        self._events.setdefault(key, []).append(event.model_copy(deep=True))
