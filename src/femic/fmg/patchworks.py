"""Patchworks export helpers (ForestModel XML + fragments shapefile)."""

from __future__ import annotations

from dataclasses import dataclass
import importlib
from pathlib import Path
from typing import Any, Iterable
import xml.etree.ElementTree as et

import numpy as np
import pandas as pd


DEFAULT_START_YEAR = 2026
DEFAULT_HORIZON_YEARS = 300
DEFAULT_CC_MIN_AGE = 0
DEFAULT_CC_MAX_AGE = 1000
DEFAULT_FRAGMENTS_CRS = "EPSG:3005"


@dataclass(frozen=True)
class PatchworksExportResult:
    """Paths and counts from a Patchworks package export."""

    forestmodel_xml_path: Path
    fragments_shapefile_path: Path
    tsa_list: list[str]
    au_count: int
    fragment_count: int
    curve_count: int


def _normalize_tsa_code(value: Any) -> str:
    code = str(value).strip()
    if code.isdigit():
        return code.zfill(2)
    return code.lower()


def _coerce_int(value: Any) -> int:
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return int(value)
    return int(str(value))


def _load_bundle_tables(
    bundle_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    au_table = pd.read_csv(bundle_dir / "au_table.csv")
    curve_table = pd.read_csv(bundle_dir / "curve_table.csv")
    curve_points_table = pd.read_csv(bundle_dir / "curve_points_table.csv")
    return au_table, curve_table, curve_points_table


def _dedupe_au_table(au_table: pd.DataFrame) -> pd.DataFrame:
    if "au_id" not in au_table.columns:
        raise ValueError("au_table.csv missing required column: au_id")
    ordered = au_table.copy()
    deduped = (
        ordered.sort_values(["au_id"])
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
    deduped["au_id"] = deduped["au_id"].astype(int)
    deduped["managed_curve_id"] = deduped["managed_curve_id"].astype(int)
    deduped["unmanaged_curve_id"] = deduped["unmanaged_curve_id"].astype(int)
    return deduped


def _curve_points_by_id(
    curve_points_table: pd.DataFrame,
) -> dict[int, list[tuple[float, float]]]:
    points: dict[int, list[tuple[float, float]]] = {}
    if not {"curve_id", "x", "y"}.issubset(curve_points_table.columns):
        raise ValueError(
            "curve_points_table.csv missing required columns: curve_id,x,y"
        )
    for curve_id_raw, subdf in curve_points_table.groupby("curve_id"):
        rows = subdf.sort_values("x")
        curve_id = _coerce_int(curve_id_raw)
        points[int(curve_id)] = [
            (float(x), float(y)) for x, y in zip(rows["x"].tolist(), rows["y"].tolist())
        ]
    return points


def _species_curve_maps(
    curve_table: pd.DataFrame,
) -> tuple[dict[int, dict[str, int]], dict[int, dict[str, int]]]:
    managed: dict[int, dict[str, int]] = {}
    unmanaged: dict[int, dict[str, int]] = {}
    if not {"curve_id", "curve_type"}.issubset(curve_table.columns):
        return managed, unmanaged
    for _, row in curve_table.iterrows():
        curve_id = _coerce_int(row["curve_id"])
        curve_type = str(row["curve_type"])
        if curve_type.startswith("managed_species_prop_"):
            species = curve_type.removeprefix("managed_species_prop_")
            base = curve_id // 1000
            managed.setdefault(base, {})[species] = curve_id
        elif curve_type.startswith("unmanaged_species_prop_"):
            species = curve_type.removeprefix("unmanaged_species_prop_")
            base = curve_id // 1000
            unmanaged.setdefault(base, {})[species] = curve_id
    return managed, unmanaged


def _add_attribute_with_curve_ref(
    parent: et.Element,
    *,
    label: str,
    curve_ref: str,
) -> None:
    attr = et.SubElement(parent, "attribute", {"label": label})
    et.SubElement(attr, "curve", {"idref": curve_ref})


def _coerce_geometry(value: Any) -> Any:
    """Normalize geometry payloads loaded from checkpoint feather files."""
    if value is None:
        return None
    if hasattr(value, "geom_type") and hasattr(value, "is_valid"):
        return value
    if isinstance(value, memoryview):
        value = value.tobytes()
    if isinstance(value, (bytes, bytearray)):
        shapely_wkb = importlib.import_module("shapely.wkb")
        return shapely_wkb.loads(bytes(value))
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            shapely_wkb = importlib.import_module("shapely.wkb")
            return shapely_wkb.loads(text, hex=True)
        except Exception:
            return value
    return value


def _gpd_module() -> Any:
    return importlib.import_module("geopandas")


def build_forestmodel_xml_tree(
    *,
    au_table: pd.DataFrame,
    curve_table: pd.DataFrame,
    curve_points_table: pd.DataFrame,
    start_year: int = DEFAULT_START_YEAR,
    horizon_years: int = DEFAULT_HORIZON_YEARS,
    cc_min_age: int = DEFAULT_CC_MIN_AGE,
    cc_max_age: int = DEFAULT_CC_MAX_AGE,
) -> et.Element:
    """Build a Patchworks ForestModel XML tree from FEMIC bundle tables."""
    deduped_au = _dedupe_au_table(au_table=au_table)
    point_map = _curve_points_by_id(curve_points_table=curve_points_table)
    managed_species_map, unmanaged_species_map = _species_curve_maps(
        curve_table=curve_table
    )

    root = et.Element(
        "ForestModel",
        {
            "description": "FEMIC Patchworks export",
            "horizon": str(int(horizon_years)),
            "year": str(int(start_year)),
            "match": "multi",
        },
    )
    et.SubElement(
        root,
        "input",
        {"block": "BLOCK", "area": "AREA_HA", "age": "F_AGE", "exclude": "BLOCK=0"},
    )
    et.SubElement(
        root,
        "output",
        {
            "messages": "messages.csv",
            "blocks": "blocks.csv",
            "features": "features.csv",
            "products": "products.csv",
            "treatments": "treatments.csv",
            "curves": "curves.csv",
            "tracknames": "tracknames.csv",
        },
    )
    et.SubElement(root, "define", {"field": "AU", "column": "AU"})
    et.SubElement(root, "define", {"field": "IFM", "column": "IFM"})
    et.SubElement(root, "define", {"field": "treatment"})

    unity_curve = et.SubElement(root, "curve", {"id": "unity"})
    et.SubElement(unity_curve, "point", {"x": "0.0", "y": "1.0"})

    curve_ids = sorted({int(v) for v in curve_table["curve_id"].tolist()})
    for curve_id in curve_ids:
        points = point_map.get(curve_id, [])
        if not points:
            continue
        curve = et.SubElement(root, "curve", {"id": f"C{curve_id}"})
        for x, y in points:
            et.SubElement(curve, "point", {"x": f"{x:.6f}", "y": f"{y:.6f}"})

    for _, row in deduped_au.iterrows():
        au_id = _coerce_int(row["au_id"])
        unmanaged_curve_id = _coerce_int(row["unmanaged_curve_id"])
        managed_curve_id = _coerce_int(row["managed_curve_id"])

        unmanaged_select = et.SubElement(
            root, "select", {"statement": f"AU eq '{au_id}' and IFM eq 'unmanaged'"}
        )
        unmanaged_features = et.SubElement(unmanaged_select, "features")
        _add_attribute_with_curve_ref(
            unmanaged_features, label="feature.Area.unmanaged", curve_ref="unity"
        )
        _add_attribute_with_curve_ref(
            unmanaged_features,
            label="feature.Yield.unmanaged.Total",
            curve_ref=f"C{unmanaged_curve_id}",
        )
        for species, species_curve_id in sorted(
            unmanaged_species_map.get(unmanaged_curve_id, {}).items()
        ):
            _add_attribute_with_curve_ref(
                unmanaged_features,
                label=f"feature.SpeciesProp.unmanaged.{species}",
                curve_ref=f"C{species_curve_id}",
            )
        et.SubElement(unmanaged_select, "track")

        managed_select = et.SubElement(
            root, "select", {"statement": f"AU eq '{au_id}' and IFM eq 'managed'"}
        )
        managed_features = et.SubElement(managed_select, "features")
        _add_attribute_with_curve_ref(
            managed_features, label="feature.Area.managed", curve_ref="unity"
        )
        _add_attribute_with_curve_ref(
            managed_features,
            label="feature.Yield.managed.Total",
            curve_ref=f"C{managed_curve_id}",
        )
        for species, species_curve_id in sorted(
            managed_species_map.get(managed_curve_id, {}).items()
        ):
            _add_attribute_with_curve_ref(
                managed_features,
                label=f"feature.SpeciesProp.managed.{species}",
                curve_ref=f"C{species_curve_id}",
            )

        track = et.SubElement(managed_select, "track")
        treatment = et.SubElement(
            track,
            "treatment",
            {
                "label": "CC",
                "minage": str(int(cc_min_age)),
                "maxage": str(int(cc_max_age)),
            },
        )
        produce = et.SubElement(treatment, "produce")
        et.SubElement(produce, "assign", {"field": "treatment", "value": "'CC'"})

        product_select = et.SubElement(
            root,
            "select",
            {
                "statement": f"AU eq '{au_id}' and IFM eq 'managed' and treatment eq 'CC'"
            },
        )
        products = et.SubElement(product_select, "products")
        _add_attribute_with_curve_ref(
            products, label="product.Treated.managed.CC", curve_ref="unity"
        )
        _add_attribute_with_curve_ref(
            products,
            label="product.Yield.managed.Total",
            curve_ref=f"C{managed_curve_id}",
        )
        for species, species_curve_id in sorted(
            managed_species_map.get(managed_curve_id, {}).items()
        ):
            _add_attribute_with_curve_ref(
                products,
                label=f"product.SpeciesProp.managed.{species}",
                curve_ref=f"C{species_curve_id}",
            )

    return root


def write_forestmodel_xml(*, root: et.Element, path: Path) -> None:
    """Write ForestModel XML tree with Patchworks DTD header."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tree = et.ElementTree(root)
    et.indent(tree, space="  ")
    xml_body = et.tostring(root, encoding="unicode")
    payload = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE ForestModel SYSTEM "ForestModel.dtd">\n'
        f"{xml_body}\n"
    )
    path.write_text(payload, encoding="utf-8")


def build_fragments_geodataframe(
    *,
    checkpoint_path: Path,
    au_table: pd.DataFrame,
    tsa_list: Iterable[str],
    fragments_crs: str = DEFAULT_FRAGMENTS_CRS,
) -> Any:
    """Build Patchworks fragments GeoDataFrame from FEMIC checkpoint output."""
    df = pd.read_feather(checkpoint_path)
    required = {"geometry", "tsa_code", "au", "PROJ_AGE_1"}
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(
            f"checkpoint missing required columns: {','.join(missing)} "
            f"({checkpoint_path})"
        )
    normalized_tsa = {_normalize_tsa_code(tsa) for tsa in tsa_list}
    au_ids = set(_dedupe_au_table(au_table=au_table)["au_id"].astype(int).tolist())
    tsa_mask = df["tsa_code"].map(_normalize_tsa_code).isin(normalized_tsa)
    scoped = df.loc[tsa_mask].copy()
    scoped = scoped[scoped["au"].notna()].copy()
    scoped["au"] = scoped["au"].astype(int)
    scoped = scoped[scoped["au"].isin(au_ids)].copy()
    scoped = scoped[scoped["geometry"].notna()].copy()
    scoped["geometry"] = scoped["geometry"].map(_coerce_geometry)
    scoped = scoped[scoped["geometry"].notna()].copy()
    if scoped.empty:
        raise ValueError("no checkpoint rows matched selected TSA/AU export filters")

    if "FEATURE_AREA_SQM" in scoped.columns:
        area_ha = pd.to_numeric(scoped["FEATURE_AREA_SQM"], errors="coerce") * 0.0001
    elif "POLYGON_AREA" in scoped.columns:
        area_ha = pd.to_numeric(scoped["POLYGON_AREA"], errors="coerce") * 0.0001
    else:
        area_ha = None

    if "thlb_raw" in scoped.columns:
        thlb_source = pd.to_numeric(scoped["thlb_raw"], errors="coerce").fillna(0)
    else:
        thlb_source = pd.Series(1.0, index=scoped.index)
    age = pd.to_numeric(scoped["PROJ_AGE_1"], errors="coerce").fillna(0).astype(int)
    out = pd.DataFrame(
        {
            "BLOCK": np.arange(1, len(scoped) + 1, dtype=int),
            "AREA_HA": area_ha if area_ha is not None else np.nan,
            "F_AGE": age,
            "AU": scoped["au"].astype(int),
            "IFM": np.where(thlb_source > 0, "managed", "unmanaged"),
            "TSA": scoped["tsa_code"].astype(str),
            "geometry": scoped["geometry"],
        }
    )
    if area_ha is None:
        gpd = _gpd_module()
        tmp = gpd.GeoDataFrame(out, geometry="geometry", crs=fragments_crs)
        out["AREA_HA"] = tmp.geometry.area * 0.0001
    out["AREA_HA"] = pd.to_numeric(out["AREA_HA"], errors="coerce").fillna(0.0)
    gpd = _gpd_module()
    return gpd.GeoDataFrame(out, geometry="geometry", crs=fragments_crs)


def write_fragments_shapefile(*, fragments_gdf: Any, path: Path) -> None:
    """Write fragments shapefile (directory + sidecar files)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fragments_gdf.to_file(path)


def export_patchworks_package(
    *,
    bundle_dir: Path,
    checkpoint_path: Path,
    output_dir: Path,
    tsa_list: Iterable[str],
    start_year: int = DEFAULT_START_YEAR,
    horizon_years: int = DEFAULT_HORIZON_YEARS,
    cc_min_age: int = DEFAULT_CC_MIN_AGE,
    cc_max_age: int = DEFAULT_CC_MAX_AGE,
    fragments_crs: str = DEFAULT_FRAGMENTS_CRS,
) -> PatchworksExportResult:
    """Export Patchworks package artifacts from FEMIC outputs."""
    normalized_tsa = sorted({_normalize_tsa_code(tsa) for tsa in tsa_list})
    if not normalized_tsa:
        raise ValueError("provide at least one TSA code for Patchworks export")

    au_table, curve_table, curve_points_table = _load_bundle_tables(
        bundle_dir=bundle_dir
    )
    au_table["tsa"] = au_table["tsa"].map(_normalize_tsa_code)
    au_table = au_table[au_table["tsa"].isin(normalized_tsa)].copy()
    if au_table.empty:
        raise ValueError("no au_table rows matched requested TSA list")

    root = build_forestmodel_xml_tree(
        au_table=au_table,
        curve_table=curve_table,
        curve_points_table=curve_points_table,
        start_year=start_year,
        horizon_years=horizon_years,
        cc_min_age=cc_min_age,
        cc_max_age=cc_max_age,
    )
    forestmodel_path = output_dir / "forestmodel.xml"
    write_forestmodel_xml(root=root, path=forestmodel_path)

    fragments_gdf = build_fragments_geodataframe(
        checkpoint_path=checkpoint_path,
        au_table=au_table,
        tsa_list=normalized_tsa,
        fragments_crs=fragments_crs,
    )
    fragments_path = output_dir / "fragments" / "fragments.shp"
    write_fragments_shapefile(fragments_gdf=fragments_gdf, path=fragments_path)

    return PatchworksExportResult(
        forestmodel_xml_path=forestmodel_path,
        fragments_shapefile_path=fragments_path,
        tsa_list=normalized_tsa,
        au_count=int(_dedupe_au_table(au_table=au_table).shape[0]),
        fragment_count=int(fragments_gdf.shape[0]),
        curve_count=int(curve_table.shape[0]),
    )
