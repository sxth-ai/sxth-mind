"""Compatibility shim.

The Learning adapter now ships inside the installed package. Prefer:

    from sxth_mind.adapters import LearningAdapter
"""

from sxth_mind.adapters.learning import LearningAdapter

__all__ = ["LearningAdapter"]
