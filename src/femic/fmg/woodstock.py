"""Woodstock compatibility export helpers (CSV package from FEMIC bundle outputs)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from .adapters import (
    build_bundle_model_context,
    normalize_tsa_code,
)
from .core import BundleModelContext
from .patchworks import (
    DEFAULT_FRAGMENTS_CRS,
    build_fragments_geodataframe,
)


DEFAULT_WOODSTOCK_OUTPUT_DIR = Path("output/woodstock")


@dataclass(frozen=True)
class WoodstockExportResult:
    """Paths and row counts from Woodstock compatibility export."""

    yields_csv_path: Path
    areas_csv_path: Path
    tsa_list: list[str]
    yield_rows: int
    area_rows: int


def _context_to_au_table(context: BundleModelContext) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "au_id": au.au_id,
                "tsa": au.tsa,
                "stratum_code": au.stratum_code,
                "si_level": au.si_level,
                "managed_curve_id": au.managed_curve_id,
                "unmanaged_curve_id": au.unmanaged_curve_id,
            }
            for au in context.analysis_units
        ]
    )


def build_woodstock_yields_table(
    *,
    context: BundleModelContext,
) -> pd.DataFrame:
    """Build long-format Woodstock compatibility yields table."""
    rows: list[dict[str, Any]] = []
    for au in context.analysis_units:
        au_id = au.au_id
        tsa = au.tsa
        stratum_code = au.stratum_code
        si_level = au.si_level
        for ifm, curve_id in (
            ("unmanaged", au.unmanaged_curve_id),
            ("managed", au.managed_curve_id),
        ):
            curve = context.curves_by_id.get(curve_id)
            if curve is None:
                continue
            for point in curve.points:
                rows.append(
                    {
                        "tsa": tsa,
                        "au_id": au_id,
                        "stratum_code": stratum_code,
                        "si_level": si_level,
                        "ifm": ifm,
                        "curve_id": curve_id,
                        "age": int(point.x),
                        "volume": float(point.y),
                    }
                )
    return pd.DataFrame(rows)


def build_woodstock_areas_table(
    *,
    checkpoint_path: Path,
    au_table: pd.DataFrame,
    tsa_list: Iterable[str],
    fragments_crs: str = DEFAULT_FRAGMENTS_CRS,
) -> pd.DataFrame:
    """Build Woodstock compatibility areas table from checkpoint geometries."""
    fragments = build_fragments_geodataframe(
        checkpoint_path=checkpoint_path,
        au_table=au_table,
        tsa_list=tsa_list,
        fragments_crs=fragments_crs,
    )
    return pd.DataFrame(
        {
            "stand_id": fragments["BLOCK"].astype(int),
            "tsa": fragments["TSA"].astype(str),
            "au_id": fragments["AU"].astype(int),
            "ifm": fragments["IFM"].astype(str),
            "age": pd.to_numeric(fragments["F_AGE"], errors="coerce")
            .fillna(0)
            .astype(int),
            "area_ha": pd.to_numeric(fragments["AREA_HA"], errors="coerce").fillna(0.0),
        }
    )


def export_woodstock_package(
    *,
    bundle_dir: Path,
    checkpoint_path: Path,
    output_dir: Path = DEFAULT_WOODSTOCK_OUTPUT_DIR,
    tsa_list: Iterable[str],
    fragments_crs: str = DEFAULT_FRAGMENTS_CRS,
) -> WoodstockExportResult:
    """Export Woodstock compatibility CSV package from FEMIC outputs."""
    normalized_tsa = sorted({normalize_tsa_code(tsa) for tsa in tsa_list})
    if not normalized_tsa:
        raise ValueError("provide at least one TSA code for Woodstock export")

    context = build_bundle_model_context(
        bundle_dir=bundle_dir,
        tsa_list=normalized_tsa,
    )
    au_table = _context_to_au_table(context)

    yields = build_woodstock_yields_table(
        context=context,
    )
    areas = build_woodstock_areas_table(
        checkpoint_path=checkpoint_path,
        au_table=au_table,
        tsa_list=normalized_tsa,
        fragments_crs=fragments_crs,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    yields_path = output_dir / "woodstock_yields.csv"
    areas_path = output_dir / "woodstock_areas.csv"
    yields.to_csv(yields_path, index=False)
    areas.to_csv(areas_path, index=False)

    return WoodstockExportResult(
        yields_csv_path=yields_path,
        areas_csv_path=areas_path,
        tsa_list=normalized_tsa,
        yield_rows=int(yields.shape[0]),
        area_rows=int(areas.shape[0]),
    )
