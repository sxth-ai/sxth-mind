"""Tests for the EvidenceSource layer (the rented raw substrate)."""

import pytest

from sxth_mind.evidence import LocalEvidenceSource
from sxth_mind.schemas import Event


class TestLocalEvidenceSource:
    @pytest.fixture
    def source(self):
        return LocalEvidenceSource()

    @pytest.mark.asyncio
    async def test_append_and_recent(self, source):
        for i in range(15):
            await source.append(
                Event(user_id="u1", project_id="p1", role="user", content=f"msg {i}")
            )

        recent = await source.recent("u1", "p1", limit=5)
        assert len(recent) == 5
        assert recent[0].content == "msg 10"
        assert recent[-1].content == "msg 14"

    @pytest.mark.asyncio
    async def test_append_assigns_id(self, source):
        await source.append(Event(user_id="u1", project_id="p1", content="hi"))
        events = await source.recent("u1", "p1")
        assert events[0].id  # non-empty

    @pytest.mark.asyncio
    async def test_scoping_by_user_and_project(self, source):
        await source.append(Event(user_id="u1", project_id="p1", content="a"))
        await source.append(Event(user_id="u1", project_id="p2", content="b"))
        await source.append(Event(user_id="u2", project_id="p1", content="c"))

        assert len(await source.recent("u1", "p1")) == 1
        assert len(await source.recent("u1", "p2")) == 1
        assert len(await source.recent("u2", "p1")) == 1

    @pytest.mark.asyncio
    async def test_search_substring(self, source):
        await source.append(Event(user_id="u1", project_id="p1", content="I love Python"))
        await source.append(Event(user_id="u1", project_id="p1", content="and coffee"))

        hits = await source.search("u1", "python", project_id="p1")
        assert len(hits) == 1
        assert "Python" in hits[0].content

    @pytest.mark.asyncio
    async def test_stored_events_are_isolated(self, source):
        event = Event(user_id="u1", project_id="p1", content="original")
        await source.append(event)

        event.content = "mutated"  # mutate caller's copy
        stored = (await source.recent("u1", "p1"))[0]
        assert stored.content == "original"

    @pytest.mark.asyncio
    async def test_base_append_is_optional_noop(self):
        # A read-only source (app owns writes) only needs recent/search.
        from sxth_mind.evidence.base import EvidenceSource

        class ReadOnly(EvidenceSource):
            async def recent(self, user_id, project_id=None, limit=10):
                return []

            async def search(self, user_id, query, project_id=None, limit=10):
                return []

        src = ReadOnly()
        # Default append is a no-op and must not raise.
        await src.append(Event(user_id="u1", content="x"))
        assert await src.recent("u1") == []
