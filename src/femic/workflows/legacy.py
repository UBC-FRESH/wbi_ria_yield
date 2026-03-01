"""Legacy workflow wrappers for FEMIC."""

from __future__ import annotations

import json
import platform
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

from femic.pipeline.io import PipelineRunConfig, resolve_run_paths
from femic.pipeline.vdyp import build_vdyp_log_paths


_LEGACY_NOISE_LINES = {"Error in sys.excepthook:", "Original exception was:"}


def _write_manifest(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _safe_version(dist_name: str) -> str | None:
    try:
        return metadata.version(dist_name)
    except metadata.PackageNotFoundError:
        return None


def _collect_runtime_versions() -> dict[str, object]:
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


def _build_manifest_payload(
    *,
    run_id: str,
    run_uuid: str,
    status: str,
    started_at: datetime,
    finished_at: datetime | None,
    duration_sec: float | None,
    exit_code: int | None,
    cmd: list[str],
    script_path: Path,
    log_dir: Path,
    tsa_list: list[str],
    resume: bool,
    debug_rows: int | None,
    env: dict[str, str],
    checkpoint_paths: list[Path],
) -> dict[str, object]:
    log_paths = build_vdyp_log_paths(log_dir, tsa_list, run_id)
    return {
        "run_id": run_id,
        "run_uuid": run_uuid,
        "status": status,
        "started_at_utc": started_at.isoformat(),
        "finished_at_utc": finished_at.isoformat() if finished_at else None,
        "duration_sec": duration_sec,
        "exit_code": exit_code,
        "command": cmd,
        "script_path": str(script_path),
        "cwd": str(script_path.parent),
        "log_dir": str(log_dir),
        "tsa_list": tsa_list,
        "options": {"resume": resume, "debug_rows": debug_rows},
        "env_flags": {
            "FEMIC_DISABLE_IPP": env.get("FEMIC_DISABLE_IPP"),
            "FEMIC_USE_SWIFTER": env.get("FEMIC_USE_SWIFTER"),
            "FEMIC_SKIP_STANDS_SHP": env.get("FEMIC_SKIP_STANDS_SHP"),
            "FEMIC_EXTERNAL_DATA_ROOT": env.get("FEMIC_EXTERNAL_DATA_ROOT"),
        },
        "runtime_versions": _collect_runtime_versions(),
        "paths": {
            "repo_root": str(script_path.parent),
            "data_dir": str((script_path.parent / "data").resolve()),
            "vdyp_cfg_dir": str(
                (script_path.parent / "vdyp_io" / "VDYP_CFG").resolve()
            ),
            "vdyp_executable": str(
                (script_path.parent / "VDYP7" / "VDYP7" / "VDYP7Console.exe").resolve()
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
                for path in checkpoint_paths
            ]
        },
    }


def run_data_prep(
    run_config: PipelineRunConfig,
) -> Path:
    """Run the legacy 00_data-prep.py workflow in a subprocess with overrides."""

    script_path = Path(__file__).resolve().parents[3] / "00_data-prep.py"
    if not script_path.exists():
        raise FileNotFoundError(f"Expected legacy script at {script_path}")

    run_paths = resolve_run_paths(script_path=script_path, log_dir=run_config.log_dir)
    resolved_tsas = run_config.tsa_list
    resolved_run_id = run_config.run_id or datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )
    resolved_log_dir = run_paths.log_dir
    manifest_path = resolved_log_dir / f"run_manifest-{resolved_run_id}.json"
    started_at = datetime.now(timezone.utc)
    monotonic_started = time.monotonic()
    checkpoint_paths = [Path(f"data/vdyp_prep-tsa{tsa}.pkl") for tsa in resolved_tsas]

    env = dict(os.environ)
    env["FEMIC_TSA_LIST"] = ",".join(resolved_tsas)
    env["FEMIC_RESUME"] = "1" if run_config.resume else "0"
    if run_config.debug_rows:
        env["FEMIC_DEBUG_ROWS"] = str(run_config.debug_rows)
    else:
        env.pop("FEMIC_DEBUG_ROWS", None)
    env["FEMIC_RUN_ID"] = resolved_run_id
    env["FEMIC_LOG_DIR"] = str(resolved_log_dir)
    env.setdefault("FEMIC_RUN_UUID", str(uuid.uuid4()))
    run_uuid = env["FEMIC_RUN_UUID"]

    cmd = [sys.executable, str(script_path)]

    _write_manifest(
        manifest_path,
        _build_manifest_payload(
            run_id=resolved_run_id,
            run_uuid=run_uuid,
            status="started",
            started_at=started_at,
            finished_at=None,
            duration_sec=None,
            exit_code=None,
            cmd=cmd,
            script_path=script_path,
            log_dir=resolved_log_dir,
            tsa_list=resolved_tsas,
            resume=run_config.resume,
            debug_rows=run_config.debug_rows,
            env=env,
            checkpoint_paths=checkpoint_paths,
        ),
    )

    process = subprocess.Popen(
        cmd,
        cwd=str(script_path.parent),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert process.stdout is not None
    for line in process.stdout:
        if line.strip() in _LEGACY_NOISE_LINES:
            continue
        sys.stdout.write(line)
    return_code = process.wait()
    finished_at = datetime.now(timezone.utc)
    duration_sec = round(time.monotonic() - monotonic_started, 3)
    _write_manifest(
        manifest_path,
        _build_manifest_payload(
            run_id=resolved_run_id,
            run_uuid=run_uuid,
            status="ok" if return_code == 0 else "failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=duration_sec,
            exit_code=return_code,
            cmd=cmd,
            script_path=script_path,
            log_dir=resolved_log_dir,
            tsa_list=resolved_tsas,
            resume=run_config.resume,
            debug_rows=run_config.debug_rows,
            env=env,
            checkpoint_paths=checkpoint_paths,
        ),
    )
    if return_code != 0:
        raise RuntimeError(
            f"Legacy workflow failed with exit code {return_code}: {' '.join(cmd)}"
        )
    return manifest_path
