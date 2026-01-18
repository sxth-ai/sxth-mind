"""
OpenAI Provider

Direct OpenAI API implementation of BaseLLMProvider.
"""

from collections.abc import AsyncIterator
from typing import Any

from sxth_mind.providers.base import BaseLLMProvider, LLMResponse, Message, ToolCall


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI API provider.

    Requires: pip install sxth-mind[openai]

    Usage:
        provider = OpenAIProvider(api_key="sk-...")
        response = await provider.chat([Message(role="user", content="Hello")])
    """

    def __init__(
        self,
        api_key: str | None = None,
        organization: str | None = None,
        base_url: str | None = None,
        default_model: str = "gpt-4o-mini",
    ):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            organization: OpenAI organization ID
            base_url: Custom base URL (for Azure, proxies, etc.)
            default_model: Default model to use
        """
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with:\n"
                "  pip install sxth-mind[openai]"
            )

        self._client = AsyncOpenAI(
            api_key=api_key,
            organization=organization,
            base_url=base_url,
        )
        self._default_model = default_model

    @property
    def default_model(self) -> str:
        return self._default_model

    async def chat(
        self,
        messages: list[Message],
        model: str | None = None,
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Send messages and get a response."""
        kwargs: dict[str, Any] = {
            "model": model or self._default_model,
            "messages": self.format_messages(messages),
            "temperature": temperature,
        }

        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        if tools:
            kwargs["tools"] = tools

        response = await self._client.chat.completions.create(**kwargs)
        choice = response.choices[0]

        # Parse tool calls if present
        tool_calls = []
        if choice.message.tool_calls:
            import json
            for tc in choice.message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                    )
                )

        return LLMResponse(
            content=choice.message.content or "",
            tool_calls=tool_calls,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            model=response.model,
            finish_reason=choice.finish_reason,
        )

    async def chat_stream(
        self,
        messages: list[Message],
        model: str | None = None,
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """Stream a response token by token."""
        kwargs: dict[str, Any] = {
            "model": model or self._default_model,
            "messages": self.format_messages(messages),
            "temperature": temperature,
            "stream": True,
        }

        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        if tools:
            kwargs["tools"] = tools

        stream = await self._client.chat.completions.create(**kwargs)

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
