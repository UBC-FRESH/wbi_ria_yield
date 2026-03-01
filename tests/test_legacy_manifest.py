from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from femic.pipeline.io import build_legacy_execution_plan, build_pipeline_run_config
from femic.pipeline.manifest import build_run_manifest_payload
from femic.pipeline.vdyp import build_vdyp_log_paths


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

    cfg = build_pipeline_run_config(
        tsa_list=["08"],
        resume=True,
        debug_rows=50,
        run_id="run123",
        log_dir=tmp_path / "logs",
    )
    plan = build_legacy_execution_plan(
        run_config=cfg,
        script_path=script_path,
        python_executable="python",
        base_env={"FEMIC_RUN_UUID": "uuid-1"},
    )
    payload = build_run_manifest_payload(
        execution_plan=plan,
        status="started",
        started_at=datetime.now(UTC),
        finished_at=None,
        duration_sec=None,
        exit_code=None,
    )

    assert payload["runtime_versions"]
    assert "paths" in payload
    assert "artifacts" in payload
    assert payload["run_uuid"] == "uuid-1"
    assert payload["artifacts"]["vdyp_stdout"][0]["exists"] is False
    assert "pre_vdyp" in payload["checkpoints"]
