"""Shared pytest fixtures for the test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

# The exact sample from the assignment brief. Ordered most-recent-first.
SAMPLE_LOG = """\
cookie,timestamp
AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00
SAZuXPGUrfbcn5UA,2018-12-09T10:13:00+00:00
5UAVanZf6UtGyKVS,2018-12-09T07:25:00+00:00
AtY0laUfhglK3lC7,2018-12-09T06:19:00+00:00
SAZuXPGUrfbcn5UA,2018-12-08T22:03:00+00:00
4sMM2LxV07bPJzwf,2018-12-08T21:30:00+00:00
fbcn5UAVanZf6UtG,2018-12-08T09:30:00+00:00
4sMM2LxV07bPJzwf,2018-12-07T23:30:00+00:00
"""


@pytest.fixture
def sample_lines() -> list[str]:
    """The sample log split into individual lines (with trailing newlines)."""
    return SAMPLE_LOG.splitlines(keepends=True)


@pytest.fixture
def sample_log_file(tmp_path: Path) -> Path:
    """Write the sample log to a temporary file and return its path."""
    path = tmp_path / "cookie_log.csv"
    path.write_text(SAMPLE_LOG, encoding="utf-8")
    return path
