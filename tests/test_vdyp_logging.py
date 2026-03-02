from __future__ import annotations

import json
from pathlib import Path

from femic.pipeline.vdyp_logging import (
    append_line,
    append_jsonl,
    append_text,
    build_vdyp_stream_header,
    build_vdyp_stream_log_block,
    build_tsa_vdyp_log_paths,
    resolve_run_id,
    serialize_jsonl_payload,
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


def test_append_text_appends_without_overwriting(tmp_path: Path) -> None:
    text_path = tmp_path / "logs" / "stdout.log"
    append_text(text_path, "hello")
    append_text(text_path, " world")
    assert text_path.read_text(encoding="utf-8") == "hello world"


def test_serialize_jsonl_payload_uses_default_str_conversion() -> None:
    class _Obj:
        def __str__(self) -> str:
            return "obj-str"

    line = serialize_jsonl_payload({"event": "ok", "obj": _Obj()})
    assert json.loads(line) == {"event": "ok", "obj": "obj-str"}


def test_append_line_creates_parent_and_appends_newline(tmp_path: Path) -> None:
    line_path = tmp_path / "logs" / "line.log"
    append_line(line_path, "first")
    append_line(line_path, "second")
    assert line_path.read_text(encoding="utf-8") == "first\nsecond\n"


def test_build_vdyp_stream_header_uses_expected_format() -> None:
    header = build_vdyp_stream_header(
        phase="initial",
        feature_count=12,
        cache_hits=3,
        cmd="wine VDYP7Console.exe",
        timestamp="2026-03-02T00:00:00+00:00",
    )
    assert (
        header
        == "\n=== 2026-03-02T00:00:00+00:00 phase=initial feature_count=12 cache_hits=3 ===\n"
        "cmd: wine VDYP7Console.exe\n"
    )


def test_build_vdyp_stream_log_block_appends_trailing_newline() -> None:
    stream_text = "vdyp stdout chunk"
    stream_header = "header\n"
    assert (
        build_vdyp_stream_log_block(
            stream_header=stream_header, stream_text=stream_text
        )
        == "header\nvdyp stdout chunk\n"
    )
