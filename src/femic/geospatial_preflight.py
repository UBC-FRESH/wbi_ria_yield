"""Cross-platform geospatial runtime preflight checks."""

from __future__ import annotations

from dataclasses import dataclass
import importlib
from pathlib import Path
import platform
import tempfile
from typing import Any


@dataclass(frozen=True)
class GeospatialPreflightResult:
    """Result payload for geospatial dependency readiness checks."""

    os_family: str
    install_hint: str
    gdal_version: str | None
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def ok(self) -> bool:
        """Whether all required geospatial checks passed."""
        return not self.errors


def detect_os_family(system_name: str | None = None) -> str:
    """Normalize host OS into a small set used for bootstrap guidance."""
    name = (system_name or platform.system()).strip().lower()
    if name.startswith("win"):
        return "windows"
    if name.startswith("linux"):
        return "linux"
    if name.startswith("darwin") or name.startswith("mac"):
        return "macos"
    return "other"


def geospatial_install_hint(os_family: str) -> str:
    """Return an OS-specific install ritual for Fiona/GDAL."""
    if os_family == "windows":
        return (
            "Windows: install binary wheels first, then verify with "
            "`python -m pip install --upgrade pip setuptools wheel && "
            "python -m pip install fiona`."
        )
    if os_family == "linux":
        return (
            "Linux: install GDAL system libs before pip install, for example "
            "`sudo apt-get install -y gdal-bin libgdal-dev && "
            "python -m pip install fiona`."
        )
    if os_family == "macos":
        return (
            "macOS: install GDAL via Homebrew first, then pip install, for example "
            "`brew install gdal && python -m pip install fiona`."
        )
    return "Install GDAL + Fiona for your platform, then rerun geospatial preflight."


def _run_shapefile_smoke(fiona_module: Any) -> tuple[tuple[str, ...], tuple[str, ...]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        with tempfile.TemporaryDirectory(prefix="femic_geo_smoke_") as tmpdir:
            shp_path = Path(tmpdir) / "smoke.shp"
            schema = {"geometry": "Point", "properties": {"id": "int"}}
            with fiona_module.open(
                shp_path,
                mode="w",
                driver="ESRI Shapefile",
                schema=schema,
                crs="EPSG:4326",
            ) as sink:
                sink.write(
                    {
                        "geometry": {"type": "Point", "coordinates": (0.0, 0.0)},
                        "properties": {"id": 1},
                    }
                )
            with fiona_module.open(shp_path, mode="r") as source:
                feature_count = sum(1 for _ in source)
            if feature_count != 1:
                errors.append(
                    "Shapefile I/O smoke test failed: expected 1 feature, "
                    f"got {feature_count}."
                )
    except Exception as exc:  # pragma: no cover - exact Fiona/GDAL failures vary
        errors.append(f"Shapefile I/O smoke test failed: {exc}")
    return tuple(errors), tuple(warnings)


def run_geospatial_preflight(
    *, run_shapefile_smoke: bool = True
) -> GeospatialPreflightResult:
    """Validate Fiona/GDAL importability and basic shapefile read/write support."""
    os_family = detect_os_family()
    install_hint = geospatial_install_hint(os_family=os_family)
    errors: list[str] = []
    warnings: list[str] = []
    gdal_version: str | None = None

    try:
        fiona_module = importlib.import_module("fiona")
    except ModuleNotFoundError:
        errors.append(
            "Python package `fiona` is not installed. "
            "FEMIC geospatial stages require Fiona/GDAL."
        )
        return GeospatialPreflightResult(
            os_family=os_family,
            install_hint=install_hint,
            gdal_version=None,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )
    except Exception as exc:
        errors.append(f"Unable to import `fiona`: {exc}")
        return GeospatialPreflightResult(
            os_family=os_family,
            install_hint=install_hint,
            gdal_version=None,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

    gdal_version = str(getattr(fiona_module, "__gdal_version__", "")).strip() or None
    if gdal_version is None:
        warnings.append("Fiona imported but GDAL version is not visible on the module.")

    if run_shapefile_smoke:
        smoke_errors, smoke_warnings = _run_shapefile_smoke(fiona_module)
        errors.extend(smoke_errors)
        warnings.extend(smoke_warnings)

    return GeospatialPreflightResult(
        os_family=os_family,
        install_hint=install_hint,
        gdal_version=gdal_version,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
