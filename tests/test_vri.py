from __future__ import annotations

import pandas as pd

from femic.pipeline.vri import (
    assign_stratum_codes_with_lexmatch,
    assign_forest_type_from_species_pct,
    classify_stand_cdm,
    classify_stand_forest_type,
    is_conifer_species_code,
    is_deciduous_species_code,
    normalize_and_filter_checkpoint2_records,
    pconif,
    pdecid,
    stratify_stand,
)


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


def test_conifer_deciduous_helpers_and_proportions() -> None:
    assert is_conifer_species_code("SW") is True
    assert is_deciduous_species_code("AT") is True
    row = {
        "SPECIES_CD_1": "SW",
        "SPECIES_CD_2": "AT",
        "SPECIES_CD_3": "PL",
        "SPECIES_CD_4": "X",
        "SPECIES_CD_5": "X",
        "SPECIES_CD_6": "X",
        "SPECIES_PCT_1": 50,
        "SPECIES_PCT_2": 30,
        "SPECIES_PCT_3": 20,
        "SPECIES_PCT_4": 0,
        "SPECIES_PCT_5": 0,
        "SPECIES_PCT_6": 0,
    }
    assert pconif(row) == 0.7
    assert pdecid(row) == 0.3


def test_stand_classification_helpers() -> None:
    conif_row = {
        "SPECIES_CD_1": "SW",
        "SPECIES_CD_2": "PL",
        "SPECIES_CD_3": "AT",
        "SPECIES_CD_4": "X",
        "SPECIES_CD_5": "X",
        "SPECIES_CD_6": "X",
        "SPECIES_PCT_1": 60,
        "SPECIES_PCT_2": 25,
        "SPECIES_PCT_3": 15,
        "SPECIES_PCT_4": 0,
        "SPECIES_PCT_5": 0,
        "SPECIES_PCT_6": 0,
    }
    decid_row = conif_row | {
        "SPECIES_CD_1": "AT",
        "SPECIES_CD_2": "EP",
        "SPECIES_PCT_1": 70,
    }
    assert classify_stand_cdm(conif_row) == "c"
    assert classify_stand_cdm(decid_row) == "d"
    assert classify_stand_forest_type(conif_row) == 1


def test_assign_forest_type_from_species_pct_assigns_column() -> None:
    frame = pd.DataFrame(
        [
            {
                "SPECIES_CD_1": "SW",
                "SPECIES_CD_2": "PL",
                "SPECIES_CD_3": "AT",
                "SPECIES_CD_4": "X",
                "SPECIES_CD_5": "X",
                "SPECIES_CD_6": "X",
                "SPECIES_PCT_1": 60,
                "SPECIES_PCT_2": 25,
                "SPECIES_PCT_3": 15,
                "SPECIES_PCT_4": 0,
                "SPECIES_PCT_5": 0,
                "SPECIES_PCT_6": 0,
            },
            {
                "SPECIES_CD_1": "AT",
                "SPECIES_CD_2": "EP",
                "SPECIES_CD_3": "SW",
                "SPECIES_CD_4": "X",
                "SPECIES_CD_5": "X",
                "SPECIES_CD_6": "X",
                "SPECIES_PCT_1": 50,
                "SPECIES_PCT_2": 35,
                "SPECIES_PCT_3": 15,
                "SPECIES_PCT_4": 0,
                "SPECIES_PCT_5": 0,
                "SPECIES_PCT_6": 0,
            },
        ]
    )
    out = assign_forest_type_from_species_pct(f_table=frame)
    assert list(out["forest_type"]) == [1, 4]


def test_stratify_stand_builds_expected_codes() -> None:
    row = {
        "BEC_ZONE_CODE": "SBS",
        "BCLCS_LEVEL_4": "TM",
        "SPECIES_CD_1": "SW",
        "SPECIES_CD_2": "PL",
        "BEC_ZONE_CODE_lexmatch": "SBSx",
        "SPECIES_CD_1_lexmatch": "SSW",
        "SPECIES_CD_2_lexmatch": "PPL",
    }
    assert stratify_stand(row) == "SBS_SW+PL"
    assert stratify_stand(row, lexmatch=True) == "SBSxSBSxSBSx_SSWSSW+PPL"


def test_assign_stratum_codes_with_lexmatch_assigns_both_columns() -> None:
    frame = pd.DataFrame(
        [
            {
                "BEC_ZONE_CODE": "SBS",
                "SPECIES_CD_1": "SW",
                "SPECIES_CD_2": "PL",
                "BCLCS_LEVEL_4": "TM",
            },
            {
                "BEC_ZONE_CODE": "BWBS",
                "SPECIES_CD_1": "AT",
                "SPECIES_CD_2": "X",
                "BCLCS_LEVEL_4": "XY",
            },
        ]
    )

    def _row_apply(table: pd.DataFrame, fn: object, axis: int) -> pd.Series:
        assert axis == 1
        return table.apply(fn, axis=axis)  # type: ignore[arg-type]

    out = assign_stratum_codes_with_lexmatch(
        f_table=frame,
        row_apply_fn=_row_apply,
    )
    assert out.loc[0, "stratum"] == "SBS_SW+PL"
    assert out.loc[1, "stratum"] == "BWBS_AT"
    assert out.loc[0, "stratum_lexmatch"].startswith("SBSxSBSxSBSx_")
