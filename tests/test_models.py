"""Unit tests for the domain model."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta, timezone

import pytest

from most_active_cookie.models import CookieLogEntry


def test_utc_date_for_utc_timestamp() -> None:
    entry = CookieLogEntry("abc", datetime(2018, 12, 9, 14, 19, tzinfo=UTC))
    assert entry.utc_date == date(2018, 12, 9)


def test_utc_date_normalises_non_utc_offset() -> None:
    # 01:30 at +05:00 is 20:30 on the *previous* day in UTC.
    tz = timezone(timedelta(hours=5))
    entry = CookieLogEntry("abc", datetime(2018, 12, 9, 1, 30, tzinfo=tz))
    assert entry.utc_date == date(2018, 12, 8)


def test_naive_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        CookieLogEntry("abc", datetime(2018, 12, 9, 14, 19))


def test_entry_is_immutable() -> None:
    entry = CookieLogEntry("abc", datetime(2018, 12, 9, tzinfo=UTC))
    with pytest.raises(AttributeError):
        entry.cookie = "xyz"  # type: ignore[misc]
