"""
Evidence Schema

An Event is one piece of raw evidence — a message, action, or signal — that
sxth-mind READS to assemble context and to derive beliefs. Events are the
"rented" substrate: sxth-mind is the system of record for beliefs
(UserMind/ProjectMind), not for the raw bytes. They live behind an
EvidenceSource, which can be backed by the app's own store, a memory vendor
(Mem0/Zep), or the bundled LocalEvidenceSource.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from sxth_mind._time import utcnow


class Event(BaseModel):
    """A single piece of raw evidence about a user."""

    id: str = Field(default="", description="Unique identifier")
    user_id: str = Field(..., description="External user ID from your system")
    project_id: str | None = Field(
        default=None, description="Optional project/thread scope"
    )

    kind: str = Field(
        default="message",
        description="Evidence kind: message | action | signal | ...",
    )
    role: str | None = Field(
        default=None,
        description="For messages: user | assistant | system | tool",
    )
    content: str = Field(..., description="The evidence content")

    timestamp: datetime = Field(default_factory=utcnow)
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary source-specific metadata"
    )

    model_config = {"extra": "allow"}
