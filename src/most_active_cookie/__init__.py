"""Find the most active cookie for a given day in a cookie log file.

The public API is intentionally small: parse a log into
:class:`CookieLogEntry` values, then feed them to
:func:`find_most_active_cookies`.
"""

from __future__ import annotations

from most_active_cookie.analyzer import find_most_active_cookies
from most_active_cookie.errors import LogParseError, MostActiveCookieError
from most_active_cookie.models import CookieLogEntry
from most_active_cookie.parser import parse_line, parse_log

__all__ = [
    "CookieLogEntry",
    "LogParseError",
    "MostActiveCookieError",
    "find_most_active_cookies",
    "parse_line",
    "parse_log",
]

__version__ = "1.0.0"
