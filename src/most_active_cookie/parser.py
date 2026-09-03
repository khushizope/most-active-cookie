"""Parsing of raw cookie-log text into :class:`CookieLogEntry` values.

The parser is deliberately decoupled from file I/O: it works on any iterable of
lines. That keeps it trivially unit-testable (feed it a list of strings) and
lets callers stream from files, network sources, or in-memory data without
changing the parsing logic.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable, Iterator
from datetime import datetime

from most_active_cookie.errors import LogParseError
from most_active_cookie.models import CookieLogEntry

logger = logging.getLogger(__name__)

_HEADER = "cookie,timestamp"
_EXPECTED_COLUMNS = 2


def parse_line(line: str) -> CookieLogEntry:
    """Parse a single ``cookie,timestamp`` line into a :class:`CookieLogEntry`.

    Args:
        line: one log line, e.g. ``"AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00"``.

    Returns:
        The parsed :class:`CookieLogEntry`.

    Raises:
        LogParseError: if the line does not have exactly two columns, the cookie
            is empty, or the timestamp is not a valid timezone-aware ISO-8601
            value.
    """
    fields = line.split(",")
    if len(fields) != _EXPECTED_COLUMNS:
        raise LogParseError(
            f"expected {_EXPECTED_COLUMNS} columns, found {len(fields)}",
            raw_line=line,
        )

    cookie, raw_timestamp = (field.strip() for field in fields)
    if not cookie:
        raise LogParseError("cookie identifier is empty", raw_line=line)

    try:
        timestamp = datetime.fromisoformat(raw_timestamp)
    except ValueError as exc:
        raise LogParseError(f"invalid timestamp {raw_timestamp!r}", raw_line=line) from exc

    if timestamp.tzinfo is None:
        raise LogParseError(
            f"timestamp {raw_timestamp!r} is missing a UTC offset",
            raw_line=line,
        )

    return CookieLogEntry(cookie=cookie, timestamp=timestamp)


def parse_log(
    lines: Iterable[str],
    *,
    strict: bool = True,
    skip_header: bool = True,
) -> Iterator[CookieLogEntry]:
    """Parse an iterable of log lines into :class:`CookieLogEntry` values.

    Blank lines are ignored. A ``cookie,timestamp`` header row is skipped when
    ``skip_header`` is true. Parsing is lazy: entries are yielded one at a time,
    so a consumer that stops early (see :func:`most_active_cookie.analyzer`)
    never forces the whole input to be read.

    Args:
        lines: any iterable of raw log lines.
        strict: when true (default) a malformed line raises
            :class:`LogParseError`; when false, the line is logged at WARNING
            level and skipped.
        skip_header: when true (default) a line equal to the
            ``cookie,timestamp`` header is ignored.

    Yields:
        :class:`CookieLogEntry` values, in the same order as the input lines.

    Raises:
        LogParseError: when ``strict`` is true and a line cannot be parsed; the
            raised error carries the 1-based line number.
    """
    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            continue
        if skip_header and line.lower() == _HEADER:
            continue
        try:
            yield parse_line(line)
        except LogParseError as error:
            enriched = LogParseError(str(error), line_number=line_number, raw_line=error.raw_line)
            if strict:
                raise enriched from error
            logger.warning("skipping malformed line: %s", enriched)
