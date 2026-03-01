from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from femic.cli.main import app


runner = CliRunner()
FIXTURE_DIR = Path(__file__).parent / "fixtures" / "vdyp" / "tsa08_debug"


def test_vdyp_report_cli_budget_passes() -> None:
    result = runner.invoke(
        app,
        [
            "vdyp",
            "report",
            "--curve-log",
            str(FIXTURE_DIR / "vdyp_curve_events-tsa08-fixture.jsonl"),
            "--run-log",
            str(FIXTURE_DIR / "vdyp_runs-tsa08-fixture.jsonl"),
            "--max-curve-warnings",
            "2",
            "--max-first-point-mismatches",
            "0",
            "--min-curve-events",
            "5",
            "--min-run-events",
            "6",
        ],
    )

    assert result.exit_code == 0
    assert "Curve events: 5" in result.stdout


def test_vdyp_report_cli_budget_fails() -> None:
    result = runner.invoke(
        app,
        [
            "vdyp",
            "report",
            "--curve-log",
            str(FIXTURE_DIR / "vdyp_curve_events-tsa08-fixture.jsonl"),
            "--run-log",
            str(FIXTURE_DIR / "vdyp_runs-tsa08-fixture.jsonl"),
            "--max-curve-warnings",
            "1",
        ],
    )

    assert result.exit_code == 1
    assert "VDYP warning-budget violations" in result.stdout
