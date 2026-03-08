from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as et

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Polygon

from femic.fmg.patchworks import (
    build_patchworks_forestmodel_definition,
    build_forestmodel_xml_tree,
    export_patchworks_package,
    validate_forestmodel_xml_tree,
    validate_fragments_geodataframe,
    write_forestmodel_xml,
)


def _write_bundle_tables(bundle_dir: Path) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "au_id": 985501000,
                "tsa": "k3z",
                "stratum_code": "CWHvm_HW+FDC",
                "si_level": "L",
                "canfi_species": 402,
                "unmanaged_curve_id": 985501000,
                "managed_curve_id": 985521000,
            }
        ]
    ).to_csv(bundle_dir / "au_table.csv", index=False)
    pd.DataFrame(
        [
            {"curve_id": 985501000, "curve_type": "unmanaged"},
            {"curve_id": 985521000, "curve_type": "managed"},
            {
                "curve_id": 985521000001,
                "curve_type": "managed_species_prop_HW",
            },
            {
                "curve_id": 985501000001,
                "curve_type": "unmanaged_species_prop_HW",
            },
        ]
    ).to_csv(bundle_dir / "curve_table.csv", index=False)
    pd.DataFrame(
        [
            {"curve_id": 985501000, "x": 1, "y": 10.0},
            {"curve_id": 985501000, "x": 10, "y": 55.0},
            {"curve_id": 985521000, "x": 1, "y": 12.0},
            {"curve_id": 985521000, "x": 10, "y": 70.0},
            {"curve_id": 985521000001, "x": 1, "y": 0.7},
            {"curve_id": 985501000001, "x": 1, "y": 0.6},
        ]
    ).to_csv(bundle_dir / "curve_points_table.csv", index=False)


def test_build_forestmodel_xml_tree_contains_cc_and_curve_refs() -> None:
    au_table = pd.DataFrame(
        [
            {
                "au_id": 985501000,
                "tsa": "k3z",
                "stratum_code": "CWHvm_HW+FDC",
                "si_level": "L",
                "managed_curve_id": 985521000,
                "unmanaged_curve_id": 985501000,
            }
        ]
    )
    curve_table = pd.DataFrame(
        [
            {"curve_id": 985501000, "curve_type": "unmanaged"},
            {"curve_id": 985521000, "curve_type": "managed"},
        ]
    )
    curve_points = pd.DataFrame(
        [
            {"curve_id": 985501000, "x": 1, "y": 10.0},
            {"curve_id": 985521000, "x": 1, "y": 12.0},
        ]
    )
    root = build_forestmodel_xml_tree(
        au_table=au_table,
        curve_table=curve_table,
        curve_points_table=curve_points,
    )
    xml_text = et.tostring(root, encoding="unicode")
    assert "treatment" in xml_text
    assert 'label="CC"' in xml_text
    assert "feature.Yield.managed.Total" in xml_text
    assert "product.Yield.managed.Total" in xml_text
    assert "AU eq '985501000'" in xml_text


def test_build_patchworks_forestmodel_definition_contains_treatment() -> None:
    au_table = pd.DataFrame(
        [
            {
                "au_id": 985501000,
                "tsa": "k3z",
                "stratum_code": "CWHvm_HW+FDC",
                "si_level": "L",
                "managed_curve_id": 985521000,
                "unmanaged_curve_id": 985501000,
            }
        ]
    )
    curve_table = pd.DataFrame(
        [
            {"curve_id": 985501000, "curve_type": "unmanaged"},
            {"curve_id": 985521000, "curve_type": "managed"},
        ]
    )
    curve_points = pd.DataFrame(
        [
            {"curve_id": 985501000, "x": 1, "y": 10.0},
            {"curve_id": 985521000, "x": 1, "y": 12.0},
        ]
    )
    from femic.fmg.adapters import build_bundle_model_context_from_tables

    context = build_bundle_model_context_from_tables(
        au_table=au_table,
        curve_table=curve_table,
        curve_points_table=curve_points,
        tsa_list=["k3z"],
    )
    definition = build_patchworks_forestmodel_definition(context=context)
    assert definition.define_fields[0].field == "AU"
    treatment_selects = [s for s in definition.selects if s.track_treatment is not None]
    assert any(
        s.track_treatment is not None and s.track_treatment.label == "CC"
        for s in treatment_selects
    )
    assert any(
        any(
            a.field == "IFM" and a.value == "'managed'"
            for a in s.track_treatment.transition_assignments
        )
        for s in treatment_selects
        if s.track_treatment is not None
    )


def test_export_patchworks_package_writes_xml_and_fragments(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle_dir = tmp_path / "bundle"
    _write_bundle_tables(bundle_dir)
    checkpoint_path = tmp_path / "checkpoint7.feather"
    output_dir = tmp_path / "patchworks_export"

    checkpoint_df = pd.DataFrame(
        [
            {
                "tsa_code": "k3z",
                "au": 985501000,
                "PROJ_AGE_1": 74,
                "FEATURE_AREA_SQM": 12000.0,
                "thlb_raw": 1,
                "geometry": Polygon([(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)]),
            }
        ]
    )
    monkeypatch.setattr(
        "femic.fmg.patchworks.pd.read_feather", lambda _path: checkpoint_df
    )

    result = export_patchworks_package(
        bundle_dir=bundle_dir,
        checkpoint_path=checkpoint_path,
        output_dir=output_dir,
        tsa_list=["k3z"],
    )

    assert result.forestmodel_xml_path.is_file()
    assert result.fragments_shapefile_path.is_file()
    xml_text = result.forestmodel_xml_path.read_text(encoding="utf-8")
    assert '<!DOCTYPE ForestModel SYSTEM "ForestModel.dtd">' in xml_text
    assert "feature.Yield.unmanaged.Total" in xml_text
    gdf = gpd.read_file(result.fragments_shapefile_path)
    assert set(["BLOCK", "AREA_HA", "F_AGE", "AU", "IFM"]).issubset(gdf.columns)
    assert int(gdf.loc[0, "AU"]) == 985501000
    assert gdf.loc[0, "IFM"] == "managed"


def test_export_patchworks_package_decodes_wkb_geometry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle_dir = tmp_path / "bundle"
    _write_bundle_tables(bundle_dir)
    checkpoint_path = tmp_path / "checkpoint7.feather"
    output_dir = tmp_path / "patchworks_export"

    geom = Polygon([(0, 0), (40, 0), (40, 40), (0, 40), (0, 0)])
    checkpoint_df = pd.DataFrame(
        [
            {
                "tsa_code": "k3z",
                "au": 985501000,
                "PROJ_AGE_1": 61,
                "thlb_raw": 0,
                "geometry": geom.wkb,
            }
        ]
    )
    monkeypatch.setattr(
        "femic.fmg.patchworks.pd.read_feather", lambda _path: checkpoint_df
    )

    result = export_patchworks_package(
        bundle_dir=bundle_dir,
        checkpoint_path=checkpoint_path,
        output_dir=output_dir,
        tsa_list=["k3z"],
    )

    gdf = gpd.read_file(result.fragments_shapefile_path)
    assert gdf.shape[0] == 1
    assert gdf.loc[0, "IFM"] == "unmanaged"
    assert gdf.geometry.iloc[0].geom_type == "Polygon"


def test_validate_forestmodel_xml_tree_rejects_missing_curve_ref() -> None:
    au_table = pd.DataFrame(
        [
            {
                "au_id": 985501000,
                "tsa": "k3z",
                "stratum_code": "CWHvm_HW+FDC",
                "si_level": "L",
                "managed_curve_id": 985521000,
                "unmanaged_curve_id": 985501000,
            }
        ]
    )
    curve_table = pd.DataFrame(
        [
            {"curve_id": 985501000, "curve_type": "unmanaged"},
            {"curve_id": 985521000, "curve_type": "managed"},
        ]
    )
    curve_points = pd.DataFrame(
        [
            {"curve_id": 985501000, "x": 1, "y": 10.0},
            {"curve_id": 985521000, "x": 1, "y": 12.0},
        ]
    )
    root = build_forestmodel_xml_tree(
        au_table=au_table,
        curve_table=curve_table,
        curve_points_table=curve_points,
    )
    managed_curve_node = root.find("./curve[@id='C985521000']")
    assert managed_curve_node is not None
    root.remove(managed_curve_node)

    with pytest.raises(ValueError, match="idref"):
        validate_forestmodel_xml_tree(root=root)


def test_validate_fragments_geodataframe_rejects_invalid_ifm() -> None:
    gdf = gpd.GeoDataFrame(
        {
            "BLOCK": [1],
            "AREA_HA": [1.0],
            "F_AGE": [10],
            "AU": [100],
            "IFM": ["bogus"],
            "TSA": ["k3z"],
            "geometry": [Polygon([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])],
        },
        geometry="geometry",
        crs="EPSG:3005",
    )

    with pytest.raises(ValueError, match="IFM contains invalid values"):
        validate_fragments_geodataframe(fragments_gdf=gdf)


def test_write_forestmodel_xml_matches_fixture(tmp_path: Path) -> None:
    au_table = pd.DataFrame(
        [
            {
                "au_id": 985501000,
                "tsa": "k3z",
                "stratum_code": "CWHvm_HW+FDC",
                "si_level": "L",
                "managed_curve_id": 985521000,
                "unmanaged_curve_id": 985501000,
            }
        ]
    )
    curve_table = pd.DataFrame(
        [
            {"curve_id": 985501000, "curve_type": "unmanaged"},
            {"curve_id": 985521000, "curve_type": "managed"},
        ]
    )
    curve_points = pd.DataFrame(
        [
            {"curve_id": 985501000, "x": 1, "y": 10.0},
            {"curve_id": 985501000, "x": 10, "y": 55.0},
            {"curve_id": 985521000, "x": 1, "y": 12.0},
            {"curve_id": 985521000, "x": 10, "y": 70.0},
        ]
    )
    root = build_forestmodel_xml_tree(
        au_table=au_table,
        curve_table=curve_table,
        curve_points_table=curve_points,
    )
    out_path = tmp_path / "forestmodel.xml"
    write_forestmodel_xml(root=root, path=out_path)

    expected = Path("tests/fixtures/fmg/forestmodel_minimal.xml").read_text(
        encoding="utf-8"
    )
    actual = out_path.read_text(encoding="utf-8")
    assert actual == expected


def test_write_forestmodel_xml_matches_multi_au_fixture(tmp_path: Path) -> None:
    au_table = pd.DataFrame(
        [
            {
                "au_id": 1001,
                "tsa": "29",
                "stratum_code": "SBPS_PLI",
                "si_level": "L",
                "managed_curve_id": 21001,
                "unmanaged_curve_id": 1001,
            },
            {
                "au_id": 1002,
                "tsa": "29",
                "stratum_code": "IDF_FD",
                "si_level": "M",
                "managed_curve_id": 21002,
                "unmanaged_curve_id": 1002,
            },
        ]
    )
    curve_table = pd.DataFrame(
        [
            {"curve_id": 1001, "curve_type": "unmanaged"},
            {"curve_id": 1002, "curve_type": "unmanaged"},
            {"curve_id": 21001, "curve_type": "managed"},
            {"curve_id": 21002, "curve_type": "managed"},
            {"curve_id": 1001001, "curve_type": "unmanaged_species_prop_PL"},
            {"curve_id": 1001002, "curve_type": "unmanaged_species_prop_FD"},
            {"curve_id": 1002001, "curve_type": "unmanaged_species_prop_SW"},
            {"curve_id": 1002002, "curve_type": "unmanaged_species_prop_AT"},
            {"curve_id": 21001001, "curve_type": "managed_species_prop_PL"},
            {"curve_id": 21001002, "curve_type": "managed_species_prop_FD"},
            {"curve_id": 21002001, "curve_type": "managed_species_prop_SW"},
            {"curve_id": 21002002, "curve_type": "managed_species_prop_AT"},
        ]
    )
    curve_points = pd.DataFrame(
        [
            {"curve_id": 1001, "x": 1, "y": 5.0},
            {"curve_id": 1001, "x": 10, "y": 40.0},
            {"curve_id": 1002, "x": 1, "y": 6.0},
            {"curve_id": 1002, "x": 10, "y": 50.0},
            {"curve_id": 21001, "x": 1, "y": 8.0},
            {"curve_id": 21001, "x": 10, "y": 65.0},
            {"curve_id": 21002, "x": 1, "y": 9.0},
            {"curve_id": 21002, "x": 10, "y": 72.0},
            {"curve_id": 1001001, "x": 1, "y": 0.70},
            {"curve_id": 1001002, "x": 1, "y": 0.30},
            {"curve_id": 1002001, "x": 1, "y": 0.55},
            {"curve_id": 1002002, "x": 1, "y": 0.45},
            {"curve_id": 21001001, "x": 1, "y": 0.80},
            {"curve_id": 21001002, "x": 1, "y": 0.20},
            {"curve_id": 21002001, "x": 1, "y": 0.60},
            {"curve_id": 21002002, "x": 1, "y": 0.40},
        ]
    )
    root = build_forestmodel_xml_tree(
        au_table=au_table,
        curve_table=curve_table,
        curve_points_table=curve_points,
    )
    out_path = tmp_path / "forestmodel_multi.xml"
    write_forestmodel_xml(root=root, path=out_path)

    expected = Path("tests/fixtures/fmg/forestmodel_multi_au.xml").read_text(
        encoding="utf-8"
    )
    actual = out_path.read_text(encoding="utf-8")
    assert actual == expected
