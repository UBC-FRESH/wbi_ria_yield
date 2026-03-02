from __future__ import annotations

import pandas as pd

from femic.pipeline.vri import normalize_and_filter_checkpoint2_records


def _base_row() -> dict[str, object]:
    return {
        "SPECIES_CD_1": None,
        "SPECIES_CD_2": None,
        "SPECIES_CD_3": None,
        "SPECIES_CD_4": None,
        "SPECIES_CD_5": None,
        "SPECIES_CD_6": None,
        "SPECIES_PCT_1": None,
        "SPECIES_PCT_2": None,
        "SPECIES_PCT_3": None,
        "SPECIES_PCT_4": None,
        "SPECIES_PCT_5": None,
        "SPECIES_PCT_6": None,
        "SOIL_NUTRIENT_REGIME": None,
        "SOIL_MOISTURE_REGIME_1": None,
        "SITE_POSITION_MESO": None,
        "BCLCS_LEVEL_2": "T",
        "BCLCS_LEVEL_3": None,
        "BCLCS_LEVEL_4": None,
        "BCLCS_LEVEL_5": None,
        "BEC_VARIANT": None,
        "NON_PRODUCTIVE_CD": "N",
        "FOR_MGMT_LAND_BASE_IND": "Y",
        "BEC_ZONE_CODE": "SBS",
        "PROJ_AGE_1": 60,
        "BASAL_AREA": 20,
        "LIVE_STAND_VOLUME_125": None,
        "LIVE_VOL_PER_HA_SPP1_125": None,
        "LIVE_VOL_PER_HA_SPP2_125": None,
        "LIVE_VOL_PER_HA_SPP3_125": None,
        "LIVE_VOL_PER_HA_SPP4_125": None,
        "LIVE_VOL_PER_HA_SPP5_125": None,
        "LIVE_VOL_PER_HA_SPP6_125": None,
    }


def test_normalize_and_filter_checkpoint2_records_applies_fill_defaults() -> None:
    frame = pd.DataFrame([_base_row()]).assign(LIVE_STAND_VOLUME_125=10)
    out = normalize_and_filter_checkpoint2_records(f_table=frame)
    row = out.iloc[0]
    assert row["SPECIES_CD_1"] == "X"
    assert row["SPECIES_PCT_1"] == 0
    assert row["SOIL_NUTRIENT_REGIME"] == "X"
    assert row["LIVE_VOL_PER_HA_SPP1_125"] == 0


def test_normalize_and_filter_checkpoint2_records_filters_excluded_rows() -> None:
    keep = _base_row()
    drop_bec = _base_row() | {"BEC_ZONE_CODE": "BAFA"}
    drop_live_vol = _base_row() | {"LIVE_STAND_VOLUME_125": 0}
    frame = pd.DataFrame([keep, drop_bec, drop_live_vol]).assign(
        LIVE_STAND_VOLUME_125=[10, 10, 0]
    )
    out = normalize_and_filter_checkpoint2_records(f_table=frame)
    assert len(out) == 1
    assert out.iloc[0]["BEC_ZONE_CODE"] == "SBS"
