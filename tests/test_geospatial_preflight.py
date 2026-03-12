from __future__ import annotations

from types import SimpleNamespace

import pytest

from femic import geospatial_preflight


def test_detect_os_family_normalizes_platform_names() -> None:
    assert geospatial_preflight.detect_os_family("Windows") == "windows"
    assert geospatial_preflight.detect_os_family("Linux") == "linux"
    assert geospatial_preflight.detect_os_family("Darwin") == "macos"
    assert geospatial_preflight.detect_os_family("UnknownOS") == "other"


def test_run_geospatial_preflight_reports_missing_fiona(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(geospatial_preflight, "detect_os_family", lambda: "windows")

    def _missing(_name: str) -> object:
        raise ModuleNotFoundError("no module named fiona")

    monkeypatch.setattr(geospatial_preflight.importlib, "import_module", _missing)

    result = geospatial_preflight.run_geospatial_preflight()

    assert not result.ok
    assert result.os_family == "windows"
    assert result.gdal_version is None
    assert result.errors
    assert "fiona" in result.errors[0]
    assert "Windows" in result.install_hint


def test_run_geospatial_preflight_success_with_visible_gdal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(geospatial_preflight, "detect_os_family", lambda: "linux")
    monkeypatch.setattr(
        geospatial_preflight.importlib,
        "import_module",
        lambda _name: SimpleNamespace(__gdal_version__="3.8.5"),
    )
    monkeypatch.setattr(
        geospatial_preflight,
        "_run_shapefile_smoke",
        lambda _module: ((), ()),
    )

    result = geospatial_preflight.run_geospatial_preflight()

    assert result.ok
    assert result.os_family == "linux"
    assert result.gdal_version == "3.8.5"
    assert result.errors == ()
    assert result.warnings == ()


def test_run_geospatial_preflight_surfaces_shapefile_smoke_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(geospatial_preflight, "detect_os_family", lambda: "linux")
    monkeypatch.setattr(
        geospatial_preflight.importlib,
        "import_module",
        lambda _name: SimpleNamespace(__gdal_version__="3.8.5"),
    )
    monkeypatch.setattr(
        geospatial_preflight,
        "_run_shapefile_smoke",
        lambda _module: (("smoke failed",), ()),
    )

    result = geospatial_preflight.run_geospatial_preflight()

    assert not result.ok
    assert result.errors == ("smoke failed",)
