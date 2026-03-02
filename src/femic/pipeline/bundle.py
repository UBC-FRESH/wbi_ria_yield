"""Helpers for model-input bundle table pathing and I/O."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(frozen=True)
class BundlePaths:
    """Resolved file paths for model input bundle tables."""

    bundle_dir: Path
    au_table: Path
    curve_table: Path
    curve_points_table: Path


def resolve_bundle_paths(
    *,
    base_dir: str | Path = "data/model_input_bundle",
    ensure_dir: bool = True,
) -> BundlePaths:
    """Resolve canonical model-input bundle table paths."""
    bundle_dir = Path(base_dir)
    if ensure_dir:
        bundle_dir.mkdir(parents=True, exist_ok=True)
    return BundlePaths(
        bundle_dir=bundle_dir,
        au_table=bundle_dir / "au_table.csv",
        curve_table=bundle_dir / "curve_table.csv",
        curve_points_table=bundle_dir / "curve_points_table.csv",
    )


def bundle_tables_ready(*, paths: BundlePaths) -> bool:
    """Return True when all required bundle tables exist."""
    return (
        paths.au_table.is_file()
        and paths.curve_table.is_file()
        and paths.curve_points_table.is_file()
    )


def load_bundle_tables(
    *,
    paths: BundlePaths,
    pd_module: Any,
    normalize_tsa_code_fn: Callable[[Any], str] | None = None,
) -> tuple[Any, Any, Any]:
    """Load bundle tables from CSV paths, optionally normalizing TSA codes."""
    au_table = pd_module.read_csv(paths.au_table)
    curve_table = pd_module.read_csv(paths.curve_table)
    curve_points_table = pd_module.read_csv(paths.curve_points_table)
    if normalize_tsa_code_fn is not None and "tsa" in au_table.columns:
        au_table["tsa"] = au_table["tsa"].apply(normalize_tsa_code_fn)
    return au_table, curve_table, curve_points_table


def write_bundle_tables(
    *,
    paths: BundlePaths,
    au_table: Any,
    curve_table: Any,
    curve_points_table: Any,
) -> None:
    """Persist bundle tables to their canonical CSV locations."""
    au_table.to_csv(paths.au_table)
    curve_table.to_csv(paths.curve_table)
    curve_points_table.to_csv(paths.curve_points_table)


def ensure_scsi_au_from_table(
    *,
    au_table: Any,
    scsi_au: dict[str, dict[tuple[str, str], int]],
    normalize_tsa_code_fn: Callable[[Any], str],
) -> None:
    """Backfill `scsi_au` map from persisted AU table entries."""
    for row in au_table.itertuples(index=False):
        tsa_code = normalize_tsa_code_fn(row.tsa)
        tsa_map = scsi_au.setdefault(tsa_code, {})
        scsi_key = (str(row.stratum_code), str(row.si_level))
        if scsi_key in tsa_map:
            continue
        au_base = int(row.au_id) - 100000 * int(tsa_code)
        tsa_map[scsi_key] = au_base
