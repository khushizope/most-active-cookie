"""Domain models for the :mod:`most_active_cookie` package."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime


@dataclass(frozen=True, slots=True)
class CookieLogEntry:
    """A single occurrence of a cookie in the log.

    The entry is immutable so it can be safely shared and hashed, and its
    timestamp is required to be timezone-aware: the log format always carries a
    UTC offset, and comparing dates across time zones is only well defined for
    aware datetimes.

    Attributes:
        cookie: the cookie identifier.
        timestamp: a timezone-aware moment at which the cookie was seen.
    """

    cookie: str
    timestamp: datetime

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ValueError("CookieLogEntry.timestamp must be timezone-aware")

    @property
    def utc_date(self) -> date:
        """The calendar date of this entry, normalised to UTC.

        Because the command-line ``-d`` argument is specified in UTC, every
        entry is bucketed by its UTC date rather than its local wall-clock date.
        """
        return self.timestamp.astimezone(UTC).date()
