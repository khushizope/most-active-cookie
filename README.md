# Most Active Cookie

[![CI](https://github.com/khushizope/most-active-cookie/actions/workflows/ci.yml/badge.svg)](https://github.com/khushizope/most-active-cookie/actions/workflows/ci.yml)

A small, dependency-free command-line tool that reads a cookie log and prints the
**most active cookie** for a given day — the cookie seen the most times during
that day (in UTC).

## Quick start

No installation is required (the tool has no third-party dependencies). From the
repository root:

```bash
PYTHONPATH=src python -m most_active_cookie -f cookie_log.csv -d 2018-12-09
# -> AtY0laUfhglK3lC7
```

> On Windows PowerShell, set the path first:
> `$env:PYTHONPATH = "src"; python -m most_active_cookie -f cookie_log.csv -d 2018-12-09`

To get the shorter `most-active-cookie` command and the dev tools, see
[Installation](#installation).

## Requirements

- Python **3.11+**
- No runtime dependencies — standard library only (`argparse`, `logging`,
  `datetime`). Third-party packages are used **only** for development (testing,
  linting, type-checking), per the assignment constraints.

## Installation

Installing is optional; do it to expose the `most-active-cookie` command and the
development tooling. A virtual environment is recommended:

```bash
python -m venv .venv
# Windows:        .venv\Scripts\activate
# macOS / Linux:  source .venv/bin/activate
pip install -e ".[dev]"
```

The tool is then available as `most-active-cookie` (equivalent to
`python -m most_active_cookie`).

## Usage

```text
most-active-cookie -f PATH -d YYYY-MM-DD [--no-strict] [-v] [--version]

  -f, --file PATH         path to the cookie log CSV file (required)
  -d, --date YYYY-MM-DD   the UTC day to analyse (required)
      --strict / --no-strict
                          --strict (default) fails on a malformed line;
                          --no-strict skips it and logs a warning
  -v, --verbose           increase logging verbosity (-v info, -vv debug)
      --version           print the version and exit
```

### Input format

A CSV file with a header row; each line is a cookie and a timezone-aware
ISO-8601 timestamp:

```csv
cookie,timestamp
AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00
SAZuXPGUrfbcn5UA,2018-12-09T10:13:00+00:00
```

### Ties and empty days

When several cookies share the highest count, every one of them is printed:

```bash
most-active-cookie -f cookie_log.csv -d 2018-12-08
# -> 4sMM2LxV07bPJzwf
#    SAZuXPGUrfbcn5UA
#    fbcn5UAVanZf6UtG
```

If no cookie was seen on the requested day, nothing is printed and the exit code
is still `0`.

### Exit codes

| Code | Meaning |
| ---- | ------- |
| `0`  | Success (including a day with no cookies, which prints nothing). |
| `1`  | The log could not be read, or a line failed to parse in strict mode. |
| `2`  | Usage error: bad arguments, an invalid date, or a missing file. |

## How it works

Each timestamp is normalised to **UTC** before its date is compared, so results
are correct even for entries recorded in other time zones. Because the log is
guaranteed to be sorted by timestamp **descending** (most recent first), the tool
counts occurrences within the target day and **stops as soon as it crosses into an
earlier day** — it never reads the rest of the file.

## Architecture

The code is split into small, single-responsibility layers, each testable in
isolation, with data flowing one way: **`cli` → `parser` → `analyzer`**.

| Module | Responsibility |
| ------ | -------------- |
| `models.py`   | `CookieLogEntry` — one log entry: a cookie and the time it was seen. |
| `parser.py`   | Turns raw log lines into `CookieLogEntry` values. |
| `analyzer.py` | `find_most_active_cookies()` — counts cookies for a day and returns the winner(s). |
| `cli.py`      | The command-line layer: argument parsing, wiring, exit codes, output. |
| `errors.py`   | The error types (`MostActiveCookieError`, `LogParseError`). |

Log entries are parsed lazily, allowing processing to stop once the requested
date has been passed.

## Development

```bash
make install     # pip install -e ".[dev]"
make test        # pytest with coverage
make lint        # ruff check
make format      # ruff format
make typecheck   # mypy
make check       # lint + typecheck + test
```

Tests cover parsing, cookie counting, ties, empty dates, UTC handling,
sorted-input optimization, and CLI behavior. CI runs the same checks on
Python 3.11–3.13 via GitHub Actions.

## Assumptions & decisions

These follow the assignment's stated assumptions and record the choices made
around them:

- **`-d` is UTC** — entries are bucketed by UTC date (see [How it works](#how-it-works)).
- **Ties** are all returned, sorted lexicographically for deterministic output.
- **A sorted log** is exploited for the early exit, not required —
  `assume_sorted=False` is a correct fallback.
- **The whole file fits in memory**, per the brief; in practice only per-day
  counts are held, bounded by the number of distinct cookies that day.
- **Malformed lines** are a hard error by default (with the line number);
  `--no-strict` downgrades them to a logged warning and skips them.

## License

Released under the MIT License. See [LICENSE](LICENSE).
