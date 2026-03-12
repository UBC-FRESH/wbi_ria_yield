"""Invariant metric extraction and evaluation for instance rebuild runs."""

from __future__ import annotations

from dataclasses import dataclass
import csv
import json
import re
from pathlib import Path
from typing import Any

from femic.patchworks_runtime import (
    infer_patchworks_model_dir,
    load_patchworks_runtime_config,
)

_POLYGON_MISMATCH_PATTERN = re.compile(
    r"Block shape file contains\s+(\d+)\s+polygons that do not have corresponding blocks",
    flags=re.IGNORECASE,
)
_BLOCK_MISMATCH_PATTERN = re.compile(
    r"blocks,?csv input file contains\s+(\d+)\s+blocks that do not have corresponding polygons",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class InvariantResult:
    """Evaluation outcome for a single configured invariant."""

    invariant_id: str
    severity: str
    metric: str
    comparator: str
    target: Any
    measured: Any
    status: str
    remediation: str | None
    message: str


def collect_rebuild_metrics(
    *,
    instance_root: Path,
    log_dir: Path,
    run_id: str,
    patchworks_config_path: Path | None,
) -> dict[str, Any]:
    """Collect known metric values used by rebuild-spec invariants."""

    metrics: dict[str, Any] = {}
    model_dir: Path | None = None
    if patchworks_config_path is not None and patchworks_config_path.exists():
        config = load_patchworks_runtime_config(patchworks_config_path)
        model_dir = infer_patchworks_model_dir(config)
        tracks_dir = config.matrix_output_dir
        blocks_path = tracks_dir / "blocks.csv"
        accounts_path = tracks_dir / "accounts.csv"
        accounts_list = _accounts_list(accounts_path)

        metrics["managed_area_ha"] = _managed_area_ha(blocks_path)
        metrics["accounts.targets.required_present"] = accounts_path.exists()
        metrics["accounts.list"] = accounts_list
        metrics["managed_species_account_count"] = _managed_species_account_count(
            accounts_path
        )
        metrics["seral_account_count"] = _seral_account_count(accounts_path)

    metrics["block_join_mismatch_count"] = _block_join_mismatch_count(
        log_dir=log_dir,
        run_id=run_id,
    )
    metrics["topology_edge_count"] = _topology_edge_count(model_dir=model_dir)
    return metrics


def evaluate_invariants(
    *,
    invariants: list[dict[str, Any]],
    metrics: dict[str, Any],
) -> list[InvariantResult]:
    """Evaluate configured invariants against measured metrics."""

    results: list[InvariantResult] = []
    for invariant in invariants:
        invariant_id = str(invariant.get("invariant_id", "")).strip()
        severity = str(invariant.get("severity", "warn")).strip() or "warn"
        metric = str(invariant.get("metric", "")).strip()
        comparator = str(invariant.get("comparator", "")).strip()
        target = invariant.get("target")
        remediation = invariant.get("remediation")
        measured = metrics.get(metric)

        ok, detail = _compare_metric(
            comparator=comparator,
            measured=measured,
            target=target,
        )
        if ok:
            status = "pass"
        else:
            status = "fail" if severity == "fatal" else "warn"
        message = (
            f"{metric} {comparator} {target!r} (measured={measured!r})"
            if not detail
            else detail
        )
        results.append(
            InvariantResult(
                invariant_id=invariant_id,
                severity=severity,
                metric=metric,
                comparator=comparator,
                target=target,
                measured=measured,
                status=status,
                remediation=str(remediation) if remediation is not None else None,
                message=message,
            )
        )
    return results


def has_fatal_invariant_failures(results: list[InvariantResult]) -> bool:
    """Return true when any invariant has fatal failure status."""

    return any(item.status == "fail" and item.severity == "fatal" for item in results)


def _managed_area_ha(blocks_csv_path: Path) -> float | None:
    if not blocks_csv_path.exists():
        return None
    total = 0.0
    with blocks_csv_path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            block_type = str(row.get("TYPE", "")).strip().lower()
            if block_type != "managed":
                continue
            try:
                total += float(row.get("AREA", "0") or 0.0)
            except (TypeError, ValueError):
                continue
    return total


def _managed_species_account_count(accounts_csv_path: Path) -> int | None:
    if not accounts_csv_path.exists():
        return None
    count = 0
    with accounts_csv_path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            account = str(row.get("ACCOUNT", "")).strip()
            lowered = account.lower()
            if not lowered.startswith("product.yield.managed."):
                continue
            if lowered.endswith(".total"):
                continue
            count += 1
    return count


def _accounts_list(accounts_csv_path: Path) -> list[str] | None:
    if not accounts_csv_path.exists():
        return None
    accounts: set[str] = set()
    with accounts_csv_path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            account = str(row.get("ACCOUNT", "")).strip()
            if account:
                accounts.add(account)
    return sorted(accounts)


def _seral_account_count(accounts_csv_path: Path) -> int | None:
    if not accounts_csv_path.exists():
        return None
    count = 0
    with accounts_csv_path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            account = str(row.get("ACCOUNT", "")).strip().lower()
            if account.startswith("feature.seral.") or account.startswith(
                "product.seral.area."
            ):
                count += 1
    return count


def _block_join_mismatch_count(*, log_dir: Path, run_id: str) -> int | None:
    log_path = log_dir / f"patchworks_matrixbuilder_stdout-{run_id}.log"
    if not log_path.exists():
        return None
    text = log_path.read_text(encoding="utf-8", errors="ignore")
    counts: list[int] = []
    counts.extend(int(value) for value in _POLYGON_MISMATCH_PATTERN.findall(text))
    counts.extend(int(value) for value in _BLOCK_MISMATCH_PATTERN.findall(text))
    return max(counts) if counts else 0


def _topology_edge_count(*, model_dir: Path | None) -> int | None:
    if model_dir is None:
        return None
    blocks_dir = model_dir / "blocks"
    if not blocks_dir.exists():
        return None
    topology_files = sorted(blocks_dir.glob("topology_blocks_*r.csv"))
    if not topology_files:
        return None
    topology_path = topology_files[-1]
    with topology_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            next(reader)
        except StopIteration:
            return 0
        return sum(1 for _ in reader)


def _compare_metric(*, comparator: str, measured: Any, target: Any) -> tuple[bool, str]:
    if comparator == "exists":
        ok = measured is not None
        return ok, "" if ok else "metric not found"
    if comparator == "not_exists":
        ok = measured is None
        return ok, "" if ok else "metric exists but should not"
    if measured is None:
        return False, "metric not found"

    if comparator == "eq":
        return measured == target, ""
    if comparator == "ne":
        return measured != target, ""
    if comparator in {"gt", "gte", "lt", "lte"}:
        try:
            measured_num = float(measured)
            target_num = float(target)
        except (TypeError, ValueError):
            return False, "numeric comparator requires numeric measured/target"
        if comparator == "gt":
            return measured_num > target_num, ""
        if comparator == "gte":
            return measured_num >= target_num, ""
        if comparator == "lt":
            return measured_num < target_num, ""
        return measured_num <= target_num, ""
    if comparator in {"contains", "not_contains"}:
        if not isinstance(measured, (list, tuple, set)):
            return False, "contains comparator requires sequence-like measured value"
        measured_values = {str(item) for item in measured}
        target_value = str(target)
        contains = target_value in measured_values
        if comparator == "contains":
            return contains, ""
        return not contains, ""
    return False, f"unsupported comparator: {comparator}"


def serialize_invariant_results(results: list[InvariantResult]) -> list[dict[str, Any]]:
    """Convert dataclass results to JSON-serializable dictionaries."""

    return [
        {
            "invariant_id": item.invariant_id,
            "severity": item.severity,
            "metric": item.metric,
            "comparator": item.comparator,
            "target": item.target,
            "measured": item.measured,
            "status": item.status,
            "remediation": item.remediation,
            "message": item.message,
        }
        for item in results
    ]


def append_invariant_payload_to_report(
    *,
    report_path: Path,
    metrics: dict[str, Any],
    invariant_results: list[InvariantResult],
) -> None:
    """Append metrics + invariant results to existing rebuild report JSON."""

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    payload["metrics"] = metrics
    payload["invariant_results"] = serialize_invariant_results(invariant_results)
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
