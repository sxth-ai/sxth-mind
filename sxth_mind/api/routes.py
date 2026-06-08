"""
API Routes

HTTP endpoints for sxth-mind.
"""

from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from sxth_mind.api.app import get_mind
from sxth_mind.mind import Mind

router = APIRouter()


# ═══════════════════════════════════════════════════════════════
# Request/Response Models
# ═══════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    """Chat request body."""
    user_id: str = Field(..., description="User identifier")
    message: str = Field(..., description="User message")
    project_id: str | None = Field(default=None, description="Optional project ID")
    stream: bool = Field(default=False, description="Stream response via SSE")


class ChatResponse(BaseModel):
    """Chat response body."""
    response: str = Field(..., description="Assistant response")
    user_id: str = Field(..., description="User identifier")
    project_id: str = Field(..., description="Project identifier")


class StateResponse(BaseModel):
    """State response body."""
    user_id: str
    user_mind: dict[str, Any] | None
    project_mind: dict[str, Any] | None = None


class ExplainResponse(BaseModel):
    """Explain response body."""
    user_id: str
    explanation: str


class NudgeResponse(BaseModel):
    """Nudge response body."""
    id: str
    nudge_type: str
    title: str
    message: str
    priority: int
    status: str


class NudgeActionResponse(BaseModel):
    """Response for a nudge status change."""
    status: str
    nudge_id: str


def _nudge_response(n: Any) -> NudgeResponse:
    return NudgeResponse(
        id=n.id,
        nudge_type=n.nudge_type,
        title=n.title,
        message=n.message,
        priority=n.priority,
        status=n.status,
    )


# ═══════════════════════════════════════════════════════════════
# Health Check
# ═══════════════════════════════════════════════════════════════

@router.get("/health")
async def health_check(mind: Mind = Depends(get_mind)) -> dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "adapter": mind.adapter.name,
        "storage": type(mind.storage).__name__,
    }


# ═══════════════════════════════════════════════════════════════
# Chat Endpoints
# ═══════════════════════════════════════════════════════════════

async def _stream_chat(mind: Mind, request: ChatRequest) -> AsyncIterator[str]:
    """Generate an SSE stream for a chat response."""
    async for token in mind.chat_stream(
        user_id=request.user_id,
        message=request.message,
        project_id=request.project_id,
    ):
        yield f"data: {token}\n\n"

    yield "data: [DONE]\n\n"


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, mind: Mind = Depends(get_mind)
) -> ChatResponse | StreamingResponse:
    """
    Send a message and get a response.

    The Mind automatically:
    - Creates/loads user and project state
    - Builds context-aware prompts
    - Updates state after the interaction
    """
    if request.stream:
        return StreamingResponse(
            _stream_chat(mind, request),
            media_type="text/event-stream",
        )

    response = await mind.chat(
        user_id=request.user_id,
        message=request.message,
        project_id=request.project_id,
    )

    return ChatResponse(
        response=response,
        user_id=request.user_id,
        project_id=request.project_id or "default",
    )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest, mind: Mind = Depends(get_mind)
) -> StreamingResponse:
    """
    Stream a chat response via Server-Sent Events.

    Each event contains a token from the response.
    Final event contains [DONE].
    """
    return StreamingResponse(
        _stream_chat(mind, request),
        media_type="text/event-stream",
    )


# ═══════════════════════════════════════════════════════════════
# State Endpoints
# ═══════════════════════════════════════════════════════════════

@router.get("/state/{user_id}", response_model=StateResponse)
async def get_state(
    user_id: str, project_id: str | None = None, mind: Mind = Depends(get_mind)
) -> StateResponse:
    """
    Get the cognitive state for a user.

    Returns UserMind and optionally ProjectMind data.
    """
    state = await mind.get_state(user_id, project_id)

    return StateResponse(
        user_id=user_id,
        user_mind=state.get("user_mind"),
        project_mind=state.get("project_mind"),
    )


@router.get("/explain/{user_id}", response_model=ExplainResponse)
async def explain_state(
    user_id: str, project_id: str | None = None, mind: Mind = Depends(get_mind)
) -> ExplainResponse:
    """
    Get a human-readable explanation of the user's state.

    Useful for debugging and understanding what the Mind knows.
    """
    explanation = await mind.explain_state(user_id, project_id)

    return ExplainResponse(
        user_id=user_id,
        explanation=explanation,
    )


# ═══════════════════════════════════════════════════════════════
# Nudge Endpoints
# ═══════════════════════════════════════════════════════════════

@router.get("/nudges/{user_id}", response_model=list[NudgeResponse])
async def get_nudges(
    user_id: str, mind: Mind = Depends(get_mind)
) -> list[NudgeResponse]:
    """
    Get pending nudges for a user.

    Nudges are proactive suggestions generated based on state.
    """
    nudges = await mind.get_pending_nudges(user_id)
    return [_nudge_response(n) for n in nudges]


@router.post("/nudges/{user_id}/generate", response_model=list[NudgeResponse])
async def generate_nudges(
    user_id: str, project_id: str | None = None, mind: Mind = Depends(get_mind)
) -> list[NudgeResponse]:
    """
    Generate new nudges for a user based on current state.

    This checks all nudge rules and creates any applicable nudges.
    """
    nudges = await mind.check_nudges(user_id, project_id)
    return [_nudge_response(n) for n in nudges]


@router.post("/nudges/{nudge_id}/dismiss", response_model=NudgeActionResponse)
async def dismiss_nudge(
    nudge_id: str, mind: Mind = Depends(get_mind)
) -> NudgeActionResponse:
    """Dismiss a nudge so it no longer appears as pending."""
    updated = await mind.dismiss_nudge(nudge_id)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Nudge {nudge_id} not found")
    return NudgeActionResponse(status="dismissed", nudge_id=nudge_id)


@router.post("/nudges/{nudge_id}/act", response_model=NudgeActionResponse)
async def act_on_nudge(
    nudge_id: str, mind: Mind = Depends(get_mind)
) -> NudgeActionResponse:
    """Mark a nudge as acted upon (e.g. the user took the suggested action)."""
    updated = await mind.act_on_nudge(nudge_id)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Nudge {nudge_id} not found")
    return NudgeActionResponse(status="acted", nudge_id=nudge_id)
