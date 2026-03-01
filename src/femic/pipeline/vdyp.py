"""VDYP-specific helper utilities."""

from __future__ import annotations

from pathlib import Path


def build_vdyp_log_paths(
    log_dir: Path, tsa_list: list[str], run_id: str
) -> dict[str, list[str]]:
    """Build run-scoped VDYP artifact paths for each TSA."""
    return {
        "vdyp_runs": [
            str(log_dir / f"vdyp_runs-tsa{tsa}-{run_id}.jsonl") for tsa in tsa_list
        ],
        "vdyp_curve_events": [
            str(log_dir / f"vdyp_curve_events-tsa{tsa}-{run_id}.jsonl")
            for tsa in tsa_list
        ],
        "vdyp_stdout": [
            str(log_dir / f"vdyp_stdout-tsa{tsa}-{run_id}.log") for tsa in tsa_list
        ],
        "vdyp_stderr": [
            str(log_dir / f"vdyp_stderr-tsa{tsa}-{run_id}.log") for tsa in tsa_list
        ],
    }
