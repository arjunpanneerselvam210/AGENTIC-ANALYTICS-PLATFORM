"""
Indian Standard Time (IST) Timezone Utilities for FreshMart Analytics Platform.
Enforces UTC+05:30 across all API timestamps, audit logs, and response serialization.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional

# Indian Standard Time (IST) is UTC + 5 hours 30 minutes
IST = timezone(timedelta(hours=5, minutes=30), name="IST")

def get_current_ist() -> datetime:
    """Returns the current timezone-aware datetime in Indian Standard Time (IST)."""
    return datetime.now(IST)

def get_current_ist_iso() -> str:
    """Returns ISO-8601 string with explicit +05:30 offset (e.g. 2026-09-25T22:30:00+05:30)."""
    return datetime.now(IST).isoformat()

def to_ist(dt: Optional[datetime]) -> datetime:
    """Converts any datetime to timezone-aware IST."""
    if dt is None:
        return get_current_ist()
    if dt.tzinfo is None:
        # Assume UTC if naive
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IST)
