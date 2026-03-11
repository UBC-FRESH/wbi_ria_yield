#!/usr/bin/env python
"""Rebuild and verify the K3Z Patchworks instance deterministically.

This script codifies the known-valid rebuild sequence and enforces regression
invariants so unexpected behavior changes fail fast.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import geopandas as gpd
import pandas as pd
import yaml

REQUIRED_NONZERO_MANAGED_SPECIES = ("BA", "CW", "DR", "FDC", "HW", "SS", "YC")
KEY_ACCOUNT_NAMES = (
    "product.Yield.managed.Total",
    "product.HarvestedVolume.managed.Total.CC",
    "product.Yield.managed.FDC",
    "product.HarvestedVolume.managed.FDC.CC",
    "feature.Seral.regenerating",
    "feature.Seral.young",
    "feature.Seral.immature",
    "feature.Seral.mature",
    "feature.Seral.overmature",
    "product.Seral.area.regenerating.985501000.CC",
    "product.Seral.area.young.985501000.CC",
    "product.Seral.area.immature.985501000.CC",
    "product.Seral.area.mature.985501000.CC",
    "product.Seral.area.overmature.985501000.CC",
)
TRACKS_TABLES = (
    "blocks.csv",
    "curves.csv",
    "treatments.csv",
    "features.csv",
    "products.csv",
    "tracknames.csv",
    "strata.csv",
    "accounts.csv",
    "protoaccounts.csv",
)


@dataclass
class RebuildReport:
    run_id: str
    instance_root: str
    tipsy_curve_mode: str
    matrix_returncode: int
    managed_area_ha: float
    passive_area_ha: float
    seral_account_count: int
    managed_species_max_y: dict[str, float]
    harvested_species_max_y: dict[str, float]
    block_join_intersection: int
    block_join_csv_only: int
    block_join_shp_only: int
    tracks_row_counts: dict[str, int]
    account_count: int
    key_accounts_present: dict[str, bool]
    artifact_timestamps_utc: dict[str, str]
    baseline_path: str | None
    baseline_match: bool | None
    baseline_differences: list[str]
    checks_passed: bool
    failures: list[str]


def _repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def _import_femic_modules(repo_root: Path) -> dict[str, Any]:
    src = repo_root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))

    from femic.pipeline.bundle import tsa_curve_id_prefix
    from femic.pipeline.managed_curves import build_transformed_managed_curves_for_tsa
    from femic.fmg.patchworks import (
        _source_curve_ref,
        build_forestmodel_xml_tree,
        validate_forestmodel_xml_tree,
        write_forestmodel_xml,
    )

    return {
        "tsa_curve_id_prefix": tsa_curve_id_prefix,
        "build_transformed_managed_curves_for_tsa": build_transformed_managed_curves_for_tsa,
        "_source_curve_ref": _source_curve_ref,
        "build_forestmodel_xml_tree": build_forestmodel_xml_tree,
        "validate_forestmodel_xml_tree": validate_forestmodel_xml_tree,
        "write_forestmodel_xml": write_forestmodel_xml,
    }


def _run_cmd(*, cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=False)


def _backup_file(path: Path, stamp: str) -> Path:
    backup = path.with_name(path.stem + f"_backup_{stamp}" + path.suffix)
    backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return backup


def _parse_managed_and_passive_area(stderr_text: str) -> tuple[float, float]:
    managed_match = re.search(r"^Managed\s*:\s*([0-9.]+)", stderr_text, flags=re.MULTILINE)
    passive_match = re.search(r"^Passive\s*:\s*([0-9.]+)", stderr_text, flags=re.MULTILINE)
    managed = float(managed_match.group(1)) if managed_match else 0.0
    passive = float(passive_match.group(1)) if passive_match else 0.0
    return managed, passive


def _series_from_products(
    *, products: pd.DataFrame, curves: pd.DataFrame, label_prefix: str, suffix_filter: str | None
) -> dict[str, float]:
    curve_max = curves.groupby("CURVE")["Y"].max()
    sub = products[products["LABEL"].astype(str).str.startswith(label_prefix)].copy()
    if suffix_filter is not None:
        sub = sub[sub["LABEL"].astype(str).str.endswith(suffix_filter)]
    sub["max_y"] = sub["CURVE"].map(curve_max).fillna(0.0)

    out: dict[str, float] = {}
    for label, max_y in sub.groupby("LABEL")["max_y"].max().items():
        species = str(label).split(".")[-1]
        if species == "CC":
            species = str(label).split(".")[-2]
        out[species] = float(max_y)
    return out


def _read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _collect_tracks_row_counts(*, tracks_dir: Path) -> dict[str, int]:
    row_counts: dict[str, int] = {}
    for name in TRACKS_TABLES:
        table_path = tracks_dir / name
        if not table_path.exists():
            row_counts[name] = -1
            continue
        frame = pd.read_csv(table_path)
        row_counts[name] = int(len(frame))
    return row_counts


def _collect_key_account_presence(*, accounts: pd.DataFrame) -> dict[str, bool]:
    values = set(accounts["ACCOUNT"].astype(str).tolist())
    return {name: (name in values) for name in KEY_ACCOUNT_NAMES}


def _to_utc_iso(path: Path) -> str:
    if not path.exists():
        return "missing"
    stamp = datetime.fromtimestamp(path.stat().st_mtime, UTC)
    return stamp.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _collect_artifact_timestamps(*, instance_root: Path, run_id: str) -> dict[str, str]:
    tracks_dir = instance_root / "models" / "k3z_patchworks_model" / "tracks"
    logs_dir = instance_root / "vdyp_io" / "logs"
    artifacts = {
        "yield_forestmodel_xml": instance_root
        / "models"
        / "k3z_patchworks_model"
        / "yield"
        / "forestmodel.xml",
        "blocks_shp": instance_root / "models" / "k3z_patchworks_model" / "blocks" / "blocks.shp",
        "topology_csv": instance_root
        / "models"
        / "k3z_patchworks_model"
        / "blocks"
        / "topology_blocks_200r.csv",
        "tracks_accounts_csv": tracks_dir / "accounts.csv",
        "tracks_products_csv": tracks_dir / "products.csv",
        "matrix_manifest_json": logs_dir / f"patchworks_matrixbuilder_manifest-{run_id}.json",
        "matrix_stderr_log": logs_dir / f"patchworks_matrixbuilder_stderr-{run_id}.log",
        "matrix_stdout_log": logs_dir / f"patchworks_matrixbuilder_stdout-{run_id}.log",
    }
    return {name: _to_utc_iso(path) for name, path in artifacts.items()}


def _compare_observed_with_baseline(
    *,
    observed_row_counts: dict[str, int],
    observed_account_count: int,
    observed_key_presence: dict[str, bool],
    baseline_payload: dict[str, Any],
) -> list[str]:
    differences: list[str] = []
    baseline_row_counts = baseline_payload.get("tracks_row_counts", {})
    for name, expected in baseline_row_counts.items():
        actual = observed_row_counts.get(str(name))
        if int(actual) != int(expected):
            differences.append(f"row-count mismatch for {name}: actual={actual} expected={expected}")

    expected_account_count = baseline_payload.get("account_count")
    if expected_account_count is not None and int(observed_account_count) != int(expected_account_count):
        differences.append(
            "account-count mismatch: "
            f"actual={observed_account_count} expected={int(expected_account_count)}"
        )

    baseline_key_presence = baseline_payload.get("key_accounts_present", {})
    for name, expected in baseline_key_presence.items():
        actual = bool(observed_key_presence.get(str(name), False))
        if actual != bool(expected):
            differences.append(
                f"key-account presence mismatch for {name}: actual={actual} expected={bool(expected)}"
            )
    return differences


def rebuild_k3z_instance(
    *,
    repo_root: Path,
    instance_root: Path,
    run_id: str,
    baseline_path: Path | None,
    write_baseline: bool,
) -> RebuildReport:
    modules = _import_femic_modules(repo_root=repo_root)
    tsa_curve_id_prefix = modules["tsa_curve_id_prefix"]
    build_transformed = modules["build_transformed_managed_curves_for_tsa"]
    source_curve_ref = modules["_source_curve_ref"]
    build_forestmodel = modules["build_forestmodel_xml_tree"]
    validate_forestmodel = modules["validate_forestmodel_xml_tree"]
    write_forestmodel = modules["write_forestmodel_xml"]

    failures: list[str] = []
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    run_profile_path = instance_root / "config" / "run_profile.k3z.yaml"
    runtime_config_path = instance_root / "config" / "patchworks.runtime.windows.yaml"
    seral_config_path = instance_root / "config" / "seral.k3z.yaml"

    run_profile = yaml.safe_load(run_profile_path.read_text(encoding="utf-8")) or {}
    modes = run_profile.get("modes", {}) if isinstance(run_profile, dict) else {}
    managed_curve_mode = str(modes.get("managed_curve_mode", "")).strip().lower()
    if managed_curve_mode != "vdyp_transform":
        failures.append(
            f"run profile managed_curve_mode must be vdyp_transform, found {managed_curve_mode!r}"
        )

    x_scale = float(modes.get("managed_curve_x_scale", 0.8))
    y_scale = float(modes.get("managed_curve_y_scale", 1.2))
    max_age = int(modes.get("managed_curve_max_age", 300))
    truncate = bool(modes.get("managed_curve_truncate_at_culm", True))

    bundle_dir = instance_root / "data" / "model_input_bundle"
    au_table = pd.read_csv(bundle_dir / "au_table.csv")
    curve_table = pd.read_csv(bundle_dir / "curve_table.csv")
    curve_points = pd.read_csv(bundle_dir / "curve_points_table.csv")

    tsa = "k3z"
    prefix = tsa_curve_id_prefix(tsa)
    au_scsi_map: dict[int, tuple[str, str]] = {}
    managed_curve_by_au: dict[int, int] = {}
    for row in au_table[au_table["tsa"].astype(str).str.lower() == tsa].itertuples(index=False):
        au_id = int(row.au_id)
        au_base = au_id - int(prefix) * 100000
        au_scsi_map[int(au_base)] = (str(row.stratum_code), str(row.si_level))
        managed_curve_by_au[int(au_base)] = int(row.managed_curve_id)

    vdyp = pd.read_feather(instance_root / "data" / "vdyp_curves_smooth-tsak3z.feather")
    vdyp_by_scsi = vdyp.sort_values(["stratum_code", "si_level", "age"]).set_index(
        ["stratum_code", "si_level"]
    )

    tipsy_curves_path = instance_root / "data" / "tipsy_curves_tsak3z.csv"
    tipsy_curves = pd.read_csv(tipsy_curves_path)
    au_values = sorted(set(tipsy_curves["AU"].astype(int).tolist()))
    transformed = build_transformed(
        tsa=tsa,
        au_values=au_values,
        au_scsi={tsa: au_scsi_map},
        vdyp_curves_by_scsi=vdyp_by_scsi,
        x_scale=x_scale,
        y_scale=y_scale,
        max_age=max_age,
        truncate_after_culmination=truncate,
    )
    if transformed.empty:
        failures.append("vdyp_transform yielded no managed curve rows")

    _backup_file(tipsy_curves_path, stamp)
    transformed.to_csv(tipsy_curves_path, index=False)

    # Update managed total curves in bundle curve points.
    managed_ids = set(int(v) for v in au_table["managed_curve_id"].tolist())
    curve_points_updated = curve_points[
        ~curve_points["curve_id"].astype(int).isin(managed_ids)
    ].copy()
    managed_rows: list[dict[str, int | float]] = []
    for row in transformed.itertuples(index=False):
        au_val = int(row.AU)
        managed_curve_id = managed_curve_by_au.get(au_val)
        if managed_curve_id is None:
            managed_curve_id = managed_curve_by_au.get(int(str(au_val)[-4:]))
        if managed_curve_id is None:
            continue
        managed_rows.append(
            {
                "curve_id": int(managed_curve_id),
                "x": int(row.Age),
                "y": round(float(row.Yield), 6),
            }
        )
    if not managed_rows:
        failures.append("no managed curve rows were mapped into bundle curve_points_table")

    curve_points_updated = pd.concat(
        [curve_points_updated, pd.DataFrame(managed_rows)], ignore_index=True
    ).sort_values(["curve_id", "x"])

    # Ensure every curve_table id has at least one curve_points row.
    ct_ids = set(curve_table["curve_id"].astype(int).tolist())
    cp_ids = set(curve_points_updated["curve_id"].astype(int).tolist())
    missing_ids = sorted(ct_ids - cp_ids)
    if missing_ids:
        xml_path = instance_root / "models" / "k3z_patchworks_model" / "yield" / "forestmodel.xml"
        import xml.etree.ElementTree as et

        xml_root = et.parse(xml_path).getroot()
        xml_curve_points: dict[str, list[tuple[int, float]]] = {}
        for curve in xml_root.findall(".//curve"):
            cid = curve.get("id")
            if not cid:
                continue
            pts: list[tuple[int, float]] = []
            for point in curve.findall("./point"):
                x = point.get("x")
                y = point.get("y")
                if x is None or y is None:
                    continue
                pts.append((int(float(x)), float(y)))
            if pts:
                xml_curve_points[cid] = pts

        recovered: list[dict[str, int | float]] = []
        for row in curve_table[curve_table["curve_id"].astype(int).isin(missing_ids)].itertuples(
            index=False
        ):
            cid = int(row.curve_id)
            cref = source_curve_ref(curve_id=cid, curve_type=str(row.curve_type))
            for x, y in xml_curve_points.get(cref, []):
                recovered.append({"curve_id": cid, "x": x, "y": round(float(y), 6)})
        if recovered:
            curve_points_updated = pd.concat(
                [curve_points_updated, pd.DataFrame(recovered)], ignore_index=True
            ).sort_values(["curve_id", "x"])

    # Persist bundle curve points update.
    cp_path = bundle_dir / "curve_points_table.csv"
    _backup_file(cp_path, stamp)
    curve_points_updated.to_csv(cp_path, index=False)

    # Rebuild forestmodel with seral stages enabled.
    seral_cfg = yaml.safe_load(seral_config_path.read_text(encoding="utf-8")) or {}
    yield_xml = instance_root / "models" / "k3z_patchworks_model" / "yield" / "forestmodel.xml"
    output_xml = instance_root / "output" / "patchworks_k3z_validated" / "forestmodel.xml"

    import xml.etree.ElementTree as et

    root_old = et.parse(yield_xml).getroot()
    start_year = int(root_old.get("year", "2026"))
    horizon_years = int(root_old.get("horizon", "300"))

    root_new = build_forestmodel(
        au_table=au_table,
        curve_table=curve_table,
        curve_points_table=curve_points_updated,
        start_year=start_year,
        horizon_years=horizon_years,
        seral_stage_config=seral_cfg,
    )
    validate_forestmodel(root=root_new)

    _backup_file(yield_xml, stamp)
    _backup_file(output_xml, stamp)
    write_forestmodel(root=root_new, path=yield_xml)
    write_forestmodel(root=root_new, path=output_xml)

    # Rebuild blocks + matrix with femic CLI.
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")

    preflight = subprocess.run(
        [sys.executable, "-m", "femic", "patchworks", "preflight", "--config", str(runtime_config_path), "--instance-root", str(instance_root)],
        cwd=str(repo_root),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if preflight.returncode != 0:
        failures.append(f"patchworks preflight failed: {preflight.stderr.strip()}")

    blocks = subprocess.run(
        [
            sys.executable,
            "-m",
            "femic",
            "patchworks",
            "build-blocks",
            "--config",
            str(runtime_config_path),
            "--instance-root",
            str(instance_root),
            "--topology-radius",
            "200",
        ],
        cwd=str(repo_root),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if blocks.returncode != 0:
        failures.append(f"patchworks build-blocks failed: {blocks.stderr.strip()}")

    matrix = subprocess.run(
        [
            sys.executable,
            "-m",
            "femic",
            "patchworks",
            "matrix-build",
            "--config",
            str(runtime_config_path),
            "--instance-root",
            str(instance_root),
            "--run-id",
            run_id,
        ],
        cwd=str(repo_root),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    # Post-run invariant checks.
    tracks_dir = instance_root / "models" / "k3z_patchworks_model" / "tracks"
    products = pd.read_csv(tracks_dir / "products.csv")
    curves = pd.read_csv(tracks_dir / "curves.csv")
    accounts = pd.read_csv(tracks_dir / "accounts.csv")
    tracks_row_counts = _collect_tracks_row_counts(tracks_dir=tracks_dir)
    key_accounts_present = _collect_key_account_presence(accounts=accounts)

    managed_species = _series_from_products(
        products=products,
        curves=curves,
        label_prefix="product.Yield.managed.",
        suffix_filter=None,
    )
    managed_species.pop("Total", None)

    harvested_species = _series_from_products(
        products=products,
        curves=curves,
        label_prefix="product.HarvestedVolume.managed.",
        suffix_filter=".CC",
    )
    harvested_species.pop("Total", None)

    for species in REQUIRED_NONZERO_MANAGED_SPECIES:
        if float(managed_species.get(species, 0.0)) <= 0.0:
            failures.append(f"managed species yield is zero for required species {species}")

    seral_accounts = accounts[
        accounts["ACCOUNT"].astype(str).str.startswith("feature.Seral.")
        | accounts["ACCOUNT"].astype(str).str.startswith("product.Seral.area.")
    ]
    if seral_accounts.empty:
        failures.append("seral accounts missing from tracks/accounts.csv")

    blocks_csv = pd.read_csv(tracks_dir / "blocks.csv")
    blocks_shp = gpd.read_file(instance_root / "models" / "k3z_patchworks_model" / "blocks" / "blocks.shp")
    csv_ids = set(pd.to_numeric(blocks_csv["BLOCK"], errors="coerce").dropna().astype(int))
    shp_ids = set(pd.to_numeric(blocks_shp["BLOCK"], errors="coerce").dropna().astype(int))
    if len(csv_ids - shp_ids) > 0 or len(shp_ids - csv_ids) > 0:
        failures.append(
            "block join mismatch between tracks/blocks.csv and model blocks shapefile"
        )

    log_path = instance_root / "vdyp_io" / "logs" / f"patchworks_matrixbuilder_stderr-{run_id}.log"
    stderr_text = _read_text_if_exists(log_path)
    managed_area, passive_area = _parse_managed_and_passive_area(stderr_text)
    if managed_area <= 0.0:
        failures.append("managed area parsed from matrix stderr is zero")

    baseline_differences: list[str] = []
    baseline_match: bool | None = None
    baseline_path_resolved: Path | None = baseline_path.resolve() if baseline_path else None

    baseline_payload = {
        "run_id": run_id,
        "generated_utc": datetime.now(UTC).replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        ),
        "tracks_row_counts": tracks_row_counts,
        "account_count": int(len(accounts)),
        "key_accounts_present": key_accounts_present,
    }
    if write_baseline:
        if baseline_path_resolved is None:
            failures.append("cannot write baseline: baseline path not provided")
        else:
            baseline_path_resolved.parent.mkdir(parents=True, exist_ok=True)
            baseline_path_resolved.write_text(
                json.dumps(baseline_payload, indent=2),
                encoding="utf-8",
            )
            baseline_match = True
    elif baseline_path_resolved is not None and baseline_path_resolved.exists():
        expected = json.loads(baseline_path_resolved.read_text(encoding="utf-8"))
        baseline_differences = _compare_observed_with_baseline(
            observed_row_counts=tracks_row_counts,
            observed_account_count=int(len(accounts)),
            observed_key_presence=key_accounts_present,
            baseline_payload=expected,
        )
        baseline_match = len(baseline_differences) == 0
        if baseline_differences:
            failures.append(
                "baseline differences detected; see baseline_differences in rebuild report"
            )
    elif baseline_path_resolved is not None:
        failures.append(
            f"baseline file missing: {baseline_path_resolved} "
            "(run with --write-baseline to initialize)"
        )

    artifact_timestamps = _collect_artifact_timestamps(
        instance_root=instance_root,
        run_id=run_id,
    )

    report = RebuildReport(
        run_id=run_id,
        instance_root=str(instance_root),
        tipsy_curve_mode=managed_curve_mode,
        matrix_returncode=int(matrix.returncode),
        managed_area_ha=float(managed_area),
        passive_area_ha=float(passive_area),
        seral_account_count=int(len(seral_accounts)),
        managed_species_max_y={k: float(v) for k, v in sorted(managed_species.items())},
        harvested_species_max_y={k: float(v) for k, v in sorted(harvested_species.items())},
        block_join_intersection=int(len(csv_ids & shp_ids)),
        block_join_csv_only=int(len(csv_ids - shp_ids)),
        block_join_shp_only=int(len(shp_ids - csv_ids)),
        tracks_row_counts=tracks_row_counts,
        account_count=int(len(accounts)),
        key_accounts_present=key_accounts_present,
        artifact_timestamps_utc=artifact_timestamps,
        baseline_path=str(baseline_path_resolved) if baseline_path_resolved else None,
        baseline_match=baseline_match,
        baseline_differences=baseline_differences,
        checks_passed=(len(failures) == 0 and matrix.returncode == 0),
        failures=failures,
    )

    report_path = instance_root / "vdyp_io" / "logs" / f"k3z_rebuild_report-{run_id}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")

    if matrix.returncode != 0:
        raise SystemExit(
            f"matrix-build failed (run_id={run_id}). See {report_path} and matrix logs."
        )
    if failures:
        raise SystemExit(
            f"rebuild checks failed ({len(failures)} issue(s)). See {report_path}."
        )

    print(f"K3Z rebuild succeeded. Report: {report_path}")

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--instance-root",
        type=Path,
        default=Path("external/femic-k3z-instance"),
        help="Path to K3Z instance root (default: external/femic-k3z-instance)",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=f"k3z_rebuild_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        help="Run id used for matrix-builder and report logs.",
    )
    parser.add_argument(
        "--baseline-json",
        type=Path,
        default=Path("scripts/k3z/k3z_tracks_baseline.json"),
        help="Path to baseline JSON used for structural regression checks.",
    )
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="Write the baseline JSON from current observed tracks summary.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    repo_root = _repo_root_from_script()
    instance_root = (repo_root / args.instance_root).resolve()
    baseline_path = (repo_root / args.baseline_json).resolve()
    rebuild_k3z_instance(
        repo_root=repo_root,
        instance_root=instance_root,
        run_id=args.run_id,
        baseline_path=baseline_path,
        write_baseline=bool(args.write_baseline),
    )


if __name__ == "__main__":
    main()
