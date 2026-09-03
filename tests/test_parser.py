"""Unit tests for the log parser."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import pytest

from most_active_cookie.errors import LogParseError
from most_active_cookie.parser import parse_line, parse_log


def test_parse_line_valid() -> None:
    entry = parse_line("AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00")
    assert entry.cookie == "AtY0laUfhglK3lC7"
    assert entry.timestamp == datetime(2018, 12, 9, 14, 19, tzinfo=UTC)


def test_parse_line_strips_surrounding_whitespace() -> None:
    entry = parse_line("  abc , 2018-12-09T14:19:00+00:00 ")
    assert entry.cookie == "abc"


@pytest.mark.parametrize(
    "line",
    [
        "only_one_column",
        "a,b,c",
        "cookie,2018-12-09T14:19:00+00:00,extra",
    ],
)
def test_parse_line_rejects_wrong_column_count(line: str) -> None:
    with pytest.raises(LogParseError, match="columns"):
        parse_line(line)


def test_parse_line_rejects_empty_cookie() -> None:
    with pytest.raises(LogParseError, match="empty"):
        parse_line(",2018-12-09T14:19:00+00:00")


def test_parse_line_rejects_invalid_timestamp() -> None:
    with pytest.raises(LogParseError, match="invalid timestamp"):
        parse_line("abc,not-a-timestamp")


def test_parse_line_rejects_naive_timestamp() -> None:
    with pytest.raises(LogParseError, match="UTC offset"):
        parse_line("abc,2018-12-09T14:19:00")


def test_parse_log_skips_header_and_blank_lines(sample_lines: list[str]) -> None:
    entries = list(parse_log(sample_lines))
    assert len(entries) == 8
    assert entries[0].cookie == "AtY0laUfhglK3lC7"


def test_parse_log_preserves_order(sample_lines: list[str]) -> None:
    cookies = [entry.cookie for entry in parse_log(sample_lines)]
    assert cookies[0] == "AtY0laUfhglK3lC7"
    assert cookies[-1] == "4sMM2LxV07bPJzwf"


def test_parse_log_strict_raises_with_line_number() -> None:
    lines = ["cookie,timestamp", "good,2018-12-09T14:19:00+00:00", "broken-line"]
    with pytest.raises(LogParseError) as exc_info:
        list(parse_log(lines))
    assert exc_info.value.line_number == 3


def test_parse_log_non_strict_skips_and_warns(caplog: pytest.LogCaptureFixture) -> None:
    lines = [
        "cookie,timestamp",
        "good,2018-12-09T14:19:00+00:00",
        "broken-line",
        "also_good,2018-12-09T10:00:00+00:00",
    ]
    with caplog.at_level(logging.WARNING):
        entries = list(parse_log(lines, strict=False))
    assert [e.cookie for e in entries] == ["good", "also_good"]
    assert "skipping malformed line" in caplog.text


def test_parse_log_can_keep_a_header_like_first_data_row() -> None:
    # skip_header only strips the literal header; real data is untouched.
    entries = list(parse_log(["abc,2018-12-09T14:19:00+00:00"], skip_header=False))
    assert len(entries) == 1
