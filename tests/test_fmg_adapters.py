from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from femic.fmg.adapters import (
    build_bundle_model_context,
    build_bundle_model_context_from_tables,
    normalize_tsa_code,
)


def _write_bundle_tables(bundle_dir: Path) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "au_id": 1001,
                "tsa": "29",
                "stratum_code": "SBPS_PLI",
                "si_level": "L",
                "planted_curve_id": 21001,
                "natural_curve_id": 1001,
            },
            {
                "au_id": 1001,
                "tsa": "29",
                "stratum_code": "SBPS_PLI",
                "si_level": "L",
                "planted_curve_id": 21001,
                "natural_curve_id": 1001,
            },
        ]
    ).to_csv(bundle_dir / "au_table.csv", index=False)
    pd.DataFrame(
        [
            {"curve_id": 1001, "curve_type": "natural"},
            {"curve_id": 21001, "curve_type": "planted"},
            {"curve_id": 21001001, "curve_type": "planted_species_prop_PL"},
            {"curve_id": 1001001, "curve_type": "natural_species_prop_PL"},
        ]
    ).to_csv(bundle_dir / "curve_table.csv", index=False)
    pd.DataFrame(
        [
            {"curve_id": 1001, "x": 1, "y": 10.0},
            {"curve_id": 1001, "x": 2, "y": 20.0},
            {"curve_id": 21001, "x": 1, "y": 12.0},
            {"curve_id": 21001, "x": 2, "y": 25.0},
            {"curve_id": 21001001, "x": 1, "y": 0.70},
            {"curve_id": 1001001, "x": 1, "y": 0.60},
        ]
    ).to_csv(bundle_dir / "curve_points_table.csv", index=False)


def test_normalize_tsa_code() -> None:
    assert normalize_tsa_code("29") == "29"
    assert normalize_tsa_code(8) == "08"
    assert normalize_tsa_code("K3Z") == "k3z"


def test_build_bundle_model_context_from_tables_scopes_and_dedupes() -> None:
    au_table = pd.DataFrame(
        [
            {
                "au_id": 1001,
                "tsa": "29",
                "stratum_code": "SBPS_PLI",
                "si_level": "L",
                "planted_curve_id": 21001,
                "natural_curve_id": 1001,
            },
            {
                "au_id": 1001,
                "tsa": "29",
                "stratum_code": "SBPS_PLI",
                "si_level": "L",
                "planted_curve_id": 21001,
                "natural_curve_id": 1001,
            },
            {
                "au_id": 2001,
                "tsa": "k3z",
                "stratum_code": "CWH_HW",
                "si_level": "M",
                "planted_curve_id": 22001,
                "natural_curve_id": 2001,
            },
        ]
    )
    curve_table = pd.DataFrame(
        [
            {"curve_id": 1001, "curve_type": "natural"},
            {"curve_id": 21001, "curve_type": "planted"},
            {"curve_id": 21001001, "curve_type": "planted_species_prop_PL"},
        ]
    )
    curve_points = pd.DataFrame(
        [
            {"curve_id": 1001, "x": 1, "y": 10.0},
            {"curve_id": 21001, "x": 1, "y": 12.0},
            {"curve_id": 21001001, "x": 1, "y": 0.7},
        ]
    )

    context = build_bundle_model_context_from_tables(
        au_table=au_table,
        curve_table=curve_table,
        curve_points_table=curve_points,
        tsa_list=["29"],
    )

    assert context.tsa_list == ["29"]
    assert len(context.analysis_units) == 1
    assert context.analysis_units[0].au_id == 1001
    assert 1001 in context.curves_by_id
    assert context.managed_species_curve_ids[21001]["PL"] == 21001001


def test_build_bundle_model_context_reads_csv(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    _write_bundle_tables(bundle_dir)
    context = build_bundle_model_context(bundle_dir=bundle_dir, tsa_list=["29"])
    assert context.tsa_list == ["29"]
    assert len(context.analysis_units) == 1
    assert context.analysis_units[0].managed_curve_id == 21001
    assert len(context.curves_by_id[1001].points) == 2


def test_build_bundle_model_context_requires_tsa(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    _write_bundle_tables(bundle_dir)
    with pytest.raises(ValueError, match="at least one TSA"):
        build_bundle_model_context(bundle_dir=bundle_dir, tsa_list=[])
