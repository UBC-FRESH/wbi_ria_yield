"""Legacy workflow wrappers for FEMIC."""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from femic.pipeline.io import PipelineRunConfig, build_legacy_execution_plan
from femic.pipeline.manifest import build_run_manifest_payload, write_manifest
from femic.pipeline.stages import run_legacy_subprocess


_LEGACY_NOISE_LINES = {"Error in sys.excepthook:", "Original exception was:"}


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
