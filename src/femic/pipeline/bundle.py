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


@dataclass(frozen=True)
class BundleAssemblyResult:
    """Assembled model-input bundle tables and missing-mapping diagnostics."""

    au_table: Any
    curve_table: Any
    curve_points_table: Any
    missing_au_curve_mappings: Any


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


def build_bundle_tables_from_curves(
    *,
    tsa_list: list[str],
    vdyp_curves_smooth: dict[str, Any],
    tipsy_curves: dict[str, Any],
    scsi_au: dict[str, dict[tuple[str, str], int]],
    canfi_species_fn: Callable[[str], int],
    pd_module: Any,
    message_fn: Callable[[str], Any] = print,
) -> BundleAssemblyResult:
    """Build AU/curve tables from per-TSA VDYP and TIPSY curve outputs."""
    au_table_data: dict[str, list[Any]] = {
        "au_id": [],
        "tsa": [],
        "stratum_code": [],
        "si_level": [],
        "canfi_species": [],
        "unmanaged_curve_id": [],
        "managed_curve_id": [],
    }
    curve_table_data: dict[str, list[Any]] = {"curve_id": [], "curve_type": []}
    curve_points_table_data: dict[str, list[Any]] = {"curve_id": [], "x": [], "y": []}
    missing_au_curve_mappings: list[dict[str, Any]] = []

    for tsa in tsa_list:
        message_fn(str(tsa))
        vdyp_curves_tsa = vdyp_curves_smooth[tsa].set_index(
            ["stratum_code", "si_level"]
        )
        tipsy_curves_tsa = tipsy_curves[tsa].reset_index().set_index("AU")
        tipsy_curve_ids = set(tipsy_curves_tsa.index.unique())
        for stratum_code, si_level in list(vdyp_curves_tsa.index.unique()):
            scsi_key = (str(stratum_code), str(si_level))
            au_id_ = scsi_au.get(tsa, {}).get(scsi_key)
            if au_id_ is None:
                missing_au_curve_mappings.append(
                    {"tsa": tsa, "stratum_code": stratum_code, "si_level": si_level}
                )
                continue
            tipsy_curve_id = 20000 + au_id_
            is_managed_au = tipsy_curve_id in tipsy_curve_ids
            au_id = 100000 * int(tsa) + au_id_
            unmanaged_curve_id = au_id
            managed_curve_id = au_id + 20000 if is_managed_au else unmanaged_curve_id
            au_table_data["au_id"].append(au_id)
            au_table_data["tsa"].append(tsa)
            au_table_data["stratum_code"].append(stratum_code)
            au_table_data["si_level"].append(si_level)
            au_table_data["canfi_species"].append(canfi_species_fn(stratum_code))
            au_table_data["unmanaged_curve_id"].append(unmanaged_curve_id)
            curve_table_data["curve_id"].append(unmanaged_curve_id)
            curve_table_data["curve_type"].append("unmanaged")
            vdyp_curve = vdyp_curves_tsa.loc[(stratum_code, si_level)]
            for x, y in zip(vdyp_curve.age, vdyp_curve.volume):
                curve_points_table_data["curve_id"].append(unmanaged_curve_id)
                curve_points_table_data["x"].append(int(x))
                curve_points_table_data["y"].append(round(y, 2))
            au_table_data["managed_curve_id"].append(managed_curve_id)
            if is_managed_au:
                curve_table_data["curve_id"].append(managed_curve_id)
                curve_table_data["curve_type"].append("managed")
                tipsy_curve = tipsy_curves_tsa.loc[tipsy_curve_id]
                for x, y in zip(tipsy_curve.Age, tipsy_curve.Yield):
                    curve_points_table_data["curve_id"].append(managed_curve_id)
                    curve_points_table_data["x"].append(int(x))
                    curve_points_table_data["y"].append(round(y, 2))

    return BundleAssemblyResult(
        au_table=pd_module.DataFrame(au_table_data),
        curve_table=pd_module.DataFrame(curve_table_data),
        curve_points_table=pd_module.DataFrame(curve_points_table_data),
        missing_au_curve_mappings=pd_module.DataFrame(missing_au_curve_mappings),
    )
