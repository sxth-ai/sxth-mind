"""Compatibility shim for the reference adapters.

These adapters now ship inside the installed package under
``sxth_mind.adapters``. Importing from ``examples`` still works when running
from a source checkout, but the canonical import is:

    from sxth_mind.adapters import SalesAdapter, HabitCoachAdapter, LearningAdapter
"""

from sxth_mind.adapters import (
    HabitCoachAdapter,
    LearningAdapter,
    SalesAdapter,
)

__all__ = ["SalesAdapter", "HabitCoachAdapter", "LearningAdapter"]
