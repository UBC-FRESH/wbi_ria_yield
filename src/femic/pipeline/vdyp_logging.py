"""VDYP logging helpers for run-scoped artifact paths and appenders."""

from __future__ import annotations

from datetime import UTC, datetime
import json
import os
from pathlib import Path
from typing import Any, Mapping


def resolve_run_id(env: Mapping[str, str] | None = None) -> str:
    """Resolve run id from environment, falling back to UTC timestamp."""
    env_map = dict(env) if env is not None else os.environ
    run_id = env_map.get("FEMIC_RUN_ID")
    if run_id:
        return run_id
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def vdyp_log_base(
    vdyp_io_dirname: str = "vdyp_io", env: Mapping[str, str] | None = None
) -> Path:
    """Resolve VDYP log base directory, honoring FEMIC_LOG_DIR override."""
    env_map = dict(env) if env is not None else os.environ
    log_dir_env = env_map.get("FEMIC_LOG_DIR")
    if log_dir_env:
        return Path(log_dir_env)
    return Path(vdyp_io_dirname) / "logs"


def build_tsa_vdyp_log_paths(
    *,
    tsa_code: str,
    run_id: str,
    vdyp_io_dirname: str = "vdyp_io",
    env: Mapping[str, str] | None = None,
) -> dict[str, Path]:
    """Build run-scoped VDYP log artifact paths for a single TSA."""
    base = vdyp_log_base(vdyp_io_dirname, env=env)
    tsa = str(tsa_code).zfill(2)
    return {
        "run": base / f"vdyp_runs-tsa{tsa}-{run_id}.jsonl",
        "curve": base / f"vdyp_curve_events-tsa{tsa}-{run_id}.jsonl",
        "stdout": base / f"vdyp_stdout-tsa{tsa}-{run_id}.log",
        "stderr": base / f"vdyp_stderr-tsa{tsa}-{run_id}.log",
    }


def serialize_jsonl_payload(payload: Mapping[str, Any]) -> str:
    """Serialize one payload for JSONL output with legacy `default=str` conversion."""
    return json.dumps(payload, default=str)


def _append_text_fragment(path: str | Path, text: str) -> None:
    """Append text to a file, creating parent directories as needed."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(text)


def append_line(path: str | Path, line: str) -> None:
    """Append one line of text with newline, creating parent directories as needed."""
    _append_text_fragment(path, line + "\n")


def append_jsonl(path: str | Path, payload: dict[str, Any]) -> None:
    """Append one JSON object line, creating parent directories as needed."""
    append_line(path, serialize_jsonl_payload(payload))


def append_text(path: str | Path, text: str) -> None:
    """Append plain text, creating parent directories as needed."""
    _append_text_fragment(path, text)


def build_vdyp_stream_header(
    *,
    phase: str,
    feature_count: int,
    cache_hits: int,
    cmd: str,
    timestamp: str | None = None,
) -> str:
    """Build a consistent VDYP stdout/stderr stream header block."""
    ts = timestamp or datetime.now(UTC).isoformat()
    return (
        f"\n=== {ts} phase={phase} feature_count={feature_count} cache_hits={cache_hits} ===\n"
        f"cmd: {cmd}\n"
    )
