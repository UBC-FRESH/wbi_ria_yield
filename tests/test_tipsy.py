from __future__ import annotations

import math

import pandas as pd

from femic.pipeline.tipsy import (
    build_tipsy_warning_event,
    compute_vdyp_oaf1,
    compute_vdyp_site_index,
    evaluate_tipsy_candidate,
)


def test_compute_vdyp_site_index_returns_mean_rounded() -> None:
    vdyp_out = {
        1: pd.DataFrame({"SI": [10.0, 12.0]}),
        2: pd.DataFrame({"SI": [14.0, 16.0]}),
    }
    assert compute_vdyp_site_index(vdyp_out) == 13.0


def test_compute_vdyp_oaf1_ignores_malformed_tables() -> None:
    vdyp_out = {
        1: pd.DataFrame({"% Stk": [85.0]}),
        2: pd.DataFrame({"bad": [1]}),
        3: pd.DataFrame({"% Stk": [95.0]}),
    }
    assert compute_vdyp_oaf1(vdyp_out) == 0.9


def test_compute_helpers_return_nan_when_no_usable_values() -> None:
    vdyp_out = {1: pd.DataFrame({"other": [1.0]})}
    assert math.isnan(compute_vdyp_site_index(vdyp_out))
    assert math.isnan(compute_vdyp_oaf1(vdyp_out))


def test_build_tipsy_warning_event_payload_shape() -> None:
    payload = build_tipsy_warning_event(
        tsa="08",
        stratumi=3,
        sc="SBS_7A",
        si_level="M",
        au=2003,
        reason="no_species_candidates",
    )
    assert payload["event"] == "vdyp_curve_fit"
    assert payload["status"] == "warning"
    assert payload["stage"] == "tipsy_input"
    assert payload["context"]["tsa"] == "08"
    assert payload["context"]["au"] == 2003


def test_evaluate_tipsy_candidate_returns_reason_for_no_species() -> None:
    vdyp_curve_df = pd.DataFrame({"age": [30, 40, 50], "volume": [150, 170, 180]})
    result_si = {
        "ss": pd.DataFrame({"SITE_INDEX": [18.0, 19.0], "siteprod": [17.0, 18.0]}),
        "species": {},
    }
    exclusion = {
        "min_vol": lambda _code: 140.0,
        "min_si": lambda _species: 10.0,
        "excl_leading_species": [],
        "excl_bec": [],
    }
    out = evaluate_tipsy_candidate(
        sc="SBS_7A",
        vdyp_curve_df=vdyp_curve_df,
        result_si=result_si,
        exclusion=exclusion,
        min_operable_years=10,
        si_iqrlo_quantile=0.5,
    )
    assert out.eligible is False
    assert out.reason == "no_species_candidates"


def test_evaluate_tipsy_candidate_happy_path() -> None:
    vdyp_curve_df = pd.DataFrame({"age": [30, 80, 120], "volume": [150, 200, 240]})
    result_si = {
        "ss": pd.DataFrame({"SITE_INDEX": [18.0, 19.0], "siteprod": [17.0, 18.0]}),
        "species": {"SW": {"pct": 60.0}},
    }
    exclusion = {
        "min_vol": lambda _code: 140.0,
        "min_si": lambda _species: 10.0,
        "excl_leading_species": [],
        "excl_bec": [],
    }
    out = evaluate_tipsy_candidate(
        sc="SBS_7A",
        vdyp_curve_df=vdyp_curve_df,
        result_si=result_si,
        exclusion=exclusion,
        min_operable_years=50,
        si_iqrlo_quantile=0.5,
    )
    assert out.eligible is True
    assert out.reason is None
    assert out.leading_species == "SW"
