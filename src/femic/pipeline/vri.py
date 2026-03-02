"""Helpers for legacy VRI table normalization/filtering stages."""

from __future__ import annotations

from typing import Any, Sequence


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
