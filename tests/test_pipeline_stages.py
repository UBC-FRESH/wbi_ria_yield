from __future__ import annotations

from pathlib import Path
import sys

from femic.pipeline.io import build_legacy_execution_plan, build_pipeline_run_config
from femic.pipeline.stages import run_legacy_subprocess


def test_run_legacy_subprocess_filters_known_noise(capsys, tmp_path: Path) -> None:
    script_path = tmp_path / "00_data-prep.py"
    script_path.write_text(
        "print('hello')\n"
        "print('Error in sys.excepthook:')\n"
        "print('Original exception was:')\n"
        "print('done')\n",
        encoding="utf-8",
    )
    cfg = build_pipeline_run_config(tsa_list=["08"], resume=True)
    plan = build_legacy_execution_plan(
        run_config=cfg,
        script_path=script_path,
        python_executable=sys.executable,
        base_env={},
    )

    result = run_legacy_subprocess(
        execution_plan=plan,
        drop_lines={"Error in sys.excepthook:", "Original exception was:"},
    )

    out = capsys.readouterr().out
    assert result.exit_code == 0
    assert "hello" in out
    assert "done" in out
    assert "Error in sys.excepthook:" not in out
    assert "Original exception was:" not in out
