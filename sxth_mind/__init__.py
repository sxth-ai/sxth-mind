"""
sxth-mind: The understanding layer for adaptive AI products.

The Mind accumulates state, detects patterns, and adapts over time.
"""

from sxth_mind.adapters.base import BaseAdapter
from sxth_mind.mind import Mind
from sxth_mind.providers.base import BaseLLMProvider
from sxth_mind.schemas.project_mind import ProjectMind
from sxth_mind.schemas.user_mind import UserMind
from sxth_mind.storage.base import BaseStorage

__version__ = "0.1.0"

__all__ = [
    "Mind",
    "BaseAdapter",
    "BaseLLMProvider",
    "BaseStorage",
    "UserMind",
    "ProjectMind",
]
