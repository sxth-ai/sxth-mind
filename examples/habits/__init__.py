"""Compatibility shim.

The Habit Coach adapter now ships inside the installed package. Prefer:

    from sxth_mind.adapters import HabitCoachAdapter
"""

from sxth_mind.adapters.habits import HabitCoachAdapter

__all__ = ["HabitCoachAdapter"]
