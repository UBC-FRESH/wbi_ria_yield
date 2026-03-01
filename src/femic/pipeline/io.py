"""I/O-oriented helpers shared across pipeline entrypoints."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_TSA_LIST = ["08", "16", "24", "40", "41"]


def normalize_tsa_list(tsa_list: Iterable[str] | None) -> list[str]:
    """Return zero-padded TSA codes, defaulting to the configured working set."""
    if not tsa_list:
        return DEFAULT_TSA_LIST.copy()
    return [str(tsa).zfill(2) for tsa in tsa_list]


@dataclass(frozen=True)
class RunPaths:
    """Resolved filesystem roots used by the legacy workflow wrapper."""

    repo_root: Path
    script_path: Path
    log_dir: Path


def resolve_run_paths(*, script_path: Path, log_dir: Path | None = None) -> RunPaths:
    repo_root = script_path.parent.resolve()
    return RunPaths(
        repo_root=repo_root,
        script_path=script_path.resolve(),
        log_dir=(log_dir or (repo_root / "vdyp_io" / "logs")).resolve(),
    )
