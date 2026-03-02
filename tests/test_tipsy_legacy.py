from __future__ import annotations

import ast
from pathlib import Path

import pandas as pd
import pytest

from femic.pipeline.tipsy_legacy import (
    build_tipsy_exclusion,
    get_legacy_tipsy_builders,
)


def test_get_legacy_tipsy_builders_returns_expected_tsa_keys() -> None:
    builders = get_legacy_tipsy_builders()
    assert set(builders) == {"08", "16", "24", "40", "41"}


def test_build_tipsy_exclusion_returns_expected_tsa_keys() -> None:
    exclusion = build_tipsy_exclusion()
    assert set(exclusion) == {"08", "16", "24", "40", "41"}
    assert exclusion["08"]["min_vol"]("SW") == 140.0


def test_tsa08_legacy_builder_returns_expected_core_fields() -> None:
    builders = get_legacy_tipsy_builders()
    builder = builders["08"]
    au_data = {
        "ss": pd.DataFrame({"SITE_INDEX": [17.0], "BEC_ZONE_CODE": ["SBS"]}),
        "species": {"SW": {"pct": 100.0}},
    }
    vdyp_out = {1: pd.DataFrame({"% Stk": [90.0]})}
    out = builder(1, au_data, vdyp_out)
    assert out["e"]["TBLno"] == 10001
    assert out["f"]["TBLno"] == 20001
    assert out["e"]["SPP_1"] == "SW"
    assert out["f"]["SPP_1"] == "SW"


def test_tsa24_legacy_builder_switches_on_bec_zone_for_fir() -> None:
    builder = get_legacy_tipsy_builders()["24"]
    vdyp_out = {1: pd.DataFrame({"SI": [18.0], "% Stk": [85.0]})}

    out_sbs = builder(
        7,
        {
            "ss": pd.DataFrame({"SITE_INDEX": [17.0], "BEC_ZONE_CODE": ["SBS"]}),
            "species": {"BL": {"pct": 100.0}},
        },
        vdyp_out,
    )
    out_essf = builder(
        7,
        {
            "ss": pd.DataFrame({"SITE_INDEX": [17.0], "BEC_ZONE_CODE": ["ESSF"]}),
            "species": {"BL": {"pct": 100.0}},
        },
        vdyp_out,
    )

    assert out_sbs["e"]["Density"] == 2500
    assert out_essf["e"]["Density"] == 1500
    assert out_sbs["e"]["SPP_1"] == "SW"
    assert out_essf["e"]["SPP_1"] == "SE"
    assert out_sbs["e"]["Regen_Delay"] == 2
    assert out_essf["e"]["Regen_Delay"] == 1


def test_tsa40_legacy_builder_sets_none_for_missing_species_slots() -> None:
    builder = get_legacy_tipsy_builders()["40"]
    vdyp_out = {1: pd.DataFrame({"SI": [17.0], "% Stk": [89.0]})}
    out = builder(
        9,
        {
            "ss": pd.DataFrame({"SITE_INDEX": [17.0], "BEC_ZONE_CODE": ["BWBS"]}),
            "species": {"SX": {"pct": 100.0}},
        },
        vdyp_out,
    )
    assert out["e"]["SPP_1"] == "SW"
    assert out["e"]["PCT_1"] == 100.0
    assert out["e"]["SPP_2"] is None
    assert out["e"]["PCT_2"] is None


def test_tsa08_legacy_builder_unsupported_species_raises_value_error() -> None:
    builder = get_legacy_tipsy_builders()["08"]
    au_data = {
        "ss": pd.DataFrame({"SITE_INDEX": [17.0], "BEC_ZONE_CODE": ["SBS"]}),
        "species": {"AT": {"pct": 100.0}},
    }
    vdyp_out = {1: pd.DataFrame({"% Stk": [90.0]})}
    with pytest.raises(ValueError, match="tsa=08"):
        builder(1, au_data, vdyp_out)


def test_tsa40_legacy_builder_unsupported_bec_raises_value_error() -> None:
    builder = get_legacy_tipsy_builders()["40"]
    au_data = {
        "ss": pd.DataFrame({"SITE_INDEX": [17.0], "BEC_ZONE_CODE": ["ICH"]}),
        "species": {"SW": {"pct": 100.0}},
    }
    vdyp_out = {1: pd.DataFrame({"SI": [17.0], "% Stk": [89.0]})}
    with pytest.raises(ValueError, match="unsupported_bec"):
        builder(1, au_data, vdyp_out)


def test_tsa41_legacy_builder_unimplemented_forest_type_raises_not_implemented() -> (
    None
):
    builder = get_legacy_tipsy_builders()["41"]
    au_data = {
        "ss": pd.DataFrame(
            {"SITE_INDEX": [16.0], "BEC_ZONE_CODE": ["BWBS"], "forest_type": [2]}
        ),
        "species": {"SW": {"pct": 100.0}},
    }
    vdyp_out = {1: pd.DataFrame({"SI": [16.0], "% Stk": [92.0]})}
    with pytest.raises(NotImplementedError, match="tsa=41"):
        builder(1, au_data, vdyp_out)


def test_tipsy_legacy_module_has_no_assert_false_sentinels() -> None:
    source_path = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "femic"
        / "pipeline"
        / "tipsy_legacy.py"
    )
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assert):
            continue
        if isinstance(node.test, ast.Constant) and node.test.value is False:
            raise AssertionError(
                "tipsy_legacy.py should not contain assert False sentinels"
            )
