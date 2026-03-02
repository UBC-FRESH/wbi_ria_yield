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
from femic.pipeline.plots import (
    StrataDistributionPlotConfig,
    build_strata_distribution_plot_config,
    plot_strata_site_index_diagnostics,
    render_strata_distribution_plot,
    resolve_strata_plot_ordering,
    strata_plot_paths,
    tipsy_vdyp_plot_path,
)
import pytest
import pandas as pd

from femic.pipeline.tsa import (
    MIN_STANDCOUNT,
    apply_stratum_alias_map,
    build_strata_summary,
    build_stratum_lexmatch_alias_map,
    target_nstrata_for,
)


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


def test_build_strata_summary_filters_and_computes_expected_fields() -> None:
    f_table = pd.DataFrame(
        {
            "stratum": ["A", "A", "A", "B", "B", "C"],
            "FEATURE_AREA_SQM": [10.0, 10.0, 10.0, 20.0, 20.0, 30.0],
            "SITE_INDEX": [10.0, 11.0, 12.0, 20.0, 21.0, 30.0],
            "FEATURE_ID": [1, 2, 3, 4, 5, 6],
            "CROWN_CLOSURE": [50.0, 60.0, 55.0, 70.0, 65.0, 80.0],
        }
    ).set_index("stratum")
    f_table["totalarea_p"] = f_table.FEATURE_AREA_SQM / f_table.FEATURE_AREA_SQM.sum()

    strata_df, largestn, site_index_iqr_mean = build_strata_summary(
        f_table=f_table,
        stratum_col="stratum",
        pd_module=pd,
        target_nstrata=2,
        min_standcount=2,
    )

    assert list(strata_df.index) == ["B", "A"]
    assert largestn == ["B", "A"]
    assert strata_df.loc["A", "median_si"] == 11.0
    assert strata_df.loc["B", "median_si"] == 20.5
    assert round(site_index_iqr_mean, 2) == 0.5


def test_build_strata_summary_requires_target_or_tsa_code() -> None:
    f_table = pd.DataFrame(
        {
            "stratum": ["A", "A"],
            "FEATURE_AREA_SQM": [1.0, 1.0],
            "SITE_INDEX": [10.0, 11.0],
            "FEATURE_ID": [1, 2],
            "CROWN_CLOSURE": [50.0, 55.0],
            "totalarea_p": [0.5, 0.5],
        }
    ).set_index("stratum")

    with pytest.raises(ValueError, match="target_nstrata or tsa_code"):
        build_strata_summary(
            f_table=f_table,
            stratum_col="stratum",
            pd_module=pd,
        )


def test_build_stratum_lexmatch_alias_map_prefers_highest_area_on_distance_tie() -> (
    None
):
    f_table = pd.DataFrame(
        {
            "stratum": ["SAA", "SBB", "SAB"],
            "stratum_lexmatch": ["AA", "BB", "AB"],
            "totalarea_p": [0.3, 0.6, 0.1],
        }
    ).set_index("stratum")

    distances = {
        ("AA", "AB"): 1,
        ("BB", "AB"): 1,
    }

    def fake_levenshtein(a: str, b: str) -> int:
        return distances.get((a, b), distances.get((b, a), 9))

    alias_map = build_stratum_lexmatch_alias_map(
        f_table=f_table,
        stratum_col="stratum",
        selected_strata_codes=["SAA", "SBB"],
        levenshtein_fn=fake_levenshtein,
    )

    assert alias_map == {"SAB": "SBB"}


def test_apply_stratum_alias_map_assigns_selected_or_best_match() -> None:
    frame = pd.DataFrame(
        {
            "stratum": ["SAA", "SAB", "SXX"],
            "value": [1, 2, 3],
        }
    )
    matched_col = apply_stratum_alias_map(
        f_table=frame,
        stratum_col="stratum",
        selected_strata_codes=["SAA", "SBB"],
        best_match={"SAB": "SBB"},
    )

    assert matched_col == "stratum_matched"
    assert frame["stratum_matched"].tolist() == ["SAA", "SBB", "SXX"]


def test_plot_path_helpers() -> None:
    pdf_path, png_path = strata_plot_paths("8")
    tipsy_path = tipsy_vdyp_plot_path(23005, "08")

    assert pdf_path == Path("plots/strata-tsa08.pdf")
    assert png_path == Path("plots/strata-tsa08.png")
    assert tipsy_path == Path("plots/tipsy_vdyp_tsa08-23005.png")


def test_build_strata_distribution_plot_config_defaults() -> None:
    cfg = build_strata_distribution_plot_config()

    assert isinstance(cfg, StrataDistributionPlotConfig)
    assert cfg.figsize == (8, 12)
    assert cfg.alpha == 0.2
    assert cfg.linewidth == 1.0
    assert cfg.inner == "box"
    assert cfg.width == 0.8
    assert cfg.bw == "scott"
    assert cfg.cut == 0.0
    assert cfg.site_index_xlim == (0, 30)


def test_resolve_strata_plot_ordering_abundance_and_lex_modes() -> None:
    strata_df = pd.DataFrame(
        {
            "totalarea_p": [0.6, 0.4],
        },
        index=["B2", "A1"],
    )

    props_default, labels_default = resolve_strata_plot_ordering(
        strata_df=strata_df,
        sort_lex=False,
    )
    props_lex, labels_lex = resolve_strata_plot_ordering(
        strata_df=strata_df,
        sort_lex=True,
    )

    assert props_default == [0.6, 0.4]
    assert labels_default == ["B2", "A1"]
    assert props_lex == [0.4, 0.6]
    assert labels_lex == ["A1", "B2"]


def test_plot_strata_site_index_diagnostics_calls_hist_and_scatter() -> None:
    class _FakeAx:
        def __init__(self) -> None:
            self.xlim_calls: list[list[float]] = []

        def set_xlim(self, value: list[float]) -> None:
            self.xlim_calls.append(value)

    class _SiteIndexSeries:
        def __init__(self, ax: _FakeAx) -> None:
            self.ax = ax
            self.hist_bins: list[list[float]] = []

        def hist(self, bins: list[float]) -> _FakeAx:
            self.hist_bins.append(bins)
            return self.ax

    class _FakeStrata:
        def __init__(self) -> None:
            self.ax = _FakeAx()
            self.site_index_median = _SiteIndexSeries(self.ax)
            self.totalarea_p = [0.4, 0.6]
            self.median_si = [12.0, 18.0]

    class _FakeNp:
        @staticmethod
        def arange(stop: float, step: float = 1.0) -> list[float]:
            vals = []
            v = 0.0
            while v < stop:
                vals.append(v)
                v += step
            return vals

    class _FakePlt:
        def __init__(self) -> None:
            self.scatter_calls: list[tuple[object, object]] = []

        def scatter(self, x: object, y: object) -> None:
            self.scatter_calls.append((x, y))

    strata = _FakeStrata()
    fake_plt = _FakePlt()
    plot_strata_site_index_diagnostics(
        strata_df=strata,
        np_module=_FakeNp(),
        plt_module=fake_plt,
    )

    assert strata.site_index_median.hist_bins == [[float(i) for i in range(25)]]
    assert strata.ax.xlim_calls == [[0, 25]]
    assert fake_plt.scatter_calls == [([0.4, 0.6], [12.0, 18.0])]


def test_render_strata_distribution_plot_uses_helper_config_and_paths() -> None:
    class _FakeAxis:
        def __init__(self) -> None:
            self.xlabel_calls: list[str] = []
            self.xlim_calls: list[tuple[float, float]] = []

        def twiny(self) -> "_FakeAxis":
            return self

        def set_xlabel(self, value: str) -> None:
            self.xlabel_calls.append(value)

        def set_xlim(self, value: tuple[float, float]) -> None:
            self.xlim_calls.append(value)

    class _FakePlt:
        def __init__(self) -> None:
            self.subplots_calls: list[tuple[float, float]] = []
            self.savefig_calls: list[tuple[Path, dict[str, object]]] = []

        def subplots(self, *, figsize: tuple[float, float]) -> tuple[None, _FakeAxis]:
            self.subplots_calls.append(figsize)
            return None, _FakeAxis()

        def savefig(self, path: Path, **kwargs: object) -> None:
            self.savefig_calls.append((path, dict(kwargs)))

    class _FakeSns:
        def __init__(self) -> None:
            self.barplot_calls = 0
            self.violinplot_calls = 0

        def barplot(self, **_kwargs: object) -> None:
            self.barplot_calls += 1

        def violinplot(self, **_kwargs: object) -> None:
            self.violinplot_calls += 1

    cfg = build_strata_distribution_plot_config()
    fake_plt = _FakePlt()
    fake_sns = _FakeSns()
    render_strata_distribution_plot(
        tsa_code="08",
        f_table=pd.DataFrame({"stratum": ["S1"], "SITE_INDEX": [20.0]}),
        stratum_col="stratum",
        labels=["S1"],
        stratum_props=[1.0],
        plot_config=cfg,
        sns_module=fake_sns,
        plt_module=fake_plt,
        strata_plot_paths_fn=lambda _tsa: (
            Path("plots/strata-tsa08.pdf"),
            Path("plots/strata-tsa08.png"),
        ),
    )

    assert fake_sns.barplot_calls == 1
    assert fake_sns.violinplot_calls == 1
    assert fake_plt.subplots_calls == [cfg.figsize]
    assert fake_plt.savefig_calls[0][0] == Path("plots/strata-tsa08.pdf")
    assert fake_plt.savefig_calls[1][0] == Path("plots/strata-tsa08.png")


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
