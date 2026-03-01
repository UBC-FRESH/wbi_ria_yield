from __future__ import annotations

import json
from pathlib import Path

from femic.vdyp.reporting import (
    VdypWarningBudget,
    evaluate_warning_budget,
    summarize_vdyp_logs,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "vdyp" / "tsa08_debug"


def test_tsa08_debug_regression_summary_counts() -> None:
    summary = summarize_vdyp_logs(
        curve_log_path=FIXTURE_DIR / "vdyp_curve_events-tsa08-fixture.jsonl",
        run_log_path=FIXTURE_DIR / "vdyp_runs-tsa08-fixture.jsonl",
        expected_first_age=1.0,
        expected_first_volume=1e-6,
        tolerance=1e-12,
    )

    assert summary.curve_events == 5
    assert summary.curve_warning_events == 2
    assert summary.curve_status_counts == {"ok": 3, "warning": 2}
    assert summary.curve_stage_counts == {
        "body_input": 1,
        "curve_input": 1,
        "tipsy_input": 1,
        "toe_fit": 2,
    }
    assert summary.first_point_events == 3
    assert summary.first_point_matches == 3
    assert summary.first_point_mismatches == 0

    assert summary.run_events == 6
    assert summary.run_status_counts == {
        "dispatch": 2,
        "empty_output": 1,
        "ok": 1,
        "start": 2,
    }
    assert summary.run_phase_counts == {"bootstrap": 6}


def test_tsa08_debug_regression_warning_budget() -> None:
    summary = summarize_vdyp_logs(
        curve_log_path=FIXTURE_DIR / "vdyp_curve_events-tsa08-fixture.jsonl",
        run_log_path=FIXTURE_DIR / "vdyp_runs-tsa08-fixture.jsonl",
        expected_first_age=1.0,
        expected_first_volume=1e-6,
        tolerance=1e-12,
    )
    budget_dict = json.loads((FIXTURE_DIR / "regression_budget.json").read_text())
    budget = VdypWarningBudget(**budget_dict)

    assert evaluate_warning_budget(summary, budget) == []


def test_warning_budget_flags_unexpected_growth() -> None:
    summary = summarize_vdyp_logs(
        curve_log_path=FIXTURE_DIR / "vdyp_curve_events-tsa08-fixture.jsonl",
        run_log_path=FIXTURE_DIR / "vdyp_runs-tsa08-fixture.jsonl",
        expected_first_age=1.0,
        expected_first_volume=1e-6,
        tolerance=1e-12,
    )
    strict_budget = VdypWarningBudget(max_curve_warnings=1)

    violations = evaluate_warning_budget(summary, strict_budget)

    assert violations
    assert "curve_warning_events" in violations[0]
