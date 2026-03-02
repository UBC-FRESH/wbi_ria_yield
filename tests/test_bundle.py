from __future__ import annotations

from pathlib import Path

import pandas as pd

from femic.pipeline.bundle import (
    build_bundle_tables_from_curves,
    bundle_tables_ready,
    ensure_scsi_au_from_table,
    load_bundle_tables,
    resolve_bundle_paths,
    write_bundle_tables,
)


def test_resolve_bundle_paths_and_ready(tmp_path: Path) -> None:
    paths = resolve_bundle_paths(base_dir=tmp_path / "bundle", ensure_dir=True)

    assert paths.bundle_dir == tmp_path / "bundle"
    assert bundle_tables_ready(paths=paths) is False

    (paths.au_table).write_text("au_id,tsa,stratum_code,si_level\n", encoding="utf-8")
    (paths.curve_table).write_text("curve_id,curve_type\n", encoding="utf-8")
    (paths.curve_points_table).write_text("curve_id,x,y\n", encoding="utf-8")
    assert bundle_tables_ready(paths=paths) is True


def test_load_write_bundle_tables_and_normalize_tsa(tmp_path: Path) -> None:
    paths = resolve_bundle_paths(base_dir=tmp_path / "bundle", ensure_dir=True)
    au_table = pd.DataFrame(
        [{"au_id": 800001, "tsa": "8", "stratum_code": "S1", "si_level": "M"}]
    )
    curve_table = pd.DataFrame([{"curve_id": 1, "curve_type": "unmanaged"}])
    curve_points_table = pd.DataFrame([{"curve_id": 1, "x": 10, "y": 50.0}])

    write_bundle_tables(
        paths=paths,
        au_table=au_table,
        curve_table=curve_table,
        curve_points_table=curve_points_table,
    )

    loaded_au, loaded_curve, loaded_points = load_bundle_tables(
        paths=paths,
        pd_module=pd,
        normalize_tsa_code_fn=lambda v: f"{int(v):02d}",
    )

    assert loaded_au.loc[0, "tsa"] == "08"
    assert loaded_curve.loc[0, "curve_type"] == "unmanaged"
    assert loaded_points.loc[0, "y"] == 50.0


def test_ensure_scsi_au_from_table_populates_missing_entries() -> None:
    au_table = pd.DataFrame(
        [
            {"au_id": 800005, "tsa": "8", "stratum_code": "BWBS_AT", "si_level": "L"},
            {"au_id": 800005, "tsa": "8", "stratum_code": "BWBS_AT", "si_level": "L"},
        ]
    )
    scsi_au: dict[str, dict[tuple[str, str], int]] = {}

    ensure_scsi_au_from_table(
        au_table=au_table,
        scsi_au=scsi_au,
        normalize_tsa_code_fn=lambda v: f"{int(v):02d}",
    )

    assert scsi_au["08"][("BWBS_AT", "L")] == 5


def test_build_bundle_tables_from_curves_builds_unmanaged_and_managed_rows() -> None:
    vdyp_curves_smooth = {
        "08": pd.DataFrame(
            [
                {"stratum_code": "BWBS_AT", "si_level": "L", "age": 10, "volume": 1.0},
                {"stratum_code": "BWBS_AT", "si_level": "L", "age": 20, "volume": 2.0},
            ]
        )
    }
    tipsy_curves = {
        "08": pd.DataFrame(
            [
                {"AU": 20005, "Age": 10, "Yield": 1.5},
                {"AU": 20005, "Age": 20, "Yield": 2.5},
            ]
        )
    }
    scsi_au = {"08": {("BWBS_AT", "L"): 5}}

    out = build_bundle_tables_from_curves(
        tsa_list=["08"],
        vdyp_curves_smooth=vdyp_curves_smooth,
        tipsy_curves=tipsy_curves,
        scsi_au=scsi_au,
        canfi_species_fn=lambda _s: 100,
        pd_module=pd,
        message_fn=lambda _m: None,
    )

    assert len(out.au_table) == 1
    assert int(out.au_table.loc[0, "au_id"]) == 800005
    assert int(out.au_table.loc[0, "managed_curve_id"]) == 820005
    assert sorted(out.curve_table["curve_type"].tolist()) == ["managed", "unmanaged"]
    assert len(out.curve_points_table) == 4
    assert out.missing_au_curve_mappings.empty


def test_build_bundle_tables_from_curves_tracks_missing_mappings() -> None:
    vdyp_curves_smooth = {
        "08": pd.DataFrame(
            [{"stratum_code": "BWBS_AT", "si_level": "L", "age": 10, "volume": 1.0}]
        )
    }
    tipsy_curves = {"08": pd.DataFrame(columns=["AU", "Age", "Yield"])}
    scsi_au: dict[str, dict[tuple[str, str], int]] = {"08": {}}

    out = build_bundle_tables_from_curves(
        tsa_list=["08"],
        vdyp_curves_smooth=vdyp_curves_smooth,
        tipsy_curves=tipsy_curves,
        scsi_au=scsi_au,
        canfi_species_fn=lambda _s: 100,
        pd_module=pd,
        message_fn=lambda _m: None,
    )

    assert out.au_table.empty
    assert len(out.missing_au_curve_mappings) == 1
    assert out.missing_au_curve_mappings.loc[0, "stratum_code"] == "BWBS_AT"
