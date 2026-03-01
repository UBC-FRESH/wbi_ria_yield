"""Plot artifact naming helpers."""

from __future__ import annotations

from pathlib import Path


def strata_plot_paths(tsa_code: str, root: Path = Path("plots")) -> tuple[Path, Path]:
    tsa = str(tsa_code).zfill(2)
    return root / f"strata-tsa{tsa}.pdf", root / f"strata-tsa{tsa}.png"


def tipsy_vdyp_plot_path(au: int, tsa_code: str, root: Path = Path("plots")) -> Path:
    tsa = str(tsa_code).zfill(2)
    return root / f"tipsy_vdyp_tsa{tsa}-{au}.png"
