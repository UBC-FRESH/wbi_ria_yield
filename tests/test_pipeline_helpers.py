from __future__ import annotations

from pathlib import Path

from femic.pipeline.io import DEFAULT_TSA_LIST, normalize_tsa_list, resolve_run_paths
from femic.pipeline.plots import strata_plot_paths, tipsy_vdyp_plot_path
from femic.pipeline.tsa import target_nstrata_for


def test_normalize_tsa_list_defaults_and_padding() -> None:
    assert normalize_tsa_list(None) == DEFAULT_TSA_LIST
    assert normalize_tsa_list([8, "16", "041"]) == ["08", "16", "041"]


def test_resolve_run_paths_uses_script_parent_as_repo_root(tmp_path: Path) -> None:
    script_path = tmp_path / "00_data-prep.py"
    script_path.write_text("# test\n", encoding="utf-8")

    resolved = resolve_run_paths(script_path=script_path)

    assert resolved.repo_root == tmp_path.resolve()
    assert resolved.log_dir == (tmp_path / "vdyp_io" / "logs").resolve()


def test_tsa_target_nstrata_lookup() -> None:
    assert target_nstrata_for("8") == 9
    assert target_nstrata_for("16") == 13


def test_plot_path_helpers() -> None:
    pdf_path, png_path = strata_plot_paths("8")
    tipsy_path = tipsy_vdyp_plot_path(23005, "08")

    assert pdf_path == Path("plots/strata-tsa08.pdf")
    assert png_path == Path("plots/strata-tsa08.png")
    assert tipsy_path == Path("plots/tipsy_vdyp_tsa08-23005.png")
