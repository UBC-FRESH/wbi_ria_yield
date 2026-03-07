from __future__ import annotations

from femic.pipeline.vdyp_overrides import vdyp_kwarg_overrides_for_tsa


def test_vdyp_kwarg_overrides_for_known_tsa() -> None:
    overrides = vdyp_kwarg_overrides_for_tsa("40")
    assert overrides[("BWBS_SX", "L")]["skip1"] == 30
    assert overrides[("SWB_SX", "L")]["dx_c1"] == 1.0
    assert overrides[("SWB_SX", "L")]["dx_c2"] == 0.0


def test_vdyp_kwarg_overrides_for_unknown_tsa_is_empty() -> None:
    assert vdyp_kwarg_overrides_for_tsa("99") == {}


def test_vdyp_kwarg_overrides_for_tsa29_contains_sbps_pl_low_si_fix() -> None:
    overrides = vdyp_kwarg_overrides_for_tsa("29")
    assert overrides[("SBPS_PL", "L")]["skip1"] == 50


def test_vdyp_kwarg_overrides_returns_defensive_copy() -> None:
    first = vdyp_kwarg_overrides_for_tsa("24")
    first[("ESSF_BL", "L")]["skip1"] = 999
    second = vdyp_kwarg_overrides_for_tsa("24")
    assert second[("ESSF_BL", "L")]["skip1"] == 30
