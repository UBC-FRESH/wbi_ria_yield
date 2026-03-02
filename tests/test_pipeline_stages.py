from __future__ import annotations

from pathlib import Path
import sys

from femic.pipeline.io import build_legacy_execution_plan, build_pipeline_run_config
from femic.pipeline.stages import (
    load_legacy_module,
    run_legacy_subprocess,
    run_legacy_tsa_loop,
)


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


def test_load_legacy_module_loads_run_tsa_symbol(tmp_path: Path) -> None:
    script_path = tmp_path / "legacy.py"
    script_path.write_text(
        "def run_tsa(*, tsa):\n    return f'ran {tsa}'\n",
        encoding="utf-8",
    )

    module = load_legacy_module(script_path=script_path, module_name="legacy_test")

    assert hasattr(module, "run_tsa")
    assert module.run_tsa(tsa="08") == "ran 08"


def test_run_legacy_tsa_loop_applies_skip_logic() -> None:
    seen: list[str] = []

    run_legacy_tsa_loop(
        tsa_list=["08", "16", "24"],
        should_skip_fn=lambda tsa: tsa == "16",
        run_one_fn=lambda tsa: seen.append(tsa),
    )

    assert seen == ["08", "24"]
