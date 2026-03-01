"""Reusable TIPSY parameter helper utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Mapping

import numpy as np


@dataclass(frozen=True)
class TIPSYCandidateEvaluation:
    """Eligibility outcome and derived metrics for one stratum+SI candidate."""

    eligible: bool
    reason: str | None
    species_map: Mapping[str, Any]
    leading_species: str | None
    bec: str
    max_vol: float
    min_vol: float
    operable_years: float
    si_vri_iqrlo: float
    si_spr_iqrlo: float
    si_vri_med: float
    si_spr_med: float
    min_si: float | None


def compute_vdyp_site_index(
    vdyp_out: Mapping[Any, Any],
    *,
    ndigits: int = 1,
) -> float:
    """Compute mean SI across VDYP output tables, rounded for TIPSY input."""
    values: list[float] = []
    for table in vdyp_out.values():
        try:
            value = float(table["SI"].mean())
        except Exception:
            continue
        if np.isfinite(value):
            values.append(value)
    if not values:
        return float("nan")
    return round(float(np.mean(values)), ndigits)


def compute_vdyp_oaf1(vdyp_out: Mapping[Any, Any]) -> float:
    """Compute OAF1 from mean VDYP `% Stk` values, handling malformed tables."""
    stockability: list[float] = []
    for table in vdyp_out.values():
        try:
            value = float(table["% Stk"].iloc[0])
        except Exception:
            continue
        if np.isfinite(value):
            stockability.append(value)
    if not stockability:
        return float("nan")
    return round(float(np.mean(stockability)) * 0.01, 2)


def build_tipsy_warning_event(
    *,
    tsa: str,
    stratumi: int,
    sc: str,
    si_level: str,
    au: int,
    reason: str,
) -> dict[str, Any]:
    """Build standardized warning payload for TIPSY-input stage issues."""
    return {
        "event": "vdyp_curve_fit",
        "timestamp": datetime.now(UTC).isoformat(),
        "status": "warning",
        "stage": "tipsy_input",
        "reason": reason,
        "context": {
            "tsa": tsa,
            "stratum_index": int(stratumi),
            "stratum_code": sc,
            "si_level": si_level,
            "au": int(au),
        },
    }


def evaluate_tipsy_candidate(
    *,
    sc: str,
    vdyp_curve_df: Any,
    result_si: Mapping[str, Any],
    exclusion: Mapping[str, Any],
    min_operable_years: float,
    si_iqrlo_quantile: float,
) -> TIPSYCandidateEvaluation:
    """Evaluate whether a stratum+SI candidate is usable for TIPSY parameter generation."""
    sc_tokens = sc.split("_")
    if len(sc_tokens) < 2 or not sc_tokens[1]:
        raise ValueError(f"invalid stratum code format: {sc!r}")
    bec = sc_tokens[0]
    min_vol = float(exclusion["min_vol"](sc_tokens[1][0]))
    max_vol = float(vdyp_curve_df.volume.max())
    if max_vol < min_vol:
        return TIPSYCandidateEvaluation(
            eligible=False,
            reason="max_vol_too_low",
            species_map={},
            leading_species=None,
            bec=bec,
            max_vol=max_vol,
            min_vol=min_vol,
            operable_years=float("nan"),
            si_vri_iqrlo=float("nan"),
            si_spr_iqrlo=float("nan"),
            si_vri_med=float("nan"),
            si_spr_med=float("nan"),
            min_si=None,
        )
    operable_ages = vdyp_curve_df[vdyp_curve_df.volume >= min_vol].age
    operable_years = float(operable_ages.max() - operable_ages.min())
    if operable_years < min_operable_years:
        return TIPSYCandidateEvaluation(
            eligible=False,
            reason="operability_window_too_narrow",
            species_map={},
            leading_species=None,
            bec=bec,
            max_vol=max_vol,
            min_vol=min_vol,
            operable_years=operable_years,
            si_vri_iqrlo=float("nan"),
            si_spr_iqrlo=float("nan"),
            si_vri_med=float("nan"),
            si_spr_med=float("nan"),
            min_si=None,
        )
    ss = result_si["ss"]
    si_vri_iqrlo = float(ss.SITE_INDEX.quantile(si_iqrlo_quantile))
    si_spr_iqrlo = float(ss.siteprod.quantile(si_iqrlo_quantile))
    si_vri_med = float(ss.SITE_INDEX.median())
    si_spr_med = float(ss.siteprod.median())
    species_map: Mapping[str, Any] = result_si.get("species", {})
    if not species_map:
        return TIPSYCandidateEvaluation(
            eligible=False,
            reason="no_species_candidates",
            species_map={},
            leading_species=None,
            bec=bec,
            max_vol=max_vol,
            min_vol=min_vol,
            operable_years=operable_years,
            si_vri_iqrlo=si_vri_iqrlo,
            si_spr_iqrlo=si_spr_iqrlo,
            si_vri_med=si_vri_med,
            si_spr_med=si_spr_med,
            min_si=None,
        )
    leading_species = list(species_map.keys())[0]
    min_si = float(exclusion["min_si"](leading_species))
    if min(si_vri_iqrlo, si_spr_iqrlo) < min_si:
        return TIPSYCandidateEvaluation(
            eligible=False,
            reason="si_too_low",
            species_map=species_map,
            leading_species=leading_species,
            bec=bec,
            max_vol=max_vol,
            min_vol=min_vol,
            operable_years=operable_years,
            si_vri_iqrlo=si_vri_iqrlo,
            si_spr_iqrlo=si_spr_iqrlo,
            si_vri_med=si_vri_med,
            si_spr_med=si_spr_med,
            min_si=min_si,
        )
    if leading_species in exclusion["excl_leading_species"]:
        return TIPSYCandidateEvaluation(
            eligible=False,
            reason="excluded_leading_species",
            species_map=species_map,
            leading_species=leading_species,
            bec=bec,
            max_vol=max_vol,
            min_vol=min_vol,
            operable_years=operable_years,
            si_vri_iqrlo=si_vri_iqrlo,
            si_spr_iqrlo=si_spr_iqrlo,
            si_vri_med=si_vri_med,
            si_spr_med=si_spr_med,
            min_si=min_si,
        )
    if bec in exclusion["excl_bec"]:
        return TIPSYCandidateEvaluation(
            eligible=False,
            reason="excluded_bec",
            species_map=species_map,
            leading_species=leading_species,
            bec=bec,
            max_vol=max_vol,
            min_vol=min_vol,
            operable_years=operable_years,
            si_vri_iqrlo=si_vri_iqrlo,
            si_spr_iqrlo=si_spr_iqrlo,
            si_vri_med=si_vri_med,
            si_spr_med=si_spr_med,
            min_si=min_si,
        )
    return TIPSYCandidateEvaluation(
        eligible=True,
        reason=None,
        species_map=species_map,
        leading_species=leading_species,
        bec=bec,
        max_vol=max_vol,
        min_vol=min_vol,
        operable_years=operable_years,
        si_vri_iqrlo=si_vri_iqrlo,
        si_spr_iqrlo=si_spr_iqrlo,
        si_vri_med=si_vri_med,
        si_spr_med=si_spr_med,
        min_si=min_si,
    )
