"""Run-manifest helpers for pipeline/workflow orchestration."""

from __future__ import annotations

from datetime import datetime
from importlib import metadata
import json
from pathlib import Path
import platform

from femic.pipeline.io import LegacyExecutionPlan
from femic.pipeline.vdyp import build_vdyp_log_paths


def write_manifest(path: Path, payload: dict[str, object]) -> None:
    """Write pretty-printed JSON manifest payload to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _safe_version(dist_name: str) -> str | None:
    try:
        return metadata.version(dist_name)
    except metadata.PackageNotFoundError:
        return None


def collect_runtime_versions() -> dict[str, object]:
    """Collect runtime/package versions relevant to reproducibility."""
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "femic": _safe_version("femic"),
        "packages": {
            "numpy": _safe_version("numpy"),
            "pandas": _safe_version("pandas"),
            "geopandas": _safe_version("geopandas"),
            "scipy": _safe_version("scipy"),
            "rasterio": _safe_version("rasterio"),
            "shapely": _safe_version("shapely"),
            "typer": _safe_version("typer"),
            "rich": _safe_version("rich"),
        },
    }


def build_run_manifest_payload(
    *,
    execution_plan: LegacyExecutionPlan,
    status: str,
    started_at: datetime,
    finished_at: datetime | None,
    duration_sec: float | None,
    exit_code: int | None,
) -> dict[str, object]:
    """Build a run manifest payload from a resolved execution plan."""
    log_paths = build_vdyp_log_paths(
        execution_plan.run_paths.log_dir,
        execution_plan.tsa_list,
        execution_plan.run_id,
    )
    output_root = execution_plan.output_root.resolve()
    versioned_output_dir = (output_root / execution_plan.output_version_tag).resolve()
    return {
        "run_id": execution_plan.run_id,
        "run_uuid": execution_plan.run_uuid,
        "status": status,
        "started_at_utc": started_at.isoformat(),
        "finished_at_utc": finished_at.isoformat() if finished_at else None,
        "duration_sec": duration_sec,
        "exit_code": exit_code,
        "command": execution_plan.cmd,
        "script_path": str(execution_plan.script_path),
        "cwd": str(execution_plan.script_path.parent),
        "log_dir": str(execution_plan.run_paths.log_dir),
        "tsa_list": execution_plan.tsa_list,
        "options": {
            "resume": execution_plan.env.get("FEMIC_RESUME") == "1",
            "debug_rows": (
                int(execution_plan.env["FEMIC_DEBUG_ROWS"])
                if "FEMIC_DEBUG_ROWS" in execution_plan.env
                else None
            ),
            "output_root": str(execution_plan.output_root),
        },
        "config_provenance": {
            "run_config_path": (
                str(execution_plan.run_config_path)
                if execution_plan.run_config_path is not None
                else None
            ),
            "run_config_sha256": execution_plan.run_config_sha256,
        },
        "outputs": {
            "output_root": str(output_root),
            "version_tag": execution_plan.output_version_tag,
            "versioned_output_dir": str(versioned_output_dir),
        },
        "env_flags": {
            "FEMIC_DISABLE_IPP": execution_plan.env.get("FEMIC_DISABLE_IPP"),
            "FEMIC_USE_SWIFTER": execution_plan.env.get("FEMIC_USE_SWIFTER"),
            "FEMIC_SKIP_STANDS_SHP": execution_plan.env.get("FEMIC_SKIP_STANDS_SHP"),
            "FEMIC_EXTERNAL_DATA_ROOT": execution_plan.env.get(
                "FEMIC_EXTERNAL_DATA_ROOT"
            ),
            "FEMIC_SAMPLING_SEED": execution_plan.env.get("FEMIC_SAMPLING_SEED"),
        },
        "runtime_parameters": {
            "femic_tsa_list": execution_plan.env.get("FEMIC_TSA_LIST"),
            "femic_resume": execution_plan.env.get("FEMIC_RESUME"),
            "femic_debug_rows": execution_plan.env.get("FEMIC_DEBUG_ROWS"),
            "femic_run_id": execution_plan.env.get("FEMIC_RUN_ID"),
            "femic_log_dir": execution_plan.env.get("FEMIC_LOG_DIR"),
            "femic_output_root": execution_plan.env.get("FEMIC_OUTPUT_ROOT"),
            "femic_run_config_path": execution_plan.env.get("FEMIC_RUN_CONFIG_PATH"),
            "femic_run_config_sha256": execution_plan.env.get(
                "FEMIC_RUN_CONFIG_SHA256"
            ),
            "femic_sampling_seed": execution_plan.env.get("FEMIC_SAMPLING_SEED"),
        },
        "runtime_versions": collect_runtime_versions(),
        "paths": {
            "repo_root": str(execution_plan.script_path.parent),
            "data_dir": str((execution_plan.script_path.parent / "data").resolve()),
            "output_dir": str(output_root),
            "vdyp_cfg_dir": str(
                (execution_plan.script_path.parent / "vdyp_io" / "VDYP_CFG").resolve()
            ),
            "vdyp_executable": str(
                (
                    execution_plan.script_path.parent
                    / "VDYP7"
                    / "VDYP7"
                    / "VDYP7Console.exe"
                ).resolve()
            ),
        },
        "log_paths": log_paths,
        "artifacts": {
            key: [{"path": path, "exists": Path(path).exists()} for path in path_list]
            for key, path_list in log_paths.items()
        },
        "checkpoints": {
            "pre_vdyp": [
                {"path": str(path), "exists": path.exists()}
                for path in execution_plan.checkpoint_paths
            ]
        },
    }
