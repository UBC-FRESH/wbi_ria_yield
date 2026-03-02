"""Reusable TIPSY parameter helper utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from femic.pipeline.diagnostics import build_timestamped_event


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


def _tipsy_candidate_exception_types() -> tuple[type[Exception], ...]:
    """Candidate-evaluation failures that preserve legacy debug+re-raise behavior."""
    return (ValueError, KeyError, TypeError, AttributeError, RuntimeError, IndexError)


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
        except (KeyError, TypeError, ValueError, IndexError, AttributeError):
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
        except (KeyError, TypeError, ValueError, IndexError, AttributeError):
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
    return build_timestamped_event(
        event="vdyp_curve_fit",
        status="warning",
        stage="tipsy_input",
        reason=reason,
        context={
            "tsa": tsa,
            "stratum_index": int(stratumi),
            "stratum_code": sc,
            "si_level": si_level,
            "au": int(au),
        },
    )


def build_tipsy_input_table(
    *,
    tipsy_params_for_tsa: Mapping[int, Mapping[str, Mapping[str, Any]]],
    tipsy_params_columns: Sequence[str],
    pd_module: Any,
    table_key: str = "f",
) -> Any:
    """Build TIPSY input table rows from per-AU parameter payloads."""
    rows: list[Any] = []
    for au in tipsy_params_for_tsa:
        table_map = tipsy_params_for_tsa[au].get(table_key)
        if table_map is None:
            continue
        if "TBLno" not in table_map:
            raise KeyError(f"missing TBLno in tipsy_params[{au!r}][{table_key!r}]")
        rows.append(pd_module.DataFrame(table_map, index=[table_map["TBLno"]]))
    if not rows:
        raise RuntimeError("No TIPSY parameter tables generated.")
    return pd_module.concat(rows)[list(tipsy_params_columns)]


def write_tipsy_input_exports(
    *,
    tipsy_table: Any,
    tsa: str,
    tipsy_params_path_prefix: str,
    dat_path_template: str = "./data/02_input-tsa{tsa}.dat",
) -> tuple[str, str]:
    """Write TIPSY input exports to XLSX and DAT outputs for one TSA."""
    tipsy_excel_path = f"{tipsy_params_path_prefix}{tsa}.xlsx"
    tipsy_dat_path = dat_path_template.format(tsa=tsa)
    tipsy_table.to_excel(
        tipsy_excel_path,
        index=False,
        sheet_name="TIPSY_inputTBL",
    )
    tipsy_table.fillna("").to_string(tipsy_dat_path, index=False)
    return tipsy_excel_path, tipsy_dat_path


def tipsy_params_excel_path(
    *,
    tsa: str,
    tipsy_params_path_prefix: str | Path,
) -> Path:
    """Build legacy per-TSA TIPSY parameter workbook path."""
    return Path(f"{tipsy_params_path_prefix}{tsa}.xlsx")


def tipsy_stage_output_paths(
    *,
    tsa: str,
    output_root: str | Path = "data",
) -> tuple[Path, Path]:
    """Build legacy 01b per-TSA output CSV paths."""
    root = Path(output_root)
    return (
        root / f"tipsy_curves_tsa{tsa}.csv",
        root / f"tipsy_sppcomp_tsa{tsa}.csv",
    )


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


def build_tipsy_params_for_tsa(
    *,
    tsa: str,
    results_for_tsa: Sequence[tuple[int, str, Mapping[str, Any]]],
    si_levels: Sequence[str],
    vdyp_curves_smooth_tsa: Any,
    vdyp_results_for_tsa: Mapping[int, Mapping[str, Any]],
    exclusion: Mapping[str, Any],
    tipsy_param_builder: Any,
    vdyp_curve_events_path: Any = None,
    append_jsonl_fn: Any = None,
    min_operable_years: float = 50.0,
    si_iqrlo_quantile: float = 0.50,
    verbose: bool = True,
    message_fn: Any = print,
) -> tuple[
    dict[tuple[str, str], int],
    dict[int, tuple[str, str]],
    dict[int, dict[str, dict[str, Any]]],
]:
    """Select eligible strata+SI combos and build TIPSY params for one TSA."""
    scsi_au_tsa: dict[tuple[str, str], int] = {}
    au_scsi_tsa: dict[int, tuple[str, str]] = {}
    tipsy_params_tsa: dict[int, dict[str, dict[str, Any]]] = {}

    vdyp_indexed = vdyp_curves_smooth_tsa.set_index(["stratum_code", "si_level"])
    vdyp_strata = set(vdyp_indexed.index.get_level_values("stratum_code"))

    for stratumi, sc, result in results_for_tsa:
        message_fn(sc)
        if sc not in vdyp_strata:
            if verbose:
                message_fn("  missing vdyp curves for stratum", sc)
            continue
        for i, si_level in enumerate(si_levels, start=1):
            au = 1000 * i + stratumi
            try:
                df = vdyp_indexed.loc[sc, si_level]
            except KeyError:
                if verbose:
                    message_fn("  missing vdyp curves for", sc, si_level)
                continue
            if not hasattr(df, "columns") and hasattr(df, "to_frame"):
                # Single-row selection can downcast to Series; normalize to DataFrame.
                df = df.to_frame().T
            try:
                candidate = evaluate_tipsy_candidate(
                    sc=sc,
                    vdyp_curve_df=df,
                    result_si=result[si_level],
                    exclusion=exclusion,
                    min_operable_years=min_operable_years,
                    si_iqrlo_quantile=si_iqrlo_quantile,
                )
            except _tipsy_candidate_exception_types():
                message_fn(sc, si_level)
                message_fn(result[si_level]["ss"])
                raise
            if not candidate.eligible:
                if verbose and candidate.reason == "max_vol_too_low":
                    message_fn(
                        "  ",
                        si_level,
                        "max_vol too low",
                        candidate.max_vol,
                        candidate.min_vol,
                    )
                elif verbose and candidate.reason == "operability_window_too_narrow":
                    message_fn(
                        "  ",
                        si_level,
                        "operability window too narrow",
                        candidate.operable_years,
                        min_operable_years,
                    )
                elif verbose and candidate.reason == "si_too_low":
                    message_fn(
                        "  ",
                        si_level,
                        "SI too low (using %0.2f quantile)" % si_iqrlo_quantile,
                        "%2.1f" % candidate.si_vri_iqrlo,
                        "%2.1f" % candidate.si_spr_iqrlo,
                        candidate.min_si,
                    )
                elif verbose and candidate.reason == "excluded_leading_species":
                    message_fn(
                        "  ",
                        si_level,
                        "bad leading species",
                        candidate.leading_species,
                    )
                elif verbose and candidate.reason == "excluded_bec":
                    message_fn("  ", si_level, "bad bec", candidate.bec)
                elif verbose and candidate.reason == "no_species_candidates":
                    message_fn("  ", si_level, "no species candidates after filtering")
                    if (
                        append_jsonl_fn is not None
                        and vdyp_curve_events_path is not None
                    ):
                        append_jsonl_fn(
                            vdyp_curve_events_path,
                            build_tipsy_warning_event(
                                tsa=tsa,
                                stratumi=int(stratumi),
                                sc=sc,
                                si_level=si_level,
                                au=int(au),
                                reason="no_species_candidates",
                            ),
                        )
                continue

            message_fn("  ", si_level, au)
            message_fn(
                "    median SI (VRI)               ",
                ("%2.1f" % candidate.si_vri_med).rjust(4),
            )
            message_fn(
                "    median SI (siteprod)          ",
                ("%2.1f" % candidate.si_spr_med).rjust(4),
            )
            message_fn(
                "    median SI ratio (VRI/siteprod) ",
                "%0.2f" % (candidate.si_vri_med / candidate.si_spr_med),
            )
            for species, v in candidate.species_map.items():
                message_fn("    species", species.ljust(3), "%3.0f" % v["pct"])
            vdyp_result = vdyp_results_for_tsa.get(stratumi, {}).get(si_level)
            if not isinstance(vdyp_result, dict):
                if verbose:
                    message_fn("    missing vdyp result table for", sc, si_level)
                if append_jsonl_fn is not None and vdyp_curve_events_path is not None:
                    append_jsonl_fn(
                        vdyp_curve_events_path,
                        build_tipsy_warning_event(
                            tsa=tsa,
                            stratumi=int(stratumi),
                            sc=sc,
                            si_level=si_level,
                            au=int(au),
                            reason="missing_vdyp_output",
                        ),
                    )
                continue
            scsi_au_tsa[(sc, si_level)] = au
            au_scsi_tsa[au] = (sc, si_level)
            tipsy_params_tsa[au] = tipsy_param_builder(
                au, result[si_level], vdyp_result
            )
            message_fn()
    return scsi_au_tsa, au_scsi_tsa, tipsy_params_tsa
