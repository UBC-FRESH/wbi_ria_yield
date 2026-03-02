"""Helpers for legacy VRI table normalization/filtering stages."""

from __future__ import annotations

from typing import Any, Sequence


def is_conifer_species_code(species_code: str) -> bool:
    """Return True if species code represents a conifer species."""
    return str(species_code)[:1] in ["B", "C", "F", "H", "J", "L", "P", "S", "T", "Y"]


def is_deciduous_species_code(species_code: str) -> bool:
    """Return True if species code represents a deciduous species."""
    return str(species_code)[:1] in ["A", "D", "E", "G", "M", "Q", "R", "U", "V", "W"]


def pconif(
    row: Any,
    *,
    species_slot_count: int = 6,
) -> float:
    """Return conifer percent share from species-percent slots."""
    return (
        sum(
            row[f"SPECIES_PCT_{idx}"]
            for idx in range(1, int(species_slot_count) + 1)
            if is_conifer_species_code(row[f"SPECIES_CD_{idx}"])
        )
        / 100.0
    )


def pdecid(
    row: Any,
    *,
    species_slot_count: int = 6,
) -> float:
    """Return deciduous percent share from species-percent slots."""
    return (
        sum(
            row[f"SPECIES_PCT_{idx}"]
            for idx in range(1, int(species_slot_count) + 1)
            if is_deciduous_species_code(row[f"SPECIES_CD_{idx}"])
        )
        / 100.0
    )


def classify_stand_cdm(row: Any) -> str:
    """Classify stand as conifer/deciduous/mixed (c/d/m)."""
    if pconif(row) >= 0.8:
        return "c"
    if pdecid(row) >= 0.8:
        return "d"
    return "m"


def classify_stand_forest_type(row: Any) -> int:
    """Classify stand into 1..4 forest-type classes from conifer proportion."""
    conif_share = pconif(row)
    if conif_share >= 0.75:
        return 1
    if conif_share >= 0.50:
        return 2
    if conif_share >= 0.25:
        return 3
    return 4


def assign_forest_type_from_species_pct(
    *,
    f_table: Any,
    out_col: str = "forest_type",
    apply_fn: Any | None = None,
    classify_fn: Any = classify_stand_forest_type,
) -> Any:
    """Assign forest-type class column using supplied row-apply callable."""
    table = f_table.copy()
    if apply_fn is None:
        apply_fn = table.apply
        table[out_col] = apply_fn(classify_fn, axis=1)
    else:
        table[out_col] = apply_fn(table, classify_fn, axis=1)
    return table


def normalize_and_filter_checkpoint2_records(
    *,
    f_table: Any,
    species_slot_count: int = 6,
    fill_token: str = "X",
    excluded_bec_zones: Sequence[str] = ("BAFA", "IMA"),
    required_bclcs_level_2: str = "T",
    required_for_mgmt_land_base: str = "Y",
    min_proj_age: int = 30,
    min_basal_area: int = 5,
    min_live_stand_volume: int = 1,
) -> Any:
    """Apply legacy checkpoint2 fillna defaults and row filters."""
    table = f_table.copy()
    pd_module = __import__("pandas")

    for idx in range(1, int(species_slot_count) + 1):
        species_col = f"SPECIES_CD_{idx}"
        species_pct_col = f"SPECIES_PCT_{idx}"
        live_vol_col = f"LIVE_VOL_PER_HA_SPP{idx}_125"
        table[species_col] = table[species_col].fillna(fill_token)
        table[species_pct_col] = pd_module.to_numeric(
            table[species_pct_col], errors="coerce"
        ).fillna(0)
        table[live_vol_col] = pd_module.to_numeric(
            table[live_vol_col], errors="coerce"
        ).fillna(0)

    for column in (
        "SOIL_NUTRIENT_REGIME",
        "SOIL_MOISTURE_REGIME_1",
        "SITE_POSITION_MESO",
        "BCLCS_LEVEL_3",
        "BCLCS_LEVEL_4",
        "BCLCS_LEVEL_5",
        "BEC_VARIANT",
    ):
        table[column] = table[column].fillna(fill_token)
    table["LIVE_STAND_VOLUME_125"] = pd_module.to_numeric(
        table["LIVE_STAND_VOLUME_125"], errors="coerce"
    ).fillna(0)
    table["PROJ_AGE_1"] = pd_module.to_numeric(table["PROJ_AGE_1"], errors="coerce")
    table["BASAL_AREA"] = pd_module.to_numeric(table["BASAL_AREA"], errors="coerce")

    table = table[table.BCLCS_LEVEL_2 == required_bclcs_level_2]
    table = table[table.NON_PRODUCTIVE_CD.notna()]
    table = table[table.FOR_MGMT_LAND_BASE_IND == required_for_mgmt_land_base]
    table = table[~table.BEC_ZONE_CODE.isin(list(excluded_bec_zones))]
    table = table[table.PROJ_AGE_1 >= min_proj_age]
    table = table[table.BASAL_AREA >= min_basal_area]
    table = table[table.LIVE_STAND_VOLUME_125 >= min_live_stand_volume]
    return table
