"""Helpers for legacy stand-feature post-processing and export."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Sequence


DEFAULT_STANDS_PROP_NAMES: tuple[str, ...] = (
    "tsa_code",
    "thlb",
    "au",
    "canfi_species",
    "PROJ_AGE_1",
    "FEATURE_AREA_SQM",
)
DEFAULT_STANDS_PROP_TYPES: tuple[tuple[str, str], ...] = (
    ("theme0", "str:10"),
    ("theme1", "str:1"),
    ("theme2", "str:10"),
    ("theme3", "str:5"),
    ("age", "int:5"),
    ("area", "float:10.1"),
)

DEFAULT_STAND_FEATURE_COLUMNS: tuple[str, ...] = (
    "geometry",
    "tsa_code",
    "thlb",
    "au",
    "curve1",
    "curve2",
    "SPECIES_CD_1",
    "PROJ_AGE_1",
    "FEATURE_AREA_SQM",
)


def should_skip_stands_export(
    *,
    skip_raw: str | None,
    default_skip: bool,
) -> bool:
    """Resolve stand-export skip flag from env/raw value and default behavior."""
    if skip_raw is None:
        return bool(default_skip)
    return skip_raw.strip().lower() in ("1", "true", "yes")


def clean_stand_geometry(geometry: Any) -> Any:
    """Apply legacy geometry fixups for invalid polygon/multipolygon records."""
    if geometry.is_valid:
        return geometry
    cleaned = geometry.buffer(0)
    shapely_geometry = __import__("shapely.geometry", fromlist=["MultiPolygon"])
    cleaned_mp = shapely_geometry.MultiPolygon([cleaned])
    assert cleaned_mp.is_valid
    assert cleaned_mp.geom_type == "MultiPolygon"
    return cleaned_mp


def extract_stand_features_for_tsa(
    *,
    f_table: Any,
    tsa_code: str,
    feature_columns: Sequence[str] = DEFAULT_STAND_FEATURE_COLUMNS,
    clean_geometry_fn: Callable[[Any], Any] = clean_stand_geometry,
) -> Any:
    """Extract per-TSA stand features and apply geometry-cleanup hook."""
    frame = f_table[list(feature_columns)]
    frame = frame.set_index("tsa_code").loc[[tsa_code]].reset_index()
    frame.geometry = frame.apply(lambda r: clean_geometry_fn(r.geometry), axis=1)
    return frame


def build_stands_column_map(
    *,
    prop_names: Sequence[str] = DEFAULT_STANDS_PROP_NAMES,
    prop_types: Sequence[tuple[str, str]] = DEFAULT_STANDS_PROP_TYPES,
) -> dict[str, str]:
    """Build legacy stand-export column rename map."""
    return dict(zip(prop_names, dict(prop_types).keys()))


def prepare_stands_export_frame(
    *,
    f_tsa: Any,
    columns_map: dict[str, str],
    au_table: Any,
    pd_module: Any,
) -> Any:
    """Apply legacy theme/age/area transforms before writing stand shapefiles."""
    frame = f_tsa.copy()
    if getattr(au_table.index, "name", None) != "au_id":
        au_table = au_table.set_index("au_id")
    frame.rename(columns=columns_map, inplace=True)
    frame["theme0"] = "tsa" + frame["theme0"]
    frame["theme2"] = frame["theme2"].astype(int)
    frame["theme3"] = frame.apply(
        lambda r: au_table.loc[r["theme2"]].canfi_species,
        axis=1,
    )
    frame["age"] = frame["age"].fillna(0).astype(int)
    frame["area"] = (frame["area"] * 0.0001).round(1)
    return frame


def export_stands_shapefiles(
    *,
    tsa_list: Sequence[str],
    f_table: Any,
    au_table: Any,
    columns_map: dict[str, str],
    output_root: str | Path = "data/shp",
    pd_module: Any | None = None,
    extract_features_fn: Callable[..., Any] = extract_stand_features_for_tsa,
    prepare_frame_fn: Callable[..., Any] = prepare_stands_export_frame,
    message_fn: Callable[[str], Any] = print,
) -> None:
    """Export per-TSA stand shapefiles using legacy naming/layout conventions."""
    root = Path(output_root)
    pd_mod = pd_module or __import__("pandas")
    for tsa in tsa_list:
        message_fn(f"processing tsa {tsa}")
        f_tsa = extract_features_fn(f_table=f_table, tsa_code=tsa)
        tsa_dir = root / f"tsa{tsa}.shp"
        tsa_dir.mkdir(parents=True, exist_ok=True)
        out = prepare_frame_fn(
            f_tsa=f_tsa,
            columns_map=columns_map,
            au_table=au_table,
            pd_module=pd_mod,
        )
        out.to_file(tsa_dir / "stands.shp")
