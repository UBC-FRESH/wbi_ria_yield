from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from femic.pipeline.vdyp import build_vdyp_log_paths
from femic.workflows.legacy import _build_manifest_payload


def test_build_log_paths_includes_stream_artifacts(tmp_path: Path) -> None:
    log_paths = build_vdyp_log_paths(tmp_path, ["08", "16"], "run123")

    assert len(log_paths["vdyp_runs"]) == 2
    assert len(log_paths["vdyp_curve_events"]) == 2
    assert len(log_paths["vdyp_stdout"]) == 2
    assert len(log_paths["vdyp_stderr"]) == 2
    assert log_paths["vdyp_stdout"][0].endswith("vdyp_stdout-tsa08-run123.log")


def test_build_manifest_payload_contains_runtime_and_artifact_sections(
    tmp_path: Path,
) -> None:
    script_path = tmp_path / "00_data-prep.py"
    script_path.write_text("print('ok')\n", encoding="utf-8")
    checkpoint = tmp_path / "data" / "vdyp_prep-tsa08.pkl"
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_text("x", encoding="utf-8")

    payload = _build_manifest_payload(
        run_id="run123",
        run_uuid="uuid-1",
        status="started",
        started_at=datetime.now(UTC),
        finished_at=None,
        duration_sec=None,
        exit_code=None,
        cmd=["python", str(script_path)],
        script_path=script_path,
        log_dir=tmp_path / "logs",
        tsa_list=["08"],
        resume=True,
        debug_rows=50,
        env={},
        checkpoint_paths=[checkpoint],
    )

    assert payload["runtime_versions"]
    assert "paths" in payload
    assert "artifacts" in payload
    assert payload["run_uuid"] == "uuid-1"
    assert payload["artifacts"]["vdyp_stdout"][0]["exists"] is False
    assert payload["checkpoints"]["pre_vdyp"][0]["exists"] is True
