"""Legacy workflow wrappers for FEMIC."""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
import pickle
from typing import Any, Callable

import pandas as pd

from femic.pipeline.bundle import (
    build_bundle_tables_from_curves,
    resolve_bundle_paths,
    write_bundle_tables,
)
from femic.pipeline.io import PipelineRunConfig, build_legacy_execution_plan
from femic.pipeline.legacy_runtime import build_legacy_01b_runtime_config
from femic.pipeline.manifest import build_run_manifest_payload, write_manifest
from femic.pipeline.stages import load_legacy_module, run_legacy_subprocess


_LEGACY_NOISE_LINES = {"Error in sys.excepthook:", "Original exception was:"}
_DEFAULT_SI_LEVELS = ("L", "M", "H")
_CANFI_MAP = {
    "AC": 1211,
    "AT": 1201,
    "BL": 304,
    "EP": 1303,
    "FD": 500,
    "FDI": 500,
    "HW": 402,
    "PL": 204,
    "PLI": 204,
    "SB": 101,
    "SE": 104,
    "SW": 105,
    "SX": 100,
    "S": 100,
}


@dataclass(frozen=True)
class PostTipsyBundleResult:
    """Result payload returned by post-TIPSY downstream assembly workflow."""

    tsa_list: list[str]
    au_rows: int
    curve_rows: int
    curve_points_rows: int
    tipsy_curves_paths: list[Path]
    tipsy_sppcomp_paths: list[Path]
    au_table_path: Path
    curve_table_path: Path
    curve_points_table_path: Path


def _default_canfi_species(stratum_code: str) -> int:
    species = str(stratum_code).split("_")[-1].split("+")[0]
    try:
        return _CANFI_MAP[species]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported stratum species for CANFI mapping: {species!r} "
            f"(stratum_code={stratum_code!r})"
        ) from exc


def _build_au_maps_from_results(
    *,
    results_for_tsa: list[tuple[int, str, Any]],
    si_levels: tuple[str, ...] = _DEFAULT_SI_LEVELS,
) -> tuple[dict[tuple[str, str], int], dict[int, tuple[str, str]]]:
    scsi_au_tsa: dict[tuple[str, str], int] = {}
    au_scsi_tsa: dict[int, tuple[str, str]] = {}
    for stratumi, stratum_code, _result in results_for_tsa:
        for idx, si_level in enumerate(si_levels, start=1):
            au_base = 1000 * idx + int(stratumi)
            key = (str(stratum_code), str(si_level))
            scsi_au_tsa[key] = au_base
            au_scsi_tsa[au_base] = key
    return scsi_au_tsa, au_scsi_tsa


def run_post_tipsy_bundle(
    *,
    tsa_list: list[str],
    repo_root: Path | None = None,
    data_root: Path = Path("data"),
    model_input_bundle_dir: Path | None = None,
    run_01b_fn: Callable[..., Any] | None = None,
    canfi_species_fn: Callable[[str], int] = _default_canfi_species,
    message_fn: Callable[[str], Any] = print,
) -> PostTipsyBundleResult:
    """Run downstream 01b + bundle assembly from cached TSA artifacts only."""
    normalized_tsa_list = [str(tsa).zfill(2) for tsa in tsa_list]
    resolved_repo_root = repo_root if repo_root is not None else Path.cwd()

    if run_01b_fn is None:
        module = load_legacy_module(
            script_path=resolved_repo_root / "01b_run-tsa.py",
            module_name="run_tsa_01b_post_tipsy",
        )
        run_01b = getattr(module, "run_tsa", None)
        if not callable(run_01b):
            raise RuntimeError("01b_run-tsa.py does not define callable run_tsa")
    else:
        run_01b = run_01b_fn

    results: dict[str, Any] = {}
    au_scsi: dict[str, Any] = {}
    scsi_au: dict[str, Any] = {}
    vdyp_curves_smooth: dict[str, Any] = {}
    tipsy_curves: dict[str, Any] = {}
    tipsy_curves_paths: list[Path] = []
    tipsy_sppcomp_paths: list[Path] = []

    for tsa in normalized_tsa_list:
        prep_path = data_root / f"vdyp_prep-tsa{tsa}.pkl"
        smooth_path = data_root / f"vdyp_curves_smooth-tsa{tsa}.feather"
        if not prep_path.exists():
            raise FileNotFoundError(f"Missing 01a prep checkpoint: {prep_path}")
        if not smooth_path.exists():
            raise FileNotFoundError(f"Missing smoothed VDYP curves: {smooth_path}")

        with prep_path.open("rb") as fh:
            results_for_tsa = pickle.load(fh)
        results[tsa] = results_for_tsa
        vdyp_curves_smooth[tsa] = pd.read_feather(smooth_path)
        scsi_au[tsa], au_scsi[tsa] = _build_au_maps_from_results(
            results_for_tsa=results_for_tsa
        )

        runtime_config = build_legacy_01b_runtime_config(
            tipsy_params_path_prefix=data_root / "tipsy_params_tsa",
            tipsy_output_root=data_root,
            tipsy_output_filename_template="04_output-tsa{tsa}.out",
        )
        message_fn(f"running 01b for tsa {tsa}")
        run_01b(
            tsa=tsa,
            results=results,
            au_scsi=au_scsi,
            tipsy_curves=tipsy_curves,
            vdyp_curves_smooth=vdyp_curves_smooth,
            runtime_config=runtime_config,
        )
        tipsy_curves_paths.append(data_root / f"tipsy_curves_tsa{tsa}.csv")
        tipsy_sppcomp_paths.append(data_root / f"tipsy_sppcomp_tsa{tsa}.csv")

    bundle_dir = (
        model_input_bundle_dir
        if model_input_bundle_dir is not None
        else (data_root / "model_input_bundle")
    )
    bundle_paths = resolve_bundle_paths(base_dir=bundle_dir, ensure_dir=True)
    bundle = build_bundle_tables_from_curves(
        tsa_list=normalized_tsa_list,
        vdyp_curves_smooth=vdyp_curves_smooth,
        tipsy_curves=tipsy_curves,
        scsi_au=scsi_au,
        canfi_species_fn=canfi_species_fn,
        pd_module=pd,
        message_fn=message_fn,
    )
    write_bundle_tables(
        paths=bundle_paths,
        au_table=bundle.au_table,
        curve_table=bundle.curve_table,
        curve_points_table=bundle.curve_points_table,
    )
    return PostTipsyBundleResult(
        tsa_list=normalized_tsa_list,
        au_rows=int(len(bundle.au_table)),
        curve_rows=int(len(bundle.curve_table)),
        curve_points_rows=int(len(bundle.curve_points_table)),
        tipsy_curves_paths=tipsy_curves_paths,
        tipsy_sppcomp_paths=tipsy_sppcomp_paths,
        au_table_path=bundle_paths.au_table,
        curve_table_path=bundle_paths.curve_table,
        curve_points_table_path=bundle_paths.curve_points_table,
    )


def run_data_prep(
    run_config: PipelineRunConfig,
) -> Path:
    """Run the legacy 00_data-prep.py workflow with explicit run configuration."""

    script_path = Path(__file__).resolve().parents[3] / "00_data-prep.py"
    if not script_path.exists():
        raise FileNotFoundError(f"Expected legacy script at {script_path}")

    execution_plan = build_legacy_execution_plan(
        run_config=run_config,
        script_path=script_path,
        python_executable=sys.executable,
        base_env=os.environ,
    )

    started_at = datetime.now(timezone.utc)
    monotonic_started = time.monotonic()
    write_manifest(
        execution_plan.manifest_path,
        build_run_manifest_payload(
            execution_plan=execution_plan,
            status="started",
            started_at=started_at,
            finished_at=None,
            duration_sec=None,
            exit_code=None,
        ),
    )

    stage_result = run_legacy_subprocess(
        execution_plan=execution_plan,
        drop_lines=_LEGACY_NOISE_LINES,
    )
    finished_at = datetime.now(timezone.utc)
    duration_sec = round(time.monotonic() - monotonic_started, 3)
    write_manifest(
        execution_plan.manifest_path,
        build_run_manifest_payload(
            execution_plan=execution_plan,
            status="ok" if stage_result.exit_code == 0 else "failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=duration_sec,
            exit_code=stage_result.exit_code,
        ),
    )

    if stage_result.exit_code != 0:
        raise RuntimeError(
            "Legacy workflow failed with exit code "
            f"{stage_result.exit_code}: {' '.join(execution_plan.cmd)}"
        )
    return execution_plan.manifest_path
