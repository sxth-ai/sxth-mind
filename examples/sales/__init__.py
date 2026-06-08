"""Compatibility shim.

The Sales adapter now ships inside the installed package. Prefer:

    from sxth_mind.adapters import SalesAdapter
"""

from sxth_mind.adapters.sales import SalesAdapter

__all__ = ["SalesAdapter"]
