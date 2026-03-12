"""Plot artifact naming helpers."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any


def strata_plot_paths(tsa_code: str, root: Path = Path("plots")) -> tuple[Path, Path]:
    """Return PDF/PNG output paths for strata diagnostics for one TSA/case code."""
    tsa = str(tsa_code).zfill(2)
    return root / f"strata-tsa{tsa}.pdf", root / f"strata-tsa{tsa}.png"


def tipsy_vdyp_plot_path(au: int, tsa_code: str, root: Path = Path("plots")) -> Path:
    """Return the canonical TIPSY-vs-VDYP overlay plot path for an AU."""
    tsa = str(tsa_code).zfill(2)
    return root / f"tipsy_vdyp_tsa{tsa}-{au}.png"


def tipsy_vdyp_ylim_for_tsa(
    tsa_code: str,
    default: tuple[float, float] = (0.0, 600.0),
) -> tuple[float, float]:
    """Return legacy TIPSY-vs-VDYP plot y-limits for a TSA/custom unit."""
    tsa = str(tsa_code).strip().lower()
    if tsa == "k3z":
        return (0.0, 2000.0)
    return default


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
    if "totalarea_p" in ordered.columns and not ordered["totalarea_p"].isna().all():
        abundance = ordered["totalarea_p"]
    elif "coverage" in ordered.columns:
        abundance = ordered["coverage"]
    else:
        abundance = ordered.iloc[:, 0]
    abundance = abundance.fillna(0.0).astype(float)
    stratum_props = [float(v) for v in abundance.values]
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
    x_lo = float(hist_xlim[0])
    x_hi = float(hist_xlim[1])
    try:
        observed_max = float(getattr(strata_df.site_index_median, "max")())
    except (AttributeError, TypeError, ValueError):
        observed_max = x_hi
    if math.isfinite(observed_max):
        x_hi = max(x_hi, observed_max + 1.0)
    ax.set_xlim([x_lo, x_hi])
    plt_module.scatter(strata_df.totalarea_p, strata_df.median_si)


def render_strata_distribution_plot(
    *,
    tsa_code: str,
    f_table: Any,
    stratum_col: str,
    labels: list[str],
    stratum_props: list[float],
    plot_config: StrataDistributionPlotConfig,
    sns_module: Any,
    plt_module: Any,
    strata_plot_paths_fn: Any = strata_plot_paths,
) -> None:
    """Render and save the 01a stratum distribution bar+violin diagnostic plot."""
    _fig, ax = plt_module.subplots(figsize=plot_config.figsize)
    ax2 = ax.twiny()
    sns_module.barplot(
        y=labels,
        x=stratum_props,
        ax=ax,
        alpha=plot_config.alpha,
        label="Relative abundance of stratum (proportion of total area)",
    )
    sns_module.violinplot(
        y=stratum_col,
        x="SITE_INDEX",
        data=f_table.reset_index(),
        ax=ax2,
        bw_method=plot_config.bw,
        order=labels,
        linewidth=plot_config.linewidth,
        inner=plot_config.inner,
        width=plot_config.width,
        cut=plot_config.cut,
    )
    # Keep sparse strata visible when violin KDE is underdetermined.
    sns_module.stripplot(
        y=stratum_col,
        x="SITE_INDEX",
        data=f_table.reset_index(),
        ax=ax2,
        order=labels,
        color="black",
        alpha=0.35,
        size=2.2,
    )
    ax.set_xlabel("Relative abundance of stratum (proportion of total area)")
    si_default_lo, si_default_hi = plot_config.site_index_xlim
    site_index = f_table.reset_index().get("SITE_INDEX")
    si_lo = float(si_default_lo)
    si_hi = float(si_default_hi)
    if site_index is not None and len(site_index) > 0:
        try:
            obs_min = float(site_index.min())
            obs_max = float(site_index.max())
        except (TypeError, ValueError):
            obs_min, obs_max = si_lo, si_hi
        if math.isfinite(obs_min):
            si_lo = min(si_lo, math.floor(obs_min) - 1.0)
        if math.isfinite(obs_max):
            si_hi = max(si_hi, math.ceil(obs_max) + 1.0)
    ax2.set_xlim((si_lo, si_hi))
    strata_pdf_path, strata_png_path = strata_plot_paths_fn(tsa_code)
    plt_module.savefig(strata_pdf_path, bbox_inches="tight")
    plt_module.savefig(strata_png_path, facecolor="white", bbox_inches="tight")
