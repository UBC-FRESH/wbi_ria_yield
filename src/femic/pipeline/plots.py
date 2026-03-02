"""Plot artifact naming helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


def strata_plot_paths(tsa_code: str, root: Path = Path("plots")) -> tuple[Path, Path]:
    tsa = str(tsa_code).zfill(2)
    return root / f"strata-tsa{tsa}.pdf", root / f"strata-tsa{tsa}.png"


def tipsy_vdyp_plot_path(au: int, tsa_code: str, root: Path = Path("plots")) -> Path:
    tsa = str(tsa_code).zfill(2)
    return root / f"tipsy_vdyp_tsa{tsa}-{au}.png"


@dataclass(frozen=True)
class StrataDistributionPlotConfig:
    """Defaults for the 01a stratum-distribution diagnostic plot."""

    figsize: tuple[float, float]
    alpha: float
    linewidth: float
    inner: str
    width: float
    bw: str
    cut: float
    site_index_xlim: tuple[float, float]


def build_strata_distribution_plot_config(
    *,
    figsize: tuple[float, float] = (8, 12),
    alpha: float = 0.2,
    linewidth: float = 1.0,
    inner: str = "box",
    width: float = 0.8,
    bw: str = "scott",
    cut: float = 0.0,
    site_index_xlim: tuple[float, float] = (0, 30),
) -> StrataDistributionPlotConfig:
    """Build defaults for 01a stratum abundance/SI violin diagnostics."""
    return StrataDistributionPlotConfig(
        figsize=figsize,
        alpha=alpha,
        linewidth=linewidth,
        inner=inner,
        width=width,
        bw=bw,
        cut=cut,
        site_index_xlim=site_index_xlim,
    )


def resolve_strata_plot_ordering(
    *,
    strata_df: Any,
    sort_lex: bool = False,
) -> tuple[list[float], list[str]]:
    """Resolve stratum bar/violin ordering inputs for 01a diagnostics plots."""
    if sort_lex:
        ordered = strata_df.sort_index()
    else:
        ordered = strata_df
    stratum_props = [float(v) for v in ordered.totalarea_p.values]
    labels = [str(v) for v in ordered.index.values]
    return stratum_props, labels


def plot_strata_site_index_diagnostics(
    *,
    strata_df: Any,
    np_module: Any,
    plt_module: Any,
    hist_xlim: tuple[float, float] = (0, 25),
    hist_bin_stop: float = 25,
    hist_bin_step: float = 1,
) -> None:
    """Render early 01a strata diagnostics (SI histogram + abundance scatter)."""
    ax = strata_df.site_index_median.hist(
        bins=np_module.arange(hist_bin_stop, step=hist_bin_step)
    )
    ax.set_xlim(list(hist_xlim))
    plt_module.scatter(strata_df.totalarea_p, strata_df.median_si)
