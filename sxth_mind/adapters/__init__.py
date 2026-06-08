"""Adapter exports.

``BaseAdapter`` is the interface you implement for your own domain. The other
three are batteries-included reference adapters you can use directly or read as
worked examples.
"""

from sxth_mind.adapters.base import BaseAdapter
from sxth_mind.adapters.habits import HabitCoachAdapter
from sxth_mind.adapters.learning import LearningAdapter
from sxth_mind.adapters.sales import SalesAdapter

__all__ = [
    "BaseAdapter",
    "SalesAdapter",
    "HabitCoachAdapter",
    "LearningAdapter",
]
