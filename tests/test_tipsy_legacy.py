from __future__ import annotations

import pandas as pd

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
