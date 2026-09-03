"""Unit tests for the cookie-activity analyzer."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta, timezone

from most_active_cookie.analyzer import find_most_active_cookies
from most_active_cookie.models import CookieLogEntry
from most_active_cookie.parser import parse_log


def _entry(cookie: str, iso: str) -> CookieLogEntry:
    return CookieLogEntry(cookie, datetime.fromisoformat(iso))


def test_single_most_active_cookie(sample_lines: list[str]) -> None:
    entries = parse_log(sample_lines)
    assert find_most_active_cookies(entries, date(2018, 12, 9)) == ["AtY0laUfhglK3lC7"]


def test_ties_return_all_sorted(sample_lines: list[str]) -> None:
    entries = parse_log(sample_lines)
    result = find_most_active_cookies(entries, date(2018, 12, 8))
    assert result == ["4sMM2LxV07bPJzwf", "SAZuXPGUrfbcn5UA", "fbcn5UAVanZf6UtG"]


def test_missing_day_returns_empty(sample_lines: list[str]) -> None:
    entries = parse_log(sample_lines)
    assert find_most_active_cookies(entries, date(2020, 1, 1)) == []


def test_empty_input_returns_empty() -> None:
    assert find_most_active_cookies([], date(2018, 12, 9)) == []


def test_sorted_scan_stops_early() -> None:
    """With assume_sorted, iteration must stop once it passes the target day."""

    def entries_with_sentinel() -> Iterator[CookieLogEntry]:
        yield _entry("hit", "2018-12-09T10:00:00+00:00")
        yield _entry("hit", "2018-12-09T09:00:00+00:00")
        yield _entry("older", "2018-12-08T23:00:00+00:00")
        raise AssertionError("scan should have stopped before reaching this entry")
        yield  # pragma: no cover

    result = find_most_active_cookies(entries_with_sentinel(), date(2018, 12, 9))
    assert result == ["hit"]


def test_full_scan_handles_unsorted_input() -> None:
    entries = [
        _entry("a", "2018-12-09T10:00:00+00:00"),
        _entry("b", "2018-12-08T10:00:00+00:00"),
        _entry("a", "2018-12-09T09:00:00+00:00"),  # target day appears again later
    ]
    assert find_most_active_cookies(entries, date(2018, 12, 9), assume_sorted=False) == ["a"]


def test_bucketing_uses_utc_date() -> None:
    tz_plus_five = timezone(timedelta(hours=5))
    entries = [
        # 02:00 +05:00 == 21:00 UTC on the 8th, so this belongs to the 8th.
        CookieLogEntry("night_owl", datetime(2018, 12, 9, 2, 0, tzinfo=tz_plus_five)),
        CookieLogEntry("day_user", datetime(2018, 12, 9, 12, 0, tzinfo=UTC)),
    ]
    on_the_8th = find_most_active_cookies(entries, date(2018, 12, 8), assume_sorted=False)
    on_the_9th = find_most_active_cookies(entries, date(2018, 12, 9), assume_sorted=False)
    assert on_the_8th == ["night_owl"]
    assert on_the_9th == ["day_user"]
