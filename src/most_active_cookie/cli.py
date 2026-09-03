"""Command-line interface for the most-active-cookie tool.

This module is the thin "controller" layer: it parses arguments, wires the
:mod:`~most_active_cookie.parser` and :mod:`~most_active_cookie.analyzer`
together, and translates outcomes into stdout output and process exit codes.
All real work lives in the parser and analyzer, which have no knowledge of the
command line.
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from datetime import date

from most_active_cookie import __version__
from most_active_cookie.analyzer import find_most_active_cookies
from most_active_cookie.errors import LogParseError, MostActiveCookieError
from most_active_cookie.parser import parse_log

logger = logging.getLogger("most_active_cookie")

EXIT_OK = 0
EXIT_ERROR = 1  # the log could not be read or parsed
EXIT_USAGE = 2  # the caller supplied bad arguments or a missing file


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser for the command-line interface."""
    parser = argparse.ArgumentParser(
        prog="most-active-cookie",
        description="Find the most active cookie for a specific day in a cookie log.",
    )
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        metavar="PATH",
        help="path to the cookie log CSV file",
    )
    parser.add_argument(
        "-d",
        "--date",
        required=True,
        dest="day",
        metavar="YYYY-MM-DD",
        type=_parse_date,
        help="the UTC day to analyse, in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--strict",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="fail on malformed lines (default); use --no-strict to skip them",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="increase logging verbosity (-v for info, -vv for debug)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def _parse_date(value: str) -> date:
    """Argument type that converts ``YYYY-MM-DD`` into a :class:`date`."""
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid date {value!r}: expected YYYY-MM-DD") from None


def _configure_logging(verbosity: int) -> None:
    """Send package logs to stderr at a level chosen by ``-v`` occurrences."""
    level = {0: logging.WARNING, 1: logging.INFO}.get(verbosity, logging.DEBUG)
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the command-line interface.

    Args:
        argv: command-line arguments (defaults to ``sys.argv[1:]``).

    Returns:
        A process exit code: ``0`` on success, ``1`` on a read/parse error, and
        ``2`` on a usage error (bad arguments or a missing file).
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args.verbose)

    try:
        # The file stays open while the analyzer lazily pulls entries, so a
        # sorted-log early exit avoids reading the rest of the file.
        with open(args.file, encoding="utf-8-sig") as stream:
            entries = parse_log(stream, strict=args.strict)
            cookies = find_most_active_cookies(entries, args.day)
    except FileNotFoundError:
        logger.error("file not found: %s", args.file)
        return EXIT_USAGE
    except LogParseError as error:
        logger.error("failed to parse log: %s", error)
        return EXIT_ERROR
    except MostActiveCookieError as error:  # defensive: any other domain error
        logger.error("%s", error)
        return EXIT_ERROR
    except OSError as error:
        logger.error("could not read %s: %s", args.file, error)
        return EXIT_ERROR

    if not cookies:
        logger.info("no cookies found for %s", args.day.isoformat())

    for cookie in cookies:
        print(cookie)
    return EXIT_OK
