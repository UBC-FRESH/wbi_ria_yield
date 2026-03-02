from __future__ import annotations

from pathlib import Path

from femic.pipeline.io import (
    FALLBACK_DEFAULT_TSA_LIST,
    build_legacy_execution_plan,
    build_pipeline_run_config,
    load_default_tsa_list,
    normalize_tsa_list,
    resolve_run_paths,
)
from femic.pipeline.plots import strata_plot_paths, tipsy_vdyp_plot_path
from femic.pipeline.tsa import MIN_STANDCOUNT, target_nstrata_for


def test_normalize_tsa_list_defaults_and_padding(tmp_path: Path) -> None:
    cfg = tmp_path / "dev.toml"
    cfg.write_text("[run]\ndefault_tsa_list = ['24','41']\n", encoding="utf-8")
    assert normalize_tsa_list(None, default_tsa_list=load_default_tsa_list(cfg)) == [
        "24",
        "41",
    ]
    assert normalize_tsa_list([8, "16", "041"]) == ["08", "16", "041"]


def test_load_default_tsa_list_fallback_when_missing(tmp_path: Path) -> None:
    assert load_default_tsa_list(tmp_path / "missing.toml") == FALLBACK_DEFAULT_TSA_LIST


def test_resolve_run_paths_uses_script_parent_as_repo_root(tmp_path: Path) -> None:
    script_path = tmp_path / "00_data-prep.py"
    script_path.write_text("# test\n", encoding="utf-8")

    resolved = resolve_run_paths(script_path=script_path)

    assert resolved.repo_root == tmp_path.resolve()
    assert resolved.log_dir == (tmp_path / "vdyp_io" / "logs").resolve()


def test_tsa_target_nstrata_lookup() -> None:
    assert target_nstrata_for("8") == 9
    assert target_nstrata_for("16") == 13
    assert MIN_STANDCOUNT == 1000


def test_plot_path_helpers() -> None:
    pdf_path, png_path = strata_plot_paths("8")
    tipsy_path = tipsy_vdyp_plot_path(23005, "08")

    assert pdf_path == Path("plots/strata-tsa08.pdf")
    assert png_path == Path("plots/strata-tsa08.png")
    assert tipsy_path == Path("plots/tipsy_vdyp_tsa08-23005.png")


def test_build_pipeline_run_config_normalizes_tsa_values() -> None:
    cfg = build_pipeline_run_config(
        tsa_list=[8, "16"],
        resume=True,
        debug_rows=25,
        run_id="test123",
        log_dir=Path("vdyp_io/logs"),
    )
    assert cfg.tsa_list == ["08", "16"]
    assert cfg.resume is True
    assert cfg.debug_rows == 25
    assert cfg.run_id == "test123"


def test_build_legacy_execution_plan_resolves_env_and_paths(tmp_path: Path) -> None:
    script_path = tmp_path / "00_data-prep.py"
    script_path.write_text("# test\n", encoding="utf-8")
    cfg = build_pipeline_run_config(
        tsa_list=["8", "24"],
        resume=False,
        debug_rows=100,
        run_id="runabc",
        log_dir=tmp_path / "logs",
    )

    plan = build_legacy_execution_plan(
        run_config=cfg,
        script_path=script_path,
        python_executable="/usr/bin/python3",
        base_env={},
    )

    assert plan.run_id == "runabc"
    assert plan.tsa_list == ["08", "24"]
    assert (
        plan.manifest_path == (tmp_path / "logs" / "run_manifest-runabc.json").resolve()
    )
    assert plan.env["FEMIC_TSA_LIST"] == "08,24"
    assert plan.env["FEMIC_RESUME"] == "0"
    assert plan.env["FEMIC_DEBUG_ROWS"] == "100"
    assert plan.env["FEMIC_RUN_ID"] == "runabc"
    assert plan.cmd == ["/usr/bin/python3", str(script_path)]
