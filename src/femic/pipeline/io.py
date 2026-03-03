"""I/O-oriented helpers shared across pipeline entrypoints."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import tomllib
from typing import Iterable, Mapping
import uuid

import yaml


DEFAULT_DEV_CONFIG_PATH = Path("config/dev.toml")
FALLBACK_DEFAULT_TSA_LIST = ["08"]
DEFAULT_RUN_CONFIG_PATH = Path("config/run_profile.yaml")


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
class PipelineRunProfile:
    """Config-file driven run profile for selecting TSAs/strata and mode flags."""

    tsa_list: list[str] | None = None
    strata_list: list[str] | None = None
    resume: bool = False
    dry_run: bool = False
    verbose: bool = False
    skip_checks: bool = False
    debug_rows: int | None = None
    run_id: str | None = None
    log_dir: Path | None = None


@dataclass(frozen=True)
class EffectiveRunOptions:
    """Resolved run options after merging CLI values with optional profile config."""

    tsa_list: list[str]
    strata_list: list[str]
    resume: bool
    dry_run: bool
    verbose: bool
    skip_checks: bool
    debug_rows: int | None
    run_id: str | None
    log_dir: Path


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


@dataclass(frozen=True)
class LegacyExternalDataPaths:
    """Resolved external source roots consumed by legacy 00_data-prep."""

    external_data_root: Path
    vri_vclr1p_path: Path
    tsa_boundaries_path: Path


def resolve_legacy_external_data_paths(
    *,
    repo_root: str | Path,
    env_override: str | None = None,
    required_vri_rel: str | Path = "bc/vri/2019/VEG_COMP_LYR_R1_POLY.gdb",
    tsa_boundaries_rel: str | Path = "bc/tsa/FADM_TSA.gdb",
) -> LegacyExternalDataPaths:
    """Resolve legacy external data root + canonical VRI/TSA source paths."""
    root = Path(repo_root)
    candidates = [
        Path(env_override) if env_override else None,
        root / "data",
        root / ".." / "data",
        Path.home() / "data",
    ]
    resolved_candidates = [candidate.resolve() for candidate in candidates if candidate]
    required_vri_path = Path(required_vri_rel)

    external_data_root = resolved_candidates[0]
    for candidate in resolved_candidates:
        if (candidate / required_vri_path).exists():
            external_data_root = candidate
            break

    return LegacyExternalDataPaths(
        external_data_root=external_data_root,
        vri_vclr1p_path=external_data_root / required_vri_path,
        tsa_boundaries_path=external_data_root / Path(tsa_boundaries_rel),
    )


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


def _normalize_optional_str_list(value: object, *, field_name: str) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")
    return [str(item) for item in value]


def _normalize_optional_bool(value: object, *, field_name: str) -> bool:
    if value is None:
        return False
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _normalize_optional_int(value: object, *, field_name: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer")
    return value


def _normalize_optional_path(value: object, *, field_name: str) -> Path | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string path")
    return Path(value)


def _normalize_optional_str(value: object, *, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    return value


def load_pipeline_run_profile(config_path: Path) -> PipelineRunProfile:
    """Load YAML/JSON run profile used to seed CLI options."""
    if not config_path.exists():
        raise FileNotFoundError(f"Run config not found: {config_path}")
    suffix = config_path.suffix.lower()
    raw_text = config_path.read_text(encoding="utf-8")
    if suffix == ".json":
        parsed = json.loads(raw_text)
    elif suffix in {".yaml", ".yml"}:
        parsed = yaml.safe_load(raw_text)
    else:
        raise ValueError(f"Unsupported run config format: {config_path}")
    if parsed is None:
        parsed = {}
    if not isinstance(parsed, dict):
        raise ValueError("Run config root must be a mapping")

    selection = parsed.get("selection", {})
    if selection is None:
        selection = {}
    if not isinstance(selection, dict):
        raise ValueError("selection must be a mapping")

    modes = parsed.get("modes", {})
    if modes is None:
        modes = {}
    if not isinstance(modes, dict):
        raise ValueError("modes must be a mapping")

    run = parsed.get("run", {})
    if run is None:
        run = {}
    if not isinstance(run, dict):
        raise ValueError("run must be a mapping")

    return PipelineRunProfile(
        tsa_list=_normalize_optional_str_list(
            selection.get("tsa"), field_name="selection.tsa"
        ),
        strata_list=_normalize_optional_str_list(
            selection.get("strata"), field_name="selection.strata"
        ),
        resume=_normalize_optional_bool(modes.get("resume"), field_name="modes.resume"),
        dry_run=_normalize_optional_bool(
            modes.get("dry_run"), field_name="modes.dry_run"
        ),
        verbose=_normalize_optional_bool(
            modes.get("verbose"), field_name="modes.verbose"
        ),
        skip_checks=_normalize_optional_bool(
            modes.get("skip_checks"), field_name="modes.skip_checks"
        ),
        debug_rows=_normalize_optional_int(
            modes.get("debug_rows"), field_name="modes.debug_rows"
        ),
        run_id=_normalize_optional_str(run.get("run_id"), field_name="run.run_id"),
        log_dir=_normalize_optional_path(run.get("log_dir"), field_name="run.log_dir"),
    )


def resolve_effective_run_options(
    *,
    tsa_list: list[str] | None,
    resume: bool,
    dry_run: bool,
    verbose: bool,
    skip_checks: bool,
    debug_rows: int | None,
    run_id: str | None,
    log_dir: Path,
    profile: PipelineRunProfile | None,
) -> EffectiveRunOptions:
    """Merge CLI run values with profile defaults and normalize for execution."""
    active_profile = profile or PipelineRunProfile()
    merged_tsa = tsa_list if tsa_list else active_profile.tsa_list
    merged_debug_rows = (
        debug_rows if debug_rows is not None else active_profile.debug_rows
    )
    merged_run_id = run_id if run_id is not None else active_profile.run_id
    merged_log_dir = (
        active_profile.log_dir
        if log_dir == Path("vdyp_io/logs") and active_profile.log_dir is not None
        else log_dir
    )
    return EffectiveRunOptions(
        tsa_list=normalize_tsa_list(merged_tsa),
        strata_list=active_profile.strata_list or [],
        resume=resume or active_profile.resume,
        dry_run=dry_run or active_profile.dry_run,
        verbose=verbose or active_profile.verbose,
        skip_checks=skip_checks or active_profile.skip_checks,
        debug_rows=merged_debug_rows,
        run_id=merged_run_id,
        log_dir=Path(merged_log_dir),
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
