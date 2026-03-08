"""Patchworks export helpers (ForestModel XML + fragments shapefile)."""

from __future__ import annotations

from dataclasses import dataclass
import importlib
import math
from pathlib import Path
from typing import Any, Iterable
import xml.etree.ElementTree as et

import numpy as np
import pandas as pd

from .adapters import (
    build_bundle_model_context,
    build_bundle_model_context_from_tables,
    normalize_tsa_code,
)
from .core import (
    AttributeBinding,
    BundleModelContext,
    CurvePoint,
    DefineFieldDefinition,
    ForestModelDefinition,
    SelectDefinition,
    TreatmentAssignment,
    TreatmentDefinition,
)


DEFAULT_START_YEAR = 2026
DEFAULT_HORIZON_YEARS = 300
DEFAULT_CC_MIN_AGE = 0
DEFAULT_CC_MAX_AGE = 1000
DEFAULT_CC_TRANSITION_IFM = "managed"
DEFAULT_FRAGMENTS_CRS = "EPSG:3005"
VALID_IFM_VALUES = {"managed", "unmanaged"}
REQUIRED_FRAGMENT_COLUMNS = {
    "BLOCK",
    "AREA_HA",
    "F_AGE",
    "AU",
    "IFM",
    "TSA",
    "geometry",
}


@dataclass(frozen=True)
class PatchworksExportResult:
    """Paths and counts from a Patchworks package export."""

    forestmodel_xml_path: Path
    fragments_shapefile_path: Path
    tsa_list: list[str]
    au_count: int
    fragment_count: int
    curve_count: int


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


def _as_quoted_literal(value: str) -> str:
    text = str(value).strip()
    if text.startswith("'") and text.endswith("'"):
        return text
    return f"'{text}'"


def _curve_value_at_x(*, points: tuple[CurvePoint, ...], x: float) -> float:
    """Evaluate a curve at `x` using constant or piecewise-linear interpolation."""
    finite_points = [
        (float(p.x), float(p.y))
        for p in points
        if math.isfinite(float(p.x)) and math.isfinite(float(p.y))
    ]
    if not finite_points:
        return 0.0
    if len(finite_points) == 1:
        return finite_points[0][1]
    x_points = np.array([xy[0] for xy in finite_points], dtype=float)
    y_points = np.array([xy[1] for xy in finite_points], dtype=float)
    order = np.argsort(x_points)
    x_sorted = x_points[order]
    y_sorted = y_points[order]
    return float(
        np.interp(float(x), x_sorted, y_sorted, left=y_sorted[0], right=y_sorted[-1])
    )


def _build_species_yield_curve(
    *,
    total_points: tuple[CurvePoint, ...],
    species_prop_points: tuple[CurvePoint, ...],
) -> tuple[CurvePoint, ...]:
    """Derive species yield curve as total-volume curve times species-proportion curve."""
    if not total_points or not species_prop_points:
        return ()
    derived: list[CurvePoint] = []
    for point in total_points:
        total_y = max(0.0, float(point.y))
        species_prop = _curve_value_at_x(points=species_prop_points, x=float(point.x))
        if not math.isfinite(species_prop):
            species_prop = 0.0
        species_prop = max(0.0, min(1.0, species_prop))
        derived.append(CurvePoint(x=float(point.x), y=total_y * species_prop))
    return tuple(derived)


def _derived_species_yield_curve_id(
    *, species_prop_curve_id: int, managed: bool
) -> int:
    """Build deterministic synthetic curve ID for derived species-yield curves."""
    suffix = 2 if managed else 1
    return int(species_prop_curve_id) * 10 + suffix


def _trim_flat_tail_points(
    points: tuple[CurvePoint, ...], *, abs_tol: float = 1e-12
) -> tuple[CurvePoint, ...]:
    """Drop redundant far-left/far-right points where terminal y-values repeat."""
    if len(points) <= 1:
        return points
    left = 0
    first_y = float(points[0].y)
    while left + 1 < len(points) and math.isclose(
        float(points[left + 1].y), first_y, rel_tol=0.0, abs_tol=abs_tol
    ):
        left += 1
    right = len(points) - 1
    last_y = float(points[right].y)
    while right > left and math.isclose(
        float(points[right - 1].y), last_y, rel_tol=0.0, abs_tol=abs_tol
    ):
        right -= 1
    trimmed = points[left : right + 1]
    if len(trimmed) > 1:
        return trimmed
    # Edge case: entire curve is flat; keep earliest point so XML doesn't collapse to max age.
    return (points[0],)


def _sanitize_curve_points_for_xml(
    points: tuple[CurvePoint, ...], *, abs_tol: float = 1e-12
) -> tuple[CurvePoint, ...]:
    """Sanitize points for ForestModel XML (finite numeric values, monotonic x, no duplicate x)."""
    finite: list[CurvePoint] = []
    for point in points:
        x_val = float(point.x)
        y_val = float(point.y)
        if not math.isfinite(x_val):
            continue
        if not math.isfinite(y_val):
            y_val = 0.0
        finite.append(CurvePoint(x=x_val, y=y_val))
    if not finite:
        return ()
    finite = sorted(finite, key=lambda p: p.x)
    deduped: list[CurvePoint] = []
    for point in finite:
        if deduped and math.isclose(
            point.x, deduped[-1].x, rel_tol=0.0, abs_tol=abs_tol
        ):
            deduped[-1] = point
        else:
            deduped.append(point)
    return tuple(deduped)


def _gpd_module() -> Any:
    return importlib.import_module("geopandas")


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


def build_forestmodel_xml_tree(
    *,
    au_table: pd.DataFrame,
    curve_table: pd.DataFrame,
    curve_points_table: pd.DataFrame,
    start_year: int = DEFAULT_START_YEAR,
    horizon_years: int = DEFAULT_HORIZON_YEARS,
    cc_min_age: int = DEFAULT_CC_MIN_AGE,
    cc_max_age: int = DEFAULT_CC_MAX_AGE,
    cc_transition_ifm: str | None = DEFAULT_CC_TRANSITION_IFM,
) -> et.Element:
    """Build a Patchworks ForestModel XML tree from FEMIC bundle tables."""
    context = build_bundle_model_context_from_tables(
        au_table=au_table,
        curve_table=curve_table,
        curve_points_table=curve_points_table,
        tsa_list=None,
    )
    return build_forestmodel_xml_tree_from_context(
        context=context,
        start_year=start_year,
        horizon_years=horizon_years,
        cc_min_age=cc_min_age,
        cc_max_age=cc_max_age,
        cc_transition_ifm=cc_transition_ifm,
    )


def build_forestmodel_xml_tree_from_context(
    *,
    context: BundleModelContext,
    start_year: int = DEFAULT_START_YEAR,
    horizon_years: int = DEFAULT_HORIZON_YEARS,
    cc_min_age: int = DEFAULT_CC_MIN_AGE,
    cc_max_age: int = DEFAULT_CC_MAX_AGE,
    cc_transition_ifm: str | None = DEFAULT_CC_TRANSITION_IFM,
) -> et.Element:
    """Build a Patchworks ForestModel XML tree from shared FMG context."""
    definition = build_patchworks_forestmodel_definition(
        context=context,
        start_year=start_year,
        horizon_years=horizon_years,
        cc_min_age=cc_min_age,
        cc_max_age=cc_max_age,
        cc_transition_ifm=cc_transition_ifm,
    )
    return forestmodel_definition_to_xml_tree(definition=definition)


def build_patchworks_forestmodel_definition(
    *,
    context: BundleModelContext,
    start_year: int = DEFAULT_START_YEAR,
    horizon_years: int = DEFAULT_HORIZON_YEARS,
    cc_min_age: int = DEFAULT_CC_MIN_AGE,
    cc_max_age: int = DEFAULT_CC_MAX_AGE,
    cc_transition_ifm: str | None = DEFAULT_CC_TRANSITION_IFM,
) -> ForestModelDefinition:
    """Build Patchworks ForestModel core definition from shared context."""
    curves: dict[str, tuple[CurvePoint, ...]] = {"unity": (CurvePoint(x=0.0, y=1.0),)}
    for curve_id in sorted(context.curves_by_id):
        points = context.curves_by_id[curve_id].points
        if points:
            curves[f"C{curve_id}"] = points

    selects: list[SelectDefinition] = []
    transition_assignments: tuple[TreatmentAssignment, ...] = ()
    if cc_transition_ifm is not None and str(cc_transition_ifm).strip():
        transition_assignments = (
            TreatmentAssignment(
                field="IFM",
                value=_as_quoted_literal(cc_transition_ifm),
            ),
        )
    for au in context.analysis_units:
        unmanaged_curve_id = au.unmanaged_curve_id
        managed_curve_id = au.managed_curve_id
        unmanaged_total_curve = context.curves_by_id.get(unmanaged_curve_id)
        managed_total_curve = context.curves_by_id.get(managed_curve_id)

        unmanaged_attrs = [
            AttributeBinding(label="feature.Area.unmanaged", curve_idref="unity"),
            AttributeBinding(
                label="feature.Yield.unmanaged.Total",
                curve_idref=f"C{unmanaged_curve_id}",
            ),
        ]
        for species, species_curve_id in sorted(
            context.unmanaged_species_curve_ids.get(unmanaged_curve_id, {}).items()
        ):
            if unmanaged_total_curve is not None:
                species_prop_curve = context.curves_by_id.get(species_curve_id)
                if species_prop_curve is not None:
                    derived_curve_id = _derived_species_yield_curve_id(
                        species_prop_curve_id=species_curve_id,
                        managed=False,
                    )
                    derived_curve_points = _build_species_yield_curve(
                        total_points=unmanaged_total_curve.points,
                        species_prop_points=species_prop_curve.points,
                    )
                    if derived_curve_points:
                        curves[f"C{derived_curve_id}"] = derived_curve_points
                        unmanaged_attrs.append(
                            AttributeBinding(
                                label=f"feature.Yield.unmanaged.{species}",
                                curve_idref=f"C{derived_curve_id}",
                            )
                        )
            unmanaged_attrs.append(
                AttributeBinding(
                    label=f"feature.SpeciesProp.unmanaged.{species}",
                    curve_idref=f"C{species_curve_id}",
                )
            )
        selects.append(
            SelectDefinition(
                statement=f"AU eq '{au.au_id}' and IFM eq 'unmanaged'",
                feature_attributes=tuple(unmanaged_attrs),
                include_track=True,
            )
        )

        managed_attrs = [
            AttributeBinding(label="feature.Area.managed", curve_idref="unity"),
            AttributeBinding(
                label="feature.Yield.managed.Total",
                curve_idref=f"C{managed_curve_id}",
            ),
        ]
        product_attrs = [
            AttributeBinding(label="product.Treated.managed.CC", curve_idref="unity"),
            AttributeBinding(
                label="product.Yield.managed.Total",
                curve_idref=f"C{managed_curve_id}",
            ),
        ]
        for species, species_curve_id in sorted(
            context.managed_species_curve_ids.get(managed_curve_id, {}).items()
        ):
            if managed_total_curve is not None:
                species_prop_curve = context.curves_by_id.get(species_curve_id)
                if species_prop_curve is not None:
                    derived_curve_id = _derived_species_yield_curve_id(
                        species_prop_curve_id=species_curve_id,
                        managed=True,
                    )
                    derived_curve_points = _build_species_yield_curve(
                        total_points=managed_total_curve.points,
                        species_prop_points=species_prop_curve.points,
                    )
                    if derived_curve_points:
                        curves[f"C{derived_curve_id}"] = derived_curve_points
                        managed_attrs.append(
                            AttributeBinding(
                                label=f"feature.Yield.managed.{species}",
                                curve_idref=f"C{derived_curve_id}",
                            )
                        )
                        product_attrs.append(
                            AttributeBinding(
                                label=f"product.Yield.managed.{species}",
                                curve_idref=f"C{derived_curve_id}",
                            )
                        )
            managed_attrs.append(
                AttributeBinding(
                    label=f"feature.SpeciesProp.managed.{species}",
                    curve_idref=f"C{species_curve_id}",
                )
            )
            product_attrs.append(
                AttributeBinding(
                    label=f"product.SpeciesProp.managed.{species}",
                    curve_idref=f"C{species_curve_id}",
                )
            )

        selects.append(
            SelectDefinition(
                statement=f"AU eq '{au.au_id}' and IFM eq 'managed'",
                feature_attributes=tuple(managed_attrs),
                include_track=True,
                track_treatment=TreatmentDefinition(
                    label="CC",
                    min_age=int(cc_min_age),
                    max_age=int(cc_max_age),
                    assignments=(
                        TreatmentAssignment(
                            field="treatment",
                            value=_as_quoted_literal("CC"),
                        ),
                    ),
                    transition_assignments=transition_assignments,
                ),
            )
        )
        selects.append(
            SelectDefinition(
                statement=(
                    f"AU eq '{au.au_id}' and IFM eq 'managed' and treatment eq 'CC'"
                ),
                product_attributes=tuple(product_attrs),
            )
        )

    return ForestModelDefinition(
        description="FEMIC Patchworks export",
        horizon=int(horizon_years),
        year=int(start_year),
        match="multi",
        input_attributes={
            "block": "BLOCK",
            "area": "AREA_HA",
            "age": "F_AGE",
            "exclude": "BLOCK=0",
        },
        output_attributes={
            "messages": "messages.csv",
            "blocks": "blocks.csv",
            "features": "features.csv",
            "products": "products.csv",
            "treatments": "treatments.csv",
            "curves": "curves.csv",
            "tracknames": "tracknames.csv",
        },
        define_fields=(
            DefineFieldDefinition(field="AU", column="AU"),
            DefineFieldDefinition(field="IFM", column="IFM"),
            DefineFieldDefinition(field="treatment"),
        ),
        curves=curves,
        selects=tuple(selects),
    )


def _append_attribute_bindings(
    *,
    parent: et.Element,
    tag_name: str,
    bindings: tuple[AttributeBinding, ...],
) -> None:
    node = et.SubElement(parent, tag_name)
    for binding in bindings:
        attr = et.SubElement(node, "attribute", {"label": binding.label})
        et.SubElement(attr, "curve", {"idref": binding.curve_idref})


def _append_track(
    *,
    parent: et.Element,
    include_track: bool,
    track_treatment: TreatmentDefinition | None,
) -> None:
    if not include_track and track_treatment is None:
        return
    track = et.SubElement(parent, "track")
    if track_treatment is None:
        return
    treatment = et.SubElement(
        track,
        "treatment",
        {
            "label": track_treatment.label,
            "minage": str(int(track_treatment.min_age)),
            "maxage": str(int(track_treatment.max_age)),
        },
    )
    if not track_treatment.assignments:
        pass
    else:
        produce = et.SubElement(treatment, "produce")
        for assignment in track_treatment.assignments:
            et.SubElement(
                produce,
                "assign",
                {"field": assignment.field, "value": assignment.value},
            )
    if not track_treatment.transition_assignments:
        return
    transition = et.SubElement(treatment, "transition")
    for assignment in track_treatment.transition_assignments:
        et.SubElement(
            transition,
            "assign",
            {"field": assignment.field, "value": assignment.value},
        )


def forestmodel_definition_to_xml_tree(
    *,
    definition: ForestModelDefinition,
) -> et.Element:
    """Serialize ForestModel core definition to XML tree."""
    root = et.Element(
        "ForestModel",
        {
            "description": definition.description,
            "horizon": str(int(definition.horizon)),
            "year": str(int(definition.year)),
            "match": definition.match,
        },
    )
    et.SubElement(root, "input", definition.input_attributes)
    et.SubElement(root, "output", definition.output_attributes)

    for define_field in definition.define_fields:
        attrs = {"field": define_field.field}
        if define_field.column is not None:
            attrs["column"] = define_field.column
        et.SubElement(root, "define", attrs)

    curve_ids = ["unity"] if "unity" in definition.curves else []
    curve_ids.extend(
        sorted(
            [cid for cid in definition.curves if cid != "unity"],
            key=lambda cid: int(cid.removeprefix("C")),
        )
    )
    for curve_id in curve_ids:
        curve_node = et.SubElement(root, "curve", {"id": curve_id})
        points = _sanitize_curve_points_for_xml(definition.curves[curve_id])
        if curve_id != "unity":
            points = _trim_flat_tail_points(points)
        if not points and curve_id == "unity":
            points = (CurvePoint(x=0.0, y=1.0),)
        elif not points:
            points = (CurvePoint(x=0.0, y=0.0),)
        for point in points:
            if curve_id == "unity":
                x_val = str(point.x)
                y_val = str(point.y)
            else:
                x_val = f"{point.x:.6f}"
                y_val = f"{point.y:.6f}"
            et.SubElement(
                curve_node,
                "point",
                {"x": x_val, "y": y_val},
            )

    for select in definition.selects:
        select_node = et.SubElement(root, "select", {"statement": select.statement})
        if select.feature_attributes:
            _append_attribute_bindings(
                parent=select_node,
                tag_name="features",
                bindings=select.feature_attributes,
            )
        _append_track(
            parent=select_node,
            include_track=select.include_track,
            track_treatment=select.track_treatment,
        )
        if select.product_attributes:
            _append_attribute_bindings(
                parent=select_node,
                tag_name="products",
                bindings=select.product_attributes,
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


def validate_forestmodel_xml_tree(*, root: et.Element) -> None:
    """Validate required ForestModel structure and curve references."""
    issues: list[str] = []
    if root.tag != "ForestModel":
        issues.append(f"root tag must be ForestModel (found {root.tag!r})")

    for attr in ("horizon", "year", "match"):
        if not root.get(attr):
            issues.append(f"ForestModel missing required attribute: {attr}")

    input_nodes = root.findall("./input")
    if not input_nodes:
        issues.append("ForestModel missing <input> node")
    else:
        required_input_attrs = {"block", "area", "age"}
        for attr in required_input_attrs:
            if not input_nodes[0].get(attr):
                issues.append(f"<input> missing required attribute: {attr}")

    output_nodes = root.findall("./output")
    if not output_nodes:
        issues.append("ForestModel missing <output> node")

    define_fields = {
        field
        for node in root.findall("./define")
        for field in [node.get("field")]
        if field is not None
    }
    for field in ("AU", "IFM", "treatment"):
        if field not in define_fields:
            issues.append(f"missing define field: {field}")

    curve_ids = {
        curve_id
        for node in root.findall(".//curve")
        for curve_id in [node.get("id")]
        if isinstance(curve_id, str)
    }
    if "unity" not in curve_ids:
        issues.append("missing required curve id 'unity'")
    if not root.findall("./curve[@id='unity']/point"):
        issues.append("unity curve missing point(s)")

    idrefs = {
        idref
        for node in root.findall(".//attribute/curve")
        for idref in [node.get("idref")]
        if isinstance(idref, str)
    }
    missing_idrefs = sorted(ref for ref in idrefs if ref not in curve_ids)
    if missing_idrefs:
        issues.append(
            f"attribute curve idref(s) missing matching curve: {missing_idrefs}"
        )

    if not root.findall(".//treatment[@label='CC']"):
        issues.append("missing required CC treatment definition")

    if issues:
        raise ValueError("invalid ForestModel XML tree: " + "; ".join(issues))


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
    if "au_id" not in au_table.columns:
        raise ValueError("au_table missing required column: au_id")
    normalized_tsa = {normalize_tsa_code(tsa) for tsa in tsa_list}
    au_ids = set(pd.to_numeric(au_table["au_id"], errors="coerce").dropna().astype(int))
    tsa_mask = df["tsa_code"].map(normalize_tsa_code).isin(normalized_tsa)
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


def validate_fragments_geodataframe(*, fragments_gdf: Any) -> None:
    """Validate required Patchworks fragments fields and value domains."""
    issues: list[str] = []
    missing_columns = sorted(
        REQUIRED_FRAGMENT_COLUMNS.difference(fragments_gdf.columns)
    )
    if missing_columns:
        issues.append(f"missing required fragments columns: {missing_columns}")
    if fragments_gdf.empty:
        issues.append("fragments dataset is empty")

    if fragments_gdf.crs is None:
        issues.append("fragments CRS is missing")

    if "geometry" in fragments_gdf.columns:
        if fragments_gdf["geometry"].isna().any():
            issues.append("fragments contains null geometry")
        elif fragments_gdf.geometry.is_empty.any():
            issues.append("fragments contains empty geometry")

    for col in ("BLOCK", "F_AGE", "AU"):
        if col in fragments_gdf.columns:
            numeric = pd.to_numeric(fragments_gdf[col], errors="coerce")
            if numeric.isna().any():
                issues.append(f"{col} contains non-numeric value(s)")
            elif (numeric < 0).any():
                issues.append(f"{col} contains negative value(s)")

    if "BLOCK" in fragments_gdf.columns:
        block_values = pd.to_numeric(fragments_gdf["BLOCK"], errors="coerce")
        if block_values.duplicated().any():
            issues.append("BLOCK values must be unique")

    if "AREA_HA" in fragments_gdf.columns:
        area = pd.to_numeric(fragments_gdf["AREA_HA"], errors="coerce")
        if area.isna().any():
            issues.append("AREA_HA contains non-numeric value(s)")
        elif (area <= 0).any():
            issues.append("AREA_HA must be strictly positive")

    if "IFM" in fragments_gdf.columns:
        ifm_values = set(
            fragments_gdf["IFM"].astype(str).str.strip().str.lower().unique()
        )
        invalid_ifm = sorted(ifm_values.difference(VALID_IFM_VALUES))
        if invalid_ifm:
            issues.append(f"IFM contains invalid values: {invalid_ifm}")

    if issues:
        raise ValueError("invalid fragments dataset: " + "; ".join(issues))


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
    cc_transition_ifm: str | None = DEFAULT_CC_TRANSITION_IFM,
    fragments_crs: str = DEFAULT_FRAGMENTS_CRS,
) -> PatchworksExportResult:
    """Export Patchworks package artifacts from FEMIC outputs."""
    normalized_tsa = sorted({normalize_tsa_code(tsa) for tsa in tsa_list})
    if not normalized_tsa:
        raise ValueError("provide at least one TSA code for Patchworks export")
    context = build_bundle_model_context(
        bundle_dir=bundle_dir,
        tsa_list=normalized_tsa,
    )
    au_table = _context_to_au_table(context)

    root = build_forestmodel_xml_tree_from_context(
        context=context,
        start_year=start_year,
        horizon_years=horizon_years,
        cc_min_age=cc_min_age,
        cc_max_age=cc_max_age,
        cc_transition_ifm=cc_transition_ifm,
    )
    validate_forestmodel_xml_tree(root=root)
    forestmodel_path = output_dir / "forestmodel.xml"
    write_forestmodel_xml(root=root, path=forestmodel_path)

    fragments_gdf = build_fragments_geodataframe(
        checkpoint_path=checkpoint_path,
        au_table=au_table,
        tsa_list=normalized_tsa,
        fragments_crs=fragments_crs,
    )
    validate_fragments_geodataframe(fragments_gdf=fragments_gdf)
    fragments_path = output_dir / "fragments" / "fragments.shp"
    write_fragments_shapefile(fragments_gdf=fragments_gdf, path=fragments_path)

    return PatchworksExportResult(
        forestmodel_xml_path=forestmodel_path,
        fragments_shapefile_path=fragments_path,
        tsa_list=normalized_tsa,
        au_count=int(len(context.analysis_units)),
        fragment_count=int(fragments_gdf.shape[0]),
        curve_count=int(len(root.findall("./curve"))),
    )
