"""Utilities for summarizing VDYP diagnostic JSONL logs."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


JsonMap = dict[str, Any]


@dataclass(frozen=True)
class VdypLogSummary:
    """Aggregate counters and mismatch diagnostics parsed from VDYP JSONL logs."""

    curve_events: int
    curve_status_counts: dict[str, int]
    curve_stage_counts: dict[str, int]
    curve_tsa_counts: dict[str, int]
    curve_warning_events: int
    first_point_events: int
    first_point_matches: int
    first_point_mismatches: int
    first_point_mismatch_rows: list[JsonMap]
    run_events: int
    run_status_counts: dict[str, int]
    run_phase_counts: dict[str, int]
    run_tsa_counts: dict[str, int]
    curve_parse_errors: int
    run_parse_errors: int


@dataclass(frozen=True)
class VdypWarningBudget:
    """Threshold configuration for pass/fail evaluation of VDYP warning signals."""

    max_curve_warnings: int | None = None
    max_first_point_mismatches: int | None = None
    max_curve_parse_errors: int | None = None
    max_run_parse_errors: int | None = None
    min_curve_events: int | None = None
    min_run_events: int | None = None


def _read_jsonl(path: Path) -> tuple[list[JsonMap], int]:
    if not path.exists():
        return [], 0
    rows: list[JsonMap] = []
    parse_errors = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            parse_errors += 1
            continue
        if isinstance(parsed, dict):
            rows.append(parsed)
        else:
            parse_errors += 1
    return rows, parse_errors


def _event_tsa(event: JsonMap) -> str:
    context = event.get("context")
    if isinstance(context, dict):
        tsa = context.get("tsa")
        if tsa is not None:
            return str(tsa)
    return "<unknown>"


def summarize_vdyp_logs(
    *,
    curve_log_path: Path,
    run_log_path: Path,
    expected_first_age: float,
    expected_first_volume: float,
    tolerance: float,
    mismatch_limit: int = 10,
) -> VdypLogSummary:
    """Parse VDYP logs and return normalized counts plus first-point QA summaries."""
    curve_rows, curve_parse_errors = _read_jsonl(curve_log_path)
    run_rows, run_parse_errors = _read_jsonl(run_log_path)

    curve_status_counts = Counter(str(r.get("status", "<missing>")) for r in curve_rows)
    curve_stage_counts = Counter(str(r.get("stage", "<missing>")) for r in curve_rows)
    curve_tsa_counts = Counter(_event_tsa(r) for r in curve_rows)
    curve_warning_events = sum(
        1 for r in curve_rows if str(r.get("status")) == "warning"
    )

    first_point_rows = [
        r for r in curve_rows if "first_age" in r and "first_volume" in r
    ]
    first_point_matches = 0
    first_point_mismatch_rows: list[JsonMap] = []
    for row in first_point_rows:
        try:
            first_age = float(row["first_age"])
            first_volume = float(row["first_volume"])
        except (TypeError, ValueError):
            first_point_mismatch_rows.append(row)
            continue
        age_ok = abs(first_age - expected_first_age) <= tolerance
        volume_ok = abs(first_volume - expected_first_volume) <= tolerance
        if age_ok and volume_ok:
            first_point_matches += 1
        else:
            first_point_mismatch_rows.append(row)
    first_point_mismatch_rows = first_point_mismatch_rows[:mismatch_limit]

    run_status_counts = Counter(str(r.get("status", "<missing>")) for r in run_rows)
    run_phase_counts = Counter(str(r.get("phase", "<missing>")) for r in run_rows)
    run_tsa_counts = Counter(_event_tsa(r) for r in run_rows)

    return VdypLogSummary(
        curve_events=len(curve_rows),
        curve_status_counts=dict(sorted(curve_status_counts.items())),
        curve_stage_counts=dict(sorted(curve_stage_counts.items())),
        curve_tsa_counts=dict(sorted(curve_tsa_counts.items())),
        curve_warning_events=curve_warning_events,
        first_point_events=len(first_point_rows),
        first_point_matches=first_point_matches,
        first_point_mismatches=len(first_point_rows) - first_point_matches,
        first_point_mismatch_rows=first_point_mismatch_rows,
        run_events=len(run_rows),
        run_status_counts=dict(sorted(run_status_counts.items())),
        run_phase_counts=dict(sorted(run_phase_counts.items())),
        run_tsa_counts=dict(sorted(run_tsa_counts.items())),
        curve_parse_errors=curve_parse_errors,
        run_parse_errors=run_parse_errors,
    )


def evaluate_warning_budget(
    summary: VdypLogSummary, budget: VdypWarningBudget
) -> list[str]:
    """Return budget-violation messages for the provided VDYP log summary."""
    violations: list[str] = []
    if budget.max_curve_warnings is not None:
        if summary.curve_warning_events > budget.max_curve_warnings:
            violations.append(
                "curve_warning_events "
                f"{summary.curve_warning_events} > {budget.max_curve_warnings}"
            )
    if budget.max_first_point_mismatches is not None:
        if summary.first_point_mismatches > budget.max_first_point_mismatches:
            violations.append(
                "first_point_mismatches "
                f"{summary.first_point_mismatches} > {budget.max_first_point_mismatches}"
            )
    if budget.max_curve_parse_errors is not None:
        if summary.curve_parse_errors > budget.max_curve_parse_errors:
            violations.append(
                "curve_parse_errors "
                f"{summary.curve_parse_errors} > {budget.max_curve_parse_errors}"
            )
    if budget.max_run_parse_errors is not None:
        if summary.run_parse_errors > budget.max_run_parse_errors:
            violations.append(
                "run_parse_errors "
                f"{summary.run_parse_errors} > {budget.max_run_parse_errors}"
            )
    if budget.min_curve_events is not None:
        if summary.curve_events < budget.min_curve_events:
            violations.append(
                f"curve_events {summary.curve_events} < {budget.min_curve_events}"
            )
    if budget.min_run_events is not None:
        if summary.run_events < budget.min_run_events:
            violations.append(
                f"run_events {summary.run_events} < {budget.min_run_events}"
            )
    return violations
