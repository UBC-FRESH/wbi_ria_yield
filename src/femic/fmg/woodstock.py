"""Woodstock compatibility export helpers (CSV package from FEMIC bundle outputs)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

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


def _normalize_tsa_code(value: Any) -> str:
    code = str(value).strip()
    if code.isdigit():
        return code.zfill(2)
    return code.lower()


def _coerce_int(value: Any) -> int:
    if isinstance(value, int):
        return value
    return int(str(value))


def _load_bundle_tables(bundle_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    au_table = pd.read_csv(bundle_dir / "au_table.csv")
    curve_points_table = pd.read_csv(bundle_dir / "curve_points_table.csv")
    return au_table, curve_points_table


def build_woodstock_yields_table(
    *,
    au_table: pd.DataFrame,
    curve_points_table: pd.DataFrame,
) -> pd.DataFrame:
    """Build long-format Woodstock compatibility yields table."""
    rows: list[dict[str, Any]] = []
    deduped = (
        au_table.sort_values(["au_id"])
        .groupby("au_id", as_index=False)
        .agg(
            {
                "tsa": "first",
                "stratum_code": "first",
                "si_level": "first",
                "managed_curve_id": "first",
                "unmanaged_curve_id": "first",
            }
        )
    )
    points = curve_points_table.copy()
    points["curve_id"] = pd.to_numeric(points["curve_id"], errors="coerce").astype(int)
    points["x"] = pd.to_numeric(points["x"], errors="coerce")
    points["y"] = pd.to_numeric(points["y"], errors="coerce")

    for row in deduped.itertuples(index=False):
        au_id = _coerce_int(row.au_id)
        tsa = str(row.tsa)
        stratum_code = str(row.stratum_code)
        si_level = str(row.si_level)
        for ifm, curve_id in (
            ("unmanaged", _coerce_int(row.unmanaged_curve_id)),
            ("managed", _coerce_int(row.managed_curve_id)),
        ):
            sub = points.loc[points["curve_id"] == curve_id, ["x", "y"]].sort_values(
                "x"
            )
            for x, y in zip(sub["x"].tolist(), sub["y"].tolist()):
                rows.append(
                    {
                        "tsa": tsa,
                        "au_id": au_id,
                        "stratum_code": stratum_code,
                        "si_level": si_level,
                        "ifm": ifm,
                        "curve_id": curve_id,
                        "age": int(x),
                        "volume": float(y),
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
    normalized_tsa = sorted({_normalize_tsa_code(tsa) for tsa in tsa_list})
    if not normalized_tsa:
        raise ValueError("provide at least one TSA code for Woodstock export")

    au_table, curve_points_table = _load_bundle_tables(bundle_dir=bundle_dir)
    au_table["tsa"] = au_table["tsa"].map(_normalize_tsa_code)
    au_table = au_table[au_table["tsa"].isin(normalized_tsa)].copy()
    if au_table.empty:
        raise ValueError("no au_table rows matched requested TSA list")

    yields = build_woodstock_yields_table(
        au_table=au_table,
        curve_points_table=curve_points_table,
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
