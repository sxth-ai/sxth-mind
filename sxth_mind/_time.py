"""
Time utilities.

Centralizes "now" so all timestamps are timezone-aware UTC and consistent
across the codebase. Using a single helper avoids the deprecated
``datetime.utcnow()`` (which returns naive datetimes) and prevents
naive/aware subtraction errors when computing elapsed time.
"""

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)
