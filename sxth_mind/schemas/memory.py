"""
Memory Schemas

Conversation memory and message history.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A single message in a conversation."""

    role: Literal["system", "user", "assistant", "tool"] = Field(
        ..., description="Message role"
    )
    content: str = Field(..., description="Message content")
    name: str | None = Field(default=None, description="Tool name if role=tool")
    tool_call_id: str | None = Field(
        default=None, description="Tool call ID if role=tool"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"extra": "allow"}


class ConversationMemory(BaseModel):
    """
    Conversation memory for a project.

    Stores recent conversation history and derived summaries.
    """

    id: str = Field(default="", description="Unique identifier")
    project_mind_id: str = Field(..., description="Reference to ProjectMind")

    # Recent messages (sliding window)
    messages: list[Message] = Field(
        default_factory=list,
        description="Recent conversation messages",
    )

    # Derived summary of older conversations
    summary: str | None = Field(
        default=None,
        description="Summary of conversation history beyond the recent window",
    )

    # Key topics/themes extracted from conversations
    topics: list[str] = Field(
        default_factory=list,
        description="Key topics discussed",
    )

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"extra": "allow"}

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content))  # type: ignore
        self.updated_at = datetime.utcnow()

    def get_recent_messages(self, limit: int = 10) -> list[Message]:
        """Get the most recent messages."""
        return self.messages[-limit:]

    def to_openai_messages(self, limit: int = 10) -> list[dict]:
        """Convert recent messages to OpenAI format."""
        return [
            {"role": m.role, "content": m.content}
            for m in self.get_recent_messages(limit)
        ]
