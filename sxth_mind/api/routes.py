"""
API Routes

HTTP endpoints for sxth-mind.
"""

from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from sxth_mind.api.app import get_mind

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
    user_mind: dict | None
    project_mind: dict | None = None


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


# ═══════════════════════════════════════════════════════════════
# Health Check
# ═══════════════════════════════════════════════════════════════

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    mind = get_mind()
    return {
        "status": "healthy",
        "adapter": mind.adapter.name,
        "storage": type(mind.storage).__name__,
    }


# ═══════════════════════════════════════════════════════════════
# Chat Endpoints
# ═══════════════════════════════════════════════════════════════

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message and get a response.

    The Mind automatically:
    - Creates/loads user and project state
    - Builds context-aware prompts
    - Updates state after the interaction
    """
    if request.stream:
        return StreamingResponse(
            stream_chat(request),
            media_type="text/event-stream",
        )

    mind = get_mind()
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
async def chat_stream(request: ChatRequest):
    """
    Stream a chat response via Server-Sent Events.

    Each event contains a token from the response.
    Final event contains [DONE].
    """
    return StreamingResponse(
        stream_chat(request),
        media_type="text/event-stream",
    )


async def stream_chat(request: ChatRequest) -> AsyncIterator[str]:
    """Generate SSE stream for chat response."""
    mind = get_mind()

    async for token in mind.chat_stream(
        user_id=request.user_id,
        message=request.message,
        project_id=request.project_id,
    ):
        yield f"data: {token}\n\n"

    yield "data: [DONE]\n\n"


# ═══════════════════════════════════════════════════════════════
# State Endpoints
# ═══════════════════════════════════════════════════════════════

@router.get("/state/{user_id}", response_model=StateResponse)
async def get_state(user_id: str, project_id: str | None = None):
    """
    Get the cognitive state for a user.

    Returns UserMind and optionally ProjectMind data.
    """
    mind = get_mind()
    state = await mind.get_state(user_id, project_id)

    return StateResponse(
        user_id=user_id,
        user_mind=state.get("user_mind"),
        project_mind=state.get("project_mind"),
    )


@router.get("/explain/{user_id}", response_model=ExplainResponse)
async def explain_state(user_id: str, project_id: str | None = None):
    """
    Get a human-readable explanation of the user's state.

    Useful for debugging and understanding what the Mind knows.
    """
    mind = get_mind()
    explanation = await mind.explain_state(user_id, project_id)

    return ExplainResponse(
        user_id=user_id,
        explanation=explanation,
    )


# ═══════════════════════════════════════════════════════════════
# Nudge Endpoints
# ═══════════════════════════════════════════════════════════════

@router.get("/nudges/{user_id}", response_model=list[NudgeResponse])
async def get_nudges(user_id: str):
    """
    Get pending nudges for a user.

    Nudges are proactive suggestions generated based on state.
    """
    mind = get_mind()
    nudges = await mind.get_pending_nudges(user_id)

    return [
        NudgeResponse(
            id=n.id,
            nudge_type=n.nudge_type,
            title=n.title,
            message=n.message,
            priority=n.priority,
            status=n.status,
        )
        for n in nudges
    ]


@router.post("/nudges/{user_id}/generate", response_model=list[NudgeResponse])
async def generate_nudges(user_id: str, project_id: str | None = None):
    """
    Generate new nudges for a user based on current state.

    This checks all nudge rules and creates any applicable nudges.
    """
    mind = get_mind()

    from sxth_mind.engine import BaselineNudgeEngine
    engine = BaselineNudgeEngine(mind.adapter, mind.storage)
    nudges = await engine.check_and_generate(user_id, project_id)

    return [
        NudgeResponse(
            id=n.id,
            nudge_type=n.nudge_type,
            title=n.title,
            message=n.message,
            priority=n.priority,
            status=n.status,
        )
        for n in nudges
    ]


@router.post("/nudges/{nudge_id}/dismiss")
async def dismiss_nudge(nudge_id: str):
    """
    Dismiss a nudge.

    The nudge will be marked as dismissed and won't appear again.
    """
    # Note: This is a stub implementation.
    # A real implementation would lookup the nudge by ID and update its status.
    # For now, we just acknowledge the request.
    return {"status": "dismissed", "nudge_id": nudge_id}


@router.post("/nudges/{nudge_id}/act")
async def act_on_nudge(nudge_id: str):
    """
    Mark a nudge as acted upon.

    Call this when the user takes action based on the nudge.
    """
    return {"status": "acted", "nudge_id": nudge_id}
