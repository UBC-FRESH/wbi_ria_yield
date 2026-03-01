from __future__ import annotations

import json
from pathlib import Path

from femic.pipeline.vdyp_logging import (
    append_jsonl,
    append_text,
    build_tsa_vdyp_log_paths,
    resolve_run_id,
    vdyp_log_base,
)


def test_resolve_run_id_prefers_environment_value() -> None:
    assert resolve_run_id(env={"FEMIC_RUN_ID": "run-123"}) == "run-123"


def test_vdyp_log_base_honors_env_override(tmp_path: Path) -> None:
    resolved = vdyp_log_base(
        vdyp_io_dirname="ignored",
        env={"FEMIC_LOG_DIR": str(tmp_path / "custom-logs")},
    )
    assert resolved == tmp_path / "custom-logs"


def test_build_tsa_vdyp_log_paths_returns_run_scoped_files() -> None:
    paths = build_tsa_vdyp_log_paths(
        tsa_code="8", run_id="abc", vdyp_io_dirname="vdyp_io"
    )
    assert paths["run"] == Path("vdyp_io/logs/vdyp_runs-tsa08-abc.jsonl")
    assert paths["curve"] == Path("vdyp_io/logs/vdyp_curve_events-tsa08-abc.jsonl")
    assert paths["stdout"] == Path("vdyp_io/logs/vdyp_stdout-tsa08-abc.log")
    assert paths["stderr"] == Path("vdyp_io/logs/vdyp_stderr-tsa08-abc.log")


def test_append_helpers_create_parent_and_write_payload(tmp_path: Path) -> None:
    jsonl_path = tmp_path / "logs" / "events.jsonl"
    text_path = tmp_path / "logs" / "stdout.log"

    append_jsonl(jsonl_path, {"event": "ok", "count": 1})
    append_text(text_path, "hello\n")

    line = jsonl_path.read_text(encoding="utf-8").strip()
    assert json.loads(line) == {"event": "ok", "count": 1}
    assert text_path.read_text(encoding="utf-8") == "hello\n"
