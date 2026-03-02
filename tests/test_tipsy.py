from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import pytest

from femic.pipeline.tipsy import (
    build_tipsy_params_for_tsa,
    build_tipsy_input_table,
    build_tipsy_warning_event,
    compute_vdyp_oaf1,
    compute_vdyp_site_index,
    evaluate_tipsy_candidate,
    tipsy_params_excel_path,
    tipsy_stage_output_paths,
    write_tipsy_input_exports,
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


def test_compute_helpers_unexpected_table_error_propagates() -> None:
    class _BadTable:
        def __getitem__(self, _key: str) -> object:
            raise ZeroDivisionError("unexpected")

    bad = _BadTable()
    with pytest.raises(ZeroDivisionError):
        compute_vdyp_site_index({1: bad})
    with pytest.raises(ZeroDivisionError):
        compute_vdyp_oaf1({1: bad})


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


def test_build_tipsy_input_table_selects_table_key_and_columns() -> None:
    tipsy_params_for_tsa = {
        1001: {
            "e": {"TBLno": 11, "AU": 1001, "SI": 16.0},
            "f": {"TBLno": 21, "AU": 1001, "SI": 18.0},
        },
        1002: {
            "e": {"TBLno": 12, "AU": 1002, "SI": 17.0},
            "f": {"TBLno": 22, "AU": 1002, "SI": 19.0},
        },
    }
    out = build_tipsy_input_table(
        tipsy_params_for_tsa=tipsy_params_for_tsa,
        tipsy_params_columns=["AU", "SI"],
        pd_module=pd,
        table_key="f",
    )
    assert list(out["AU"]) == [1001, 1002]
    assert list(out["SI"]) == [18.0, 19.0]


def test_build_tipsy_input_table_raises_when_no_rows() -> None:
    tipsy_params_for_tsa = {1001: {"e": {"TBLno": 11, "AU": 1001, "SI": 16.0}}}
    with pytest.raises(RuntimeError, match="No TIPSY parameter tables generated"):
        build_tipsy_input_table(
            tipsy_params_for_tsa=tipsy_params_for_tsa,
            tipsy_params_columns=["AU", "SI"],
            pd_module=pd,
            table_key="f",
        )


def test_write_tipsy_input_exports_writes_excel_and_dat(tmp_path: Path) -> None:
    table = pd.DataFrame({"AU": [1001], "SI": [18.0]})
    prefix = str(tmp_path / "tipsy_params_tsa")
    dat_template = str(tmp_path / "02_input-tsa{tsa}.dat")
    excel_path, dat_path = write_tipsy_input_exports(
        tipsy_table=table,
        tsa="08",
        tipsy_params_path_prefix=prefix,
        dat_path_template=dat_template,
    )
    assert excel_path == str(tmp_path / "tipsy_params_tsa08.xlsx")
    assert dat_path == str(tmp_path / "02_input-tsa08.dat")
    assert Path(excel_path).is_file()
    assert Path(dat_path).is_file()
    assert "AU" in Path(dat_path).read_text()


def test_tipsy_stage_output_paths_uses_expected_naming(tmp_path: Path) -> None:
    curves_path, sppcomp_path = tipsy_stage_output_paths(tsa="08", output_root=tmp_path)
    assert curves_path == tmp_path / "tipsy_curves_tsa08.csv"
    assert sppcomp_path == tmp_path / "tipsy_sppcomp_tsa08.csv"


def test_tipsy_params_excel_path_uses_expected_naming(tmp_path: Path) -> None:
    path = tipsy_params_excel_path(
        tsa="08",
        tipsy_params_path_prefix=tmp_path / "tipsy_params_tsa",
    )
    assert path == tmp_path / "tipsy_params_tsa08.xlsx"


def test_build_tipsy_params_for_tsa_assigns_expected_maps() -> None:
    results_for_tsa = [
        (
            0,
            "SBS_7A",
            {
                "L": {
                    "ss": pd.DataFrame(
                        {
                            "SITE_INDEX": [18.0],
                            "siteprod": [17.0],
                            "BEC_ZONE_CODE": ["SBS"],
                        }
                    ),
                    "species": {"SW": {"pct": 60.0}},
                }
            },
        )
    ]
    vdyp_curves_smooth_tsa = pd.DataFrame(
        {
            "stratum_code": ["SBS_7A", "SBS_7A"],
            "si_level": ["L", "L"],
            "age": [30, 120],
            "volume": [160.0, 220.0],
        }
    )
    exclusion = {
        "min_vol": lambda _code: 140.0,
        "min_si": lambda _species: 10.0,
        "excl_leading_species": [],
        "excl_bec": [],
    }

    def _builder(
        au_id: int,
        _au_data: object,
        _vdyp_out: object,
    ) -> dict[str, dict[str, object]]:
        return {"f": {"TBLno": 20000 + au_id}}

    scsi_au_tsa, au_scsi_tsa, tipsy_params_tsa = build_tipsy_params_for_tsa(
        tsa="08",
        results_for_tsa=results_for_tsa,
        si_levels=["L"],
        vdyp_curves_smooth_tsa=vdyp_curves_smooth_tsa,
        vdyp_results_for_tsa={0: {"L": {"dummy": 1}}},
        exclusion=exclusion,
        tipsy_param_builder=_builder,
        verbose=False,
        message_fn=lambda *_args: None,
    )
    assert scsi_au_tsa == {("SBS_7A", "L"): 1000}
    assert au_scsi_tsa == {1000: ("SBS_7A", "L")}
    assert tipsy_params_tsa[1000]["f"]["TBLno"] == 21000


def test_build_tipsy_params_for_tsa_logs_missing_vdyp_output_warning() -> None:
    events: list[dict[str, object]] = []
    results_for_tsa = [
        (
            0,
            "SBS_7A",
            {
                "L": {
                    "ss": pd.DataFrame(
                        {
                            "SITE_INDEX": [18.0],
                            "siteprod": [17.0],
                            "BEC_ZONE_CODE": ["SBS"],
                        }
                    ),
                    "species": {"SW": {"pct": 60.0}},
                }
            },
        )
    ]
    vdyp_curves_smooth_tsa = pd.DataFrame(
        {
            "stratum_code": ["SBS_7A", "SBS_7A"],
            "si_level": ["L", "L"],
            "age": [30, 120],
            "volume": [160.0, 220.0],
        }
    )
    exclusion = {
        "min_vol": lambda _code: 140.0,
        "min_si": lambda _species: 10.0,
        "excl_leading_species": [],
        "excl_bec": [],
    }

    def _append_jsonl(_path: object, payload: dict[str, object]) -> None:
        events.append(payload)

    scsi_au_tsa, au_scsi_tsa, tipsy_params_tsa = build_tipsy_params_for_tsa(
        tsa="08",
        results_for_tsa=results_for_tsa,
        si_levels=["L"],
        vdyp_curves_smooth_tsa=vdyp_curves_smooth_tsa,
        vdyp_results_for_tsa={},
        exclusion=exclusion,
        tipsy_param_builder=lambda *_args: {"f": {}},
        vdyp_curve_events_path="events.jsonl",
        append_jsonl_fn=_append_jsonl,
        verbose=True,
        message_fn=lambda *_args: None,
    )
    assert scsi_au_tsa == {}
    assert au_scsi_tsa == {}
    assert tipsy_params_tsa == {}
    assert len(events) == 1
    assert events[0]["reason"] == "missing_vdyp_output"


def test_build_tipsy_params_for_tsa_logs_no_species_candidates_warning() -> None:
    events: list[dict[str, object]] = []
    results_for_tsa = [
        (
            0,
            "SBS_7A",
            {
                "L": {
                    "ss": pd.DataFrame(
                        {
                            "SITE_INDEX": [18.0],
                            "siteprod": [17.0],
                            "BEC_ZONE_CODE": ["SBS"],
                        }
                    ),
                    "species": {},
                }
            },
        )
    ]
    vdyp_curves_smooth_tsa = pd.DataFrame(
        {
            "stratum_code": ["SBS_7A", "SBS_7A"],
            "si_level": ["L", "L"],
            "age": [30, 120],
            "volume": [160.0, 220.0],
        }
    )
    exclusion = {
        "min_vol": lambda _code: 140.0,
        "min_si": lambda _species: 10.0,
        "excl_leading_species": [],
        "excl_bec": [],
    }

    def _append_jsonl(_path: object, payload: dict[str, object]) -> None:
        events.append(payload)

    _ = build_tipsy_params_for_tsa(
        tsa="08",
        results_for_tsa=results_for_tsa,
        si_levels=["L"],
        vdyp_curves_smooth_tsa=vdyp_curves_smooth_tsa,
        vdyp_results_for_tsa={0: {"L": {"dummy": 1}}},
        exclusion=exclusion,
        tipsy_param_builder=lambda *_args: {"f": {}},
        vdyp_curve_events_path="events.jsonl",
        append_jsonl_fn=_append_jsonl,
        verbose=True,
        message_fn=lambda *_args: None,
    )
    assert len(events) == 1
    assert events[0]["reason"] == "no_species_candidates"


def test_build_tipsy_params_for_tsa_candidate_value_error_logs_debug_then_raises() -> (
    None
):
    messages: list[tuple[object, ...]] = []
    results_for_tsa = [
        (
            0,
            "BAD",
            {
                "L": {
                    "ss": pd.DataFrame(
                        {
                            "SITE_INDEX": [18.0],
                            "siteprod": [17.0],
                            "BEC_ZONE_CODE": ["SBS"],
                        }
                    ),
                    "species": {"SW": {"pct": 60.0}},
                }
            },
        )
    ]
    vdyp_curves_smooth_tsa = pd.DataFrame(
        {
            "stratum_code": ["BAD", "BAD"],
            "si_level": ["L", "L"],
            "age": [30, 120],
            "volume": [160.0, 220.0],
        }
    )
    exclusion = {
        "min_vol": lambda _code: 140.0,
        "min_si": lambda _species: 10.0,
        "excl_leading_species": [],
        "excl_bec": [],
    }

    with pytest.raises(ValueError, match="invalid stratum code format"):
        build_tipsy_params_for_tsa(
            tsa="08",
            results_for_tsa=results_for_tsa,
            si_levels=["L"],
            vdyp_curves_smooth_tsa=vdyp_curves_smooth_tsa,
            vdyp_results_for_tsa={0: {"L": {"dummy": 1}}},
            exclusion=exclusion,
            tipsy_param_builder=lambda *_args: {"f": {}},
            verbose=False,
            message_fn=lambda *args: messages.append(args),
        )

    assert any(msg == ("BAD", "L") for msg in messages)


def test_build_tipsy_params_for_tsa_unexpected_candidate_error_propagates() -> None:
    results_for_tsa = [
        (
            0,
            "SBS_7A",
            {
                "L": {
                    "ss": pd.DataFrame(
                        {
                            "SITE_INDEX": [18.0],
                            "siteprod": [17.0],
                            "BEC_ZONE_CODE": ["SBS"],
                        }
                    ),
                    "species": {"SW": {"pct": 60.0}},
                }
            },
        )
    ]
    vdyp_curves_smooth_tsa = pd.DataFrame(
        {
            "stratum_code": ["SBS_7A", "SBS_7A"],
            "si_level": ["L", "L"],
            "age": [30, 120],
            "volume": [160.0, 220.0],
        }
    )
    exclusion = {
        "min_vol": lambda _code: (_ for _ in ()).throw(ZeroDivisionError("unexpected")),
        "min_si": lambda _species: 10.0,
        "excl_leading_species": [],
        "excl_bec": [],
    }

    with pytest.raises(ZeroDivisionError, match="unexpected"):
        build_tipsy_params_for_tsa(
            tsa="08",
            results_for_tsa=results_for_tsa,
            si_levels=["L"],
            vdyp_curves_smooth_tsa=vdyp_curves_smooth_tsa,
            vdyp_results_for_tsa={0: {"L": {"dummy": 1}}},
            exclusion=exclusion,
            tipsy_param_builder=lambda *_args: {"f": {}},
            verbose=False,
            message_fn=lambda *_args: None,
        )
