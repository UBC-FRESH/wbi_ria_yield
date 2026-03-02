"""I/O-oriented helpers shared across pipeline entrypoints."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
import tomllib
from typing import Iterable, Mapping
import uuid


DEFAULT_DEV_CONFIG_PATH = Path("config/dev.toml")
FALLBACK_DEFAULT_TSA_LIST = ["08"]


def load_default_tsa_list(config_path: Path = DEFAULT_DEV_CONFIG_PATH) -> list[str]:
    """Load default TSA list from a dev-facing TOML config file."""
    if not config_path.exists():
        return FALLBACK_DEFAULT_TSA_LIST.copy()
    try:
        parsed = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError:
        return FALLBACK_DEFAULT_TSA_LIST.copy()
    run_cfg = parsed.get("run", {})
    if not isinstance(run_cfg, dict):
        return FALLBACK_DEFAULT_TSA_LIST.copy()
    default_tsa_list = run_cfg.get("default_tsa_list")
    if not isinstance(default_tsa_list, list) or not default_tsa_list:
        return FALLBACK_DEFAULT_TSA_LIST.copy()
    return [str(tsa).zfill(2) for tsa in default_tsa_list]


def normalize_tsa_list(
    tsa_list: Iterable[str] | None, *, default_tsa_list: Iterable[str] | None = None
) -> list[str]:
    """Return zero-padded TSA codes, defaulting to configured dev defaults."""
    if not tsa_list:
        if default_tsa_list is None:
            return load_default_tsa_list()
        return [str(tsa).zfill(2) for tsa in default_tsa_list]
    return [str(tsa).zfill(2) for tsa in tsa_list]


def build_ria_vri_checkpoint_paths(
    *,
    output_root: str | Path = "data",
    count: int = 8,
    stem_prefix: str = "ria_vri_vclr1p_checkpoint",
    suffix: str = ".feather",
) -> dict[int, Path]:
    """Build ordered legacy VRI checkpoint artifact paths."""
    root = Path(output_root)
    return {
        idx: root / f"{stem_prefix}{idx}{suffix}" for idx in range(1, int(count) + 1)
    }


@dataclass(frozen=True)
class RunPaths:
    """Resolved filesystem roots used by the legacy workflow wrapper."""

    repo_root: Path
    script_path: Path
    log_dir: Path


@dataclass(frozen=True)
class PipelineRunConfig:
    """Explicit run configuration passed from CLI into workflow wrappers."""

    tsa_list: list[str]
    resume: bool
    debug_rows: int | None = None
    run_id: str | None = None
    log_dir: Path | None = None


@dataclass(frozen=True)
class LegacyExecutionPlan:
    """Fully resolved execution inputs for legacy subprocess runs."""

    script_path: Path
    run_paths: RunPaths
    run_id: str
    run_uuid: str
    tsa_list: list[str]
    manifest_path: Path
    checkpoint_paths: list[Path]
    env: dict[str, str]
    cmd: list[str]


@dataclass(frozen=True)
class LegacyDataArtifactPaths:
    """Legacy data artifact paths used by 00_data-prep orchestration."""

    ria_stands_path: Path
    vdyp_input_pandl_path: Path
    site_prod_bc_gdb_path: Path
    tsa_boundaries_feather_path: Path
    vri_vclr1p_categorical_columns_path: Path
    ria_vclr1p_feature_tif_path: Path
    siteprod_gdb_path: Path
    siteprod_tmpexport_tif_path_prefix: Path
    siteprod_tif_path: Path
    vdyp_ply_feather_path: Path
    vdyp_lyr_feather_path: Path
    vdyp_results_tsa_pickle_path_prefix: Path
    vdyp_results_pickle_path: Path
    vdyp_curves_smooth_tsa_feather_path_prefix: Path
    vdyp_curves_smooth_feather_path: Path
    tipsy_params_path_prefix: Path
    tipsy_params_columns_path: Path
    model_input_bundle_dir: Path
    misc_thlb_tif_path: Path
    stands_shp_dir: Path


def build_legacy_data_artifact_paths(
    *,
    output_root: str | Path = "data",
) -> LegacyDataArtifactPaths:
    """Build legacy 00_data-prep artifact path payload under one data root."""
    root = Path(output_root)
    return LegacyDataArtifactPaths(
        ria_stands_path=root / "veg_comp_lyr_r1_poly-ria.shp",
        vdyp_input_pandl_path=root / "VEG_COMP_VDYP7_INPUT_POLY_AND_LAYER_2019.gdb",
        site_prod_bc_gdb_path=root / "Site_Prod_BC.gdb",
        tsa_boundaries_feather_path=root / "tsa_boundaries.feather",
        vri_vclr1p_categorical_columns_path=root / "vri_vclr1p_categorical_columns",
        ria_vclr1p_feature_tif_path=root / "ria_vclr1p_feature_raster.tif",
        siteprod_gdb_path=root / "Site_Prod_BC.gdb",
        siteprod_tmpexport_tif_path_prefix=root / "site_prod_bc_",
        siteprod_tif_path=root / "siteprod.tif",
        vdyp_ply_feather_path=root / "vdyp_ply.feather",
        vdyp_lyr_feather_path=root / "vdyp_lyr.feather",
        vdyp_results_tsa_pickle_path_prefix=root / "vdyp_results-tsa",
        vdyp_results_pickle_path=root / "vdyp_results.pkl",
        vdyp_curves_smooth_tsa_feather_path_prefix=root / "vdyp_curves_smooth-tsa",
        vdyp_curves_smooth_feather_path=root / "vdyp_curves_smooth.feather",
        tipsy_params_path_prefix=root / "tipsy_params_tsa",
        tipsy_params_columns_path=root / "tipsy_params_columns",
        model_input_bundle_dir=root / "model_input_bundle",
        misc_thlb_tif_path=root / "misc.thlb.tif",
        stands_shp_dir=root / "shp",
    )


def resolve_run_paths(*, script_path: Path, log_dir: Path | None = None) -> RunPaths:
    repo_root = script_path.parent.resolve()
    return RunPaths(
        repo_root=repo_root,
        script_path=script_path.resolve(),
        log_dir=(log_dir or (repo_root / "vdyp_io" / "logs")).resolve(),
    )


def build_pipeline_run_config(
    *,
    tsa_list: Iterable[str] | None,
    resume: bool,
    debug_rows: int | None = None,
    run_id: str | None = None,
    log_dir: Path | None = None,
) -> PipelineRunConfig:
    """Create normalized pipeline run configuration from CLI inputs."""
    normalized_tsas = normalize_tsa_list(tsa_list)
    return PipelineRunConfig(
        tsa_list=normalized_tsas,
        resume=resume,
        debug_rows=debug_rows,
        run_id=run_id,
        log_dir=log_dir,
    )


def build_legacy_execution_plan(
    *,
    run_config: PipelineRunConfig,
    script_path: Path,
    python_executable: str,
    base_env: Mapping[str, str],
) -> LegacyExecutionPlan:
    """Resolve all command/env/path details needed to execute the legacy script."""
    run_paths = resolve_run_paths(script_path=script_path, log_dir=run_config.log_dir)
    run_id = run_config.run_id or datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    manifest_path = run_paths.log_dir / f"run_manifest-{run_id}.json"
    checkpoint_paths = [
        Path(f"data/vdyp_prep-tsa{tsa}.pkl") for tsa in run_config.tsa_list
    ]

    env = dict(base_env)
    env["FEMIC_TSA_LIST"] = ",".join(run_config.tsa_list)
    env["FEMIC_RESUME"] = "1" if run_config.resume else "0"
    if run_config.debug_rows:
        env["FEMIC_DEBUG_ROWS"] = str(run_config.debug_rows)
    else:
        env.pop("FEMIC_DEBUG_ROWS", None)
    env["FEMIC_RUN_ID"] = run_id
    env["FEMIC_LOG_DIR"] = str(run_paths.log_dir)
    env.setdefault("FEMIC_RUN_UUID", str(uuid.uuid4()))
    run_uuid = env["FEMIC_RUN_UUID"]

    cmd = [python_executable, str(script_path)]
    return LegacyExecutionPlan(
        script_path=script_path,
        run_paths=run_paths,
        run_id=run_id,
        run_uuid=run_uuid,
        tsa_list=run_config.tsa_list,
        manifest_path=manifest_path,
        checkpoint_paths=checkpoint_paths,
        env=env,
        cmd=cmd,
    )
