"""Domain-specific exceptions for the :mod:`most_active_cookie` package."""

from __future__ import annotations


class MostActiveCookieError(Exception):
    """Base class for every error raised by this package.

    Catching this type lets callers handle all package-level failures without
    coupling to the concrete exception hierarchy.
    """


class LogParseError(MostActiveCookieError):
    """Raised when a line in the cookie log cannot be parsed.

    Attributes:
        line_number: 1-based index of the offending line, when known.
        raw_line: the original, unparsed line content.
    """

    def __init__(
        self,
        message: str,
        *,
        line_number: int | None = None,
        raw_line: str | None = None,
    ) -> None:
        self.line_number = line_number
        self.raw_line = raw_line
        location = f" (line {line_number})" if line_number is not None else ""
        super().__init__(f"{message}{location}")
