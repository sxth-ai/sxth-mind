"""
Base LLM Provider Interface

Abstract interface for LLM providers. Implement this to use any LLM
framework with sxth-mind (Agno, LangChain, direct OpenAI, etc.)
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A message in a conversation."""

    role: str = Field(..., description="Message role: system, user, assistant, tool")
    content: str = Field(..., description="Message content")
    name: str | None = Field(default=None, description="Tool name if role=tool")
    tool_call_id: str | None = Field(default=None, description="Tool call ID if role=tool")


class ToolCall(BaseModel):
    """A tool call requested by the LLM."""

    id: str = Field(..., description="Unique tool call ID")
    name: str = Field(..., description="Tool name")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Tool arguments")


class LLMResponse(BaseModel):
    """Response from an LLM."""

    content: str = Field(default="", description="Response content")
    tool_calls: list[ToolCall] = Field(default_factory=list, description="Tool calls")
    usage: dict[str, int] = Field(
        default_factory=dict, description="Token usage stats"
    )
    model: str | None = Field(default=None, description="Model used")
    finish_reason: str | None = Field(default=None, description="Why generation stopped")


class BaseLLMProvider(ABC):
    """
    Abstract interface for LLM providers.

    Implement this to use any LLM framework with sxth-mind.

    Example implementations:
    - OpenAIProvider: Direct OpenAI API calls
    - AgnoProvider: Uses Agno framework
    - LangChainProvider: Uses LangChain
    """

    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        model: str | None = None,
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """
        Send messages and get a response.

        Args:
            messages: Conversation messages
            model: Model to use (provider-specific default if None)
            tools: Tool definitions in OpenAI format
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            LLMResponse with content and optional tool calls
        """
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[Message],
        model: str | None = None,
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """
        Stream a response token by token.

        Args:
            messages: Conversation messages
            model: Model to use
            tools: Tool definitions
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Yields:
            Response tokens as they're generated
        """
        pass

    @property
    def default_model(self) -> str:
        """Default model for this provider."""
        return "gpt-4o-mini"

    def format_messages(self, messages: list[Message]) -> list[dict]:
        """Convert Message objects to provider format."""
        return [
            {"role": m.role, "content": m.content}
            for m in messages
        ]
