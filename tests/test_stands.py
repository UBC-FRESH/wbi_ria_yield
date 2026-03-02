from __future__ import annotations

from pathlib import Path

import pandas as pd

from femic.pipeline.stands import (
    build_stands_column_map,
    clean_stand_geometry,
    export_stands_shapefiles,
    extract_stand_features_for_tsa,
    prepare_stands_export_frame,
    should_skip_stands_export,
)
import pytest


def test_should_skip_stands_export_defaults_and_overrides() -> None:
    assert should_skip_stands_export(skip_raw=None, default_skip=True) is True
    assert should_skip_stands_export(skip_raw=None, default_skip=False) is False
    assert should_skip_stands_export(skip_raw="1", default_skip=False) is True
    assert should_skip_stands_export(skip_raw="false", default_skip=True) is False


def test_build_stands_column_map() -> None:
    mapping = build_stands_column_map()
    assert mapping["tsa_code"] == "theme0"
    assert mapping["FEATURE_AREA_SQM"] == "area"


def test_extract_and_prepare_stands_export_frame() -> None:
    class _Geom:
        is_valid = True

    f_table = pd.DataFrame(
        [
            {
                "geometry": _Geom(),
                "tsa_code": "08",
                "thlb": 1,
                "au": 800005,
                "curve1": 820005,
                "curve2": 800005,
                "SPECIES_CD_1": "SW",
                "PROJ_AGE_1": 50,
                "FEATURE_AREA_SQM": 10000.0,
            }
        ]
    )
    au_table = pd.DataFrame([{"au_id": 800005, "canfi_species": 105}])
    extracted = extract_stand_features_for_tsa(
        f_table=f_table,
        tsa_code="08",
        clean_geometry_fn=lambda g: g,
    )
    prepared = prepare_stands_export_frame(
        f_tsa=extracted,
        columns_map=build_stands_column_map(),
        au_table=au_table,
        pd_module=pd,
    )

    assert prepared.loc[0, "theme0"] == "tsa08"
    assert int(prepared.loc[0, "theme2"]) == 800005
    assert int(prepared.loc[0, "theme3"]) == 105
    assert float(prepared.loc[0, "area"]) == 1.0


def test_export_stands_shapefiles_with_stubbed_frame(tmp_path: Path) -> None:
    calls: list[tuple[str, str]] = []

    class _Frame:
        def to_file(self, path: Path) -> None:
            calls.append(("to_file", str(path)))

    def _extract_features_fn(*, f_table: object, tsa_code: str) -> object:
        return {"tsa": tsa_code, "f": f_table}

    def _prepare_frame_fn(
        *,
        f_tsa: object,
        columns_map: dict[str, str],
        au_table: object,
        pd_module: object,
    ) -> _Frame:
        calls.append(("prepare", str(f_tsa)))
        return _Frame()

    export_stands_shapefiles(
        tsa_list=["08"],
        f_table="f-table",
        au_table="au-table",
        columns_map={"a": "b"},
        output_root=tmp_path,
        pd_module=pd,
        extract_features_fn=_extract_features_fn,
        prepare_frame_fn=_prepare_frame_fn,
        message_fn=lambda _m: None,
    )

    assert calls[0][0] == "prepare"
    assert calls[1][0] == "to_file"
    assert calls[1][1].endswith("tsa08.shp/stands.shp")


def test_clean_stand_geometry_raises_when_cleanup_still_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Geom:
        is_valid = False

        @staticmethod
        def buffer(_distance: int) -> str:
            return "buffered"

    class _BadMultiPolygon:
        def __init__(self, _parts: object) -> None:
            self.is_valid = False
            self.geom_type = "MultiPolygon"

    class _FakeModule:
        MultiPolygon = _BadMultiPolygon

    import builtins

    real_import = builtins.__import__

    def _patched_import(
        name: str,
        globals: object = None,
        locals: object = None,
        fromlist: object = (),
        level: int = 0,
    ) -> object:
        if name == "shapely.geometry":
            return _FakeModule()
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _patched_import)

    with pytest.raises(ValueError, match="remained invalid"):
        clean_stand_geometry(_Geom())


def test_clean_stand_geometry_raises_when_cleanup_not_multipolygon(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Geom:
        is_valid = False

        @staticmethod
        def buffer(_distance: int) -> str:
            return "buffered"

    class _BadMultiPolygon:
        def __init__(self, _parts: object) -> None:
            self.is_valid = True
            self.geom_type = "Polygon"

    class _FakeModule:
        MultiPolygon = _BadMultiPolygon

    import builtins

    real_import = builtins.__import__

    def _patched_import(
        name: str,
        globals: object = None,
        locals: object = None,
        fromlist: object = (),
        level: int = 0,
    ) -> object:
        if name == "shapely.geometry":
            return _FakeModule()
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _patched_import)

    with pytest.raises(ValueError, match="Expected MultiPolygon"):
        clean_stand_geometry(_Geom())
