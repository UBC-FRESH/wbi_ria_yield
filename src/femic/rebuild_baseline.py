"""Baseline snapshot + diff helpers for instance rebuild regression checks."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

from femic.patchworks_runtime import (
    infer_patchworks_model_dir,
    load_patchworks_runtime_config,
)

DEFAULT_BASELINE_RELATIVE_PATH = Path("config/rebuild.baseline.json")
DEFAULT_TRACK_TABLES: tuple[str, ...] = (
    "accounts.csv",
    "blocks.csv",
    "curves.csv",
    "features.csv",
    "products.csv",
    "strata.csv",
    "tracknames.csv",
    "treatments.csv",
)


def resolve_baseline_path(
    *,
    baseline_path: Path | None,
    instance_root: Path,
) -> Path:
    """Resolve baseline path against instance root when relative."""

    candidate = baseline_path or DEFAULT_BASELINE_RELATIVE_PATH
    if candidate.is_absolute():
        return candidate
    return (instance_root / candidate).resolve()


def build_current_snapshot(
    *,
    patchworks_config_path: Path,
) -> dict[str, Any]:
    """Build normalized snapshot payload for key track/XML structures."""

    config = load_patchworks_runtime_config(patchworks_config_path)
    model_dir = infer_patchworks_model_dir(config)
    tracks_dir = config.matrix_output_dir
    forestmodel_xml_path = config.forestmodel_xml_path

    track_tables: dict[str, dict[str, Any]] = {}
    for table_name in DEFAULT_TRACK_TABLES:
        path = tracks_dir / table_name
        if not path.exists():
            continue
        track_tables[table_name] = {
            "path": str(path),
            "sha256": _file_sha256(path),
            "row_count": _csv_row_count(path),
        }

    xml_summary: dict[str, Any] = {
        "path": str(forestmodel_xml_path),
        "exists": forestmodel_xml_path.exists(),
    }
    if forestmodel_xml_path.exists():
        xml_summary.update(_forestmodel_structure_counts(forestmodel_xml_path))

    return {
        "schema_version": "1.0",
        "model_dir": str(model_dir),
        "tracks_dir": str(tracks_dir),
        "forestmodel_xml": xml_summary,
        "track_tables": track_tables,
    }


def load_snapshot(path: Path) -> dict[str, Any]:
    """Load a baseline snapshot JSON payload."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Baseline snapshot must be a JSON object: {path}")
    return payload


def save_snapshot(*, path: Path, snapshot: dict[str, Any]) -> None:
    """Persist snapshot JSON payload (creating parent directories if needed)."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")


def diff_snapshots(
    *,
    baseline: dict[str, Any],
    current: dict[str, Any],
) -> dict[str, Any]:
    """Return structural diff summary between baseline and current snapshots."""

    baseline_tables = _as_mapping(baseline.get("track_tables"))
    current_tables = _as_mapping(current.get("track_tables"))
    table_names = sorted(set(baseline_tables).union(current_tables))

    table_diffs: list[dict[str, Any]] = []
    for table_name in table_names:
        before = _as_mapping(baseline_tables.get(table_name))
        after = _as_mapping(current_tables.get(table_name))
        if not before:
            table_diffs.append(
                {
                    "table": table_name,
                    "status": "added",
                    "before": None,
                    "after": after,
                }
            )
            continue
        if not after:
            table_diffs.append(
                {
                    "table": table_name,
                    "status": "removed",
                    "before": before,
                    "after": None,
                }
            )
            continue
        changed = before.get("sha256") != after.get("sha256") or before.get(
            "row_count"
        ) != after.get("row_count")
        if changed:
            table_diffs.append(
                {
                    "table": table_name,
                    "status": "changed",
                    "before": before,
                    "after": after,
                }
            )

    baseline_xml = _as_mapping(baseline.get("forestmodel_xml"))
    current_xml = _as_mapping(current.get("forestmodel_xml"))
    xml_changed_keys = []
    for key in ("curve_count", "attribute_count", "select_count", "treatment_count"):
        if baseline_xml.get(key) != current_xml.get(key):
            xml_changed_keys.append(key)
    xml_diff: dict[str, Any] = {
        "status": "unchanged",
        "changed_keys": [],
    }
    if xml_changed_keys:
        xml_diff = {
            "status": "changed",
            "changed_keys": xml_changed_keys,
            "before": {key: baseline_xml.get(key) for key in xml_changed_keys},
            "after": {key: current_xml.get(key) for key in xml_changed_keys},
        }

    return {
        "table_diffs": table_diffs,
        "xml_diff": xml_diff,
        "diff_count": len(table_diffs) + (1 if xml_diff["status"] == "changed" else 0),
        "baseline_match": len(table_diffs) == 0 and xml_diff["status"] == "unchanged",
    }


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _csv_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            next(reader)
        except StopIteration:
            return 0
        return sum(1 for _ in reader)


def _forestmodel_structure_counts(path: Path) -> dict[str, int]:
    root = ET.parse(path).getroot()
    return {
        "curve_count": len(root.findall(".//curve")),
        "attribute_count": len(root.findall(".//attribute")),
        "select_count": len(root.findall(".//select")),
        "treatment_count": len(root.findall(".//treatment")),
    }
