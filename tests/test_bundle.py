from __future__ import annotations

from pathlib import Path

import pandas as pd

from femic.pipeline.bundle import (
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
