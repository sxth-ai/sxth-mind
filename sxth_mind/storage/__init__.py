"""Storage exports."""

from sxth_mind.storage.base import BaseStorage
from sxth_mind.storage.memory import MemoryStorage


# Lazy import for optional dependencies
def __getattr__(name: str):
    if name == "SQLiteStorage":
        from sxth_mind.storage.sqlite import SQLiteStorage
        return SQLiteStorage
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["BaseStorage", "MemoryStorage", "SQLiteStorage"]
