"""Analysis of cookie activity over a single UTC day."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from datetime import date

from most_active_cookie.models import CookieLogEntry


def find_most_active_cookies(
    entries: Iterable[CookieLogEntry],
    target_date: date,
    *,
    assume_sorted: bool = True,
) -> list[str]:
    """Return the cookie(s) seen most often on ``target_date`` (UTC).

    The "most active" cookie is the one that appears the most times during the
    given day. The result contains every cookie tied for that highest count,
    sorted lexicographically so the output is deterministic. When no cookie was
    seen on the day, an empty list is returned.

    Performance:
        The log is guaranteed to be sorted by timestamp descending (most recent
        first). When ``assume_sorted`` is true (the default) the scan stops as
        soon as it moves past ``target_date`` into an older day, so only the
        relevant slice of the log is inspected instead of the whole file. Set
        ``assume_sorted`` to false to force a full scan for inputs whose ordering
        cannot be trusted.

    Args:
        entries: the parsed log entries, ordered most-recent-first when
            ``assume_sorted`` is true.
        target_date: the UTC calendar day to analyse.
        assume_sorted: whether ``entries`` are sorted by timestamp descending.

    Returns:
        A lexicographically sorted list of the most active cookies (possibly
        empty).
    """
    counts: Counter[str] = Counter()

    for entry in entries:
        entry_date = entry.utc_date
        if entry_date == target_date:
            counts[entry.cookie] += 1
        elif assume_sorted and entry_date < target_date:
            # Entries are sorted newest-first, so once we cross below the target
            # day no later entry can belong to it: stop reading.
            break

    if not counts:
        return []

    highest = max(counts.values())
    return sorted(cookie for cookie, count in counts.items() if count == highest)
