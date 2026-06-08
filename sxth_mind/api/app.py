"""
FastAPI Application Factory

Creates and configures the sxth-mind HTTP API.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from sxth_mind.adapters.base import BaseAdapter
from sxth_mind.mind import Mind
from sxth_mind.providers.base import BaseLLMProvider
from sxth_mind.storage.base import BaseStorage
from sxth_mind.storage.memory import MemoryStorage


def get_mind(request: Request) -> Mind:
    """FastAPI dependency: return the Mind bound to this app instance."""
    mind: Mind | None = getattr(request.app.state, "mind", None)
    if mind is None:  # pragma: no cover - defensive, create_app always sets it
        raise RuntimeError("Mind not initialized. Create the app via create_app().")
    return mind


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifespan context manager for startup/shutdown."""
    mind: Mind = app.state.mind

    # Startup
    if hasattr(mind.storage, "initialize"):
        await mind.storage.initialize()

    yield

    # Shutdown
    if hasattr(mind.storage, "close"):
        await mind.storage.close()


def create_app(
    adapter: BaseAdapter,
    provider: BaseLLMProvider | None = None,
    storage: BaseStorage | None = None,
    cors_origins: list[str] | None = None,
) -> FastAPI:
    """
    Create a FastAPI application with sxth-mind.

    Args:
        adapter: Domain adapter (required)
        provider: LLM provider (optional, defaults based on what's installed)
        storage: Storage backend (optional, defaults to memory)
        cors_origins: CORS allowed origins (optional)

    Returns:
        Configured FastAPI application

    Usage:
        from sxth_mind.api import create_app
        from sxth_mind.adapters import SalesAdapter

        app = create_app(adapter=SalesAdapter())

        # Run with: uvicorn module:app --reload
    """
    # Create FastAPI app
    app = FastAPI(
        title="sxth-mind",
        description="The understanding layer for adaptive AI products",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Bind the Mind to this app instance (no module-level global, so multiple
    # apps can coexist in one process and tests stay isolated).
    app.state.mind = Mind(
        adapter=adapter,
        provider=provider,
        storage=storage or MemoryStorage(),
    )

    # Add CORS middleware
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Import routes here to avoid circular imports
    from sxth_mind.api.routes import router
    app.include_router(router)

    return app
