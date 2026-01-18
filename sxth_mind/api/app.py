"""
FastAPI Application Factory

Creates and configures the sxth-mind HTTP API.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sxth_mind.adapters.base import BaseAdapter
from sxth_mind.mind import Mind
from sxth_mind.providers.base import BaseLLMProvider
from sxth_mind.storage.base import BaseStorage
from sxth_mind.storage.memory import MemoryStorage

# Global mind instance (set during app creation)
_mind: Mind | None = None


def get_mind() -> Mind:
    """Get the global Mind instance."""
    if _mind is None:
        raise RuntimeError("Mind not initialized. Call create_app() first.")
    return _mind


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifespan context manager for startup/shutdown."""
    # Startup
    if _mind and hasattr(_mind.storage, "initialize"):
        await _mind.storage.initialize()

    yield

    # Shutdown
    if _mind and hasattr(_mind.storage, "close"):
        await _mind.storage.close()


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
        from examples.sales import SalesAdapter

        app = create_app(adapter=SalesAdapter())

        # Run with: uvicorn module:app --reload
    """
    global _mind

    # Create Mind instance
    _mind = Mind(
        adapter=adapter,
        provider=provider,
        storage=storage or MemoryStorage(),
    )

    # Create FastAPI app
    app = FastAPI(
        title="sxth-mind",
        description="The understanding layer for adaptive AI products",
        version="0.1.0",
        lifespan=lifespan,
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
