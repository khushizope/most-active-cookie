"""Integration tests for the command-line interface."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from most_active_cookie import __version__
from most_active_cookie.cli import EXIT_ERROR, EXIT_OK, EXIT_USAGE, main


def test_cli_reports_single_most_active_cookie(
    sample_log_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["-f", str(sample_log_file), "-d", "2018-12-09"])
    assert exit_code == EXIT_OK
    assert capsys.readouterr().out == "AtY0laUfhglK3lC7\n"


def test_cli_reports_all_tied_cookies(
    sample_log_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["-f", str(sample_log_file), "-d", "2018-12-08"])
    assert exit_code == EXIT_OK
    assert capsys.readouterr().out == "4sMM2LxV07bPJzwf\nSAZuXPGUrfbcn5UA\nfbcn5UAVanZf6UtG\n"


def test_cli_day_without_activity_prints_nothing(
    sample_log_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["-f", str(sample_log_file), "-d", "2020-01-01"])
    assert exit_code == EXIT_OK
    assert capsys.readouterr().out == ""


def test_cli_missing_file_returns_usage_error(caplog: pytest.LogCaptureFixture) -> None:
    exit_code = main(["-f", "does_not_exist.csv", "-d", "2018-12-09"])
    assert exit_code == EXIT_USAGE
    assert "file not found" in caplog.text


def test_cli_invalid_date_is_a_usage_error(sample_log_file: Path) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["-f", str(sample_log_file), "-d", "09-12-2018"])
    assert exc_info.value.code == EXIT_USAGE


def test_cli_strict_mode_fails_on_malformed_log(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    bad = tmp_path / "bad.csv"
    bad.write_text("cookie,timestamp\nbroken-line\n", encoding="utf-8")
    exit_code = main(["-f", str(bad), "-d", "2018-12-09"])
    assert exit_code == EXIT_ERROR
    assert "failed to parse log" in caplog.text


def test_cli_no_strict_skips_malformed_log(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = tmp_path / "bad.csv"
    bad.write_text(
        "cookie,timestamp\nbroken-line\ngood,2018-12-09T10:00:00+00:00\n",
        encoding="utf-8",
    )
    exit_code = main(["-f", str(bad), "-d", "2018-12-09", "--no-strict"])
    assert exit_code == EXIT_OK
    assert capsys.readouterr().out == "good\n"


def test_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == EXIT_OK
    assert __version__ in capsys.readouterr().out


def test_module_entrypoint_runs_end_to_end(sample_log_file: Path) -> None:
    """Smoke-test the real ``python -m most_active_cookie`` invocation."""
    project_root = Path(__file__).resolve().parents[1]
    env = {**os.environ, "PYTHONPATH": str(project_root / "src")}
    command = [
        sys.executable,
        "-m",
        "most_active_cookie",
        "-f",
        str(sample_log_file),
        "-d",
        "2018-12-09",
    ]
    result = subprocess.run(command, capture_output=True, text=True, env=env, check=True)
    assert result.stdout == "AtY0laUfhglK3lC7\n"
