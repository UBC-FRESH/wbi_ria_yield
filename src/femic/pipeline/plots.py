"""Plot artifact naming helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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
