"""VDYP-specific helper utilities."""

from __future__ import annotations

from pathlib import Path

from femic.pipeline.vdyp_logging import build_tsa_vdyp_log_paths


def build_vdyp_log_paths(
    log_dir: Path, tsa_list: list[str], run_id: str
) -> dict[str, list[str]]:
    """Build run-scoped VDYP artifact paths for each TSA."""
    tsa_paths = [
        build_tsa_vdyp_log_paths(
            tsa_code=tsa,
            run_id=run_id,
            env={"FEMIC_LOG_DIR": str(log_dir)},
        )
        for tsa in tsa_list
    ]
    return {
        "vdyp_runs": [str(paths["run"]) for paths in tsa_paths],
        "vdyp_curve_events": [str(paths["curve"]) for paths in tsa_paths],
        "vdyp_stdout": [str(paths["stdout"]) for paths in tsa_paths],
        "vdyp_stderr": [str(paths["stderr"]) for paths in tsa_paths],
    }
