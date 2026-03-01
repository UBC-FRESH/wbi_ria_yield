"""I/O-oriented helpers shared across pipeline entrypoints."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib
from typing import Iterable


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
