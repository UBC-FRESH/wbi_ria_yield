from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np

from femic.pipeline.siteprod import (
    build_siteprod_layer_tif_path,
    enumerate_siteprod_layer_tif_paths,
    export_and_stack_siteprod_layers,
    list_siteprod_layers,
    parse_arc_raster_rescue_layer_mappings,
)


def test_parse_arc_raster_rescue_layer_mappings() -> None:
    stdout = "layer name\n0 site_prod_sw\n1 site_prod_pl\n"
    layer_species, species_layer = parse_arc_raster_rescue_layer_mappings(
        stdout_text=stdout
    )
    assert layer_species == {0: "SW", 1: "PL"}
    assert species_layer == {"SW": 0, "PL": 1}


def test_build_and_enumerate_siteprod_temp_paths(tmp_path: Path) -> None:
    prefix = tmp_path / "site_prod_bc_"
    p1 = build_siteprod_layer_tif_path(
        siteprod_tmpexport_tif_path_prefix=prefix,
        species="SW",
    )
    p2 = build_siteprod_layer_tif_path(
        siteprod_tmpexport_tif_path_prefix=prefix,
        species="PL",
    )
    p1.write_text("x", encoding="utf-8")
    p2.write_text("x", encoding="utf-8")

    found = enumerate_siteprod_layer_tif_paths(
        siteprod_tmpexport_tif_path_prefix=prefix
    )
    assert found == sorted([p1, p2])


def test_list_siteprod_layers_uses_runner_output() -> None:
    def _run(cmd: list[object], capture_output: bool) -> SimpleNamespace:
        assert capture_output is True
        assert len(cmd) == 2
        return SimpleNamespace(stdout=b"layer name\n0 site_prod_sw\n")

    layer_species, species_layer = list_siteprod_layers(
        arc_raster_rescue_exe_path=Path("arc_raster_rescue.exe"),
        siteprod_gdb_path=Path("Site_Prod_BC.gdb"),
        run_fn=_run,
    )
    assert layer_species == {0: "SW"}
    assert species_layer == {"SW": 0}


def test_export_and_stack_siteprod_layers(tmp_path: Path) -> None:
    class _FakeSrc:
        def __init__(self, path: Path) -> None:
            self.path = path
            self.meta = {"driver": "GTiff", "dtype": "uint8", "height": 1, "width": 1}

        def __enter__(self) -> "_FakeSrc":
            return self

        def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
            return None

        def read(self, _band: int) -> np.ndarray:
            return np.array([[1]], dtype=np.uint8)

    class _FakeDst:
        def __init__(self, path: Path) -> None:
            self.path = path
            self.path.write_text("stack", encoding="utf-8")
            self.written_bands: list[int] = []

        def __enter__(self) -> "_FakeDst":
            return self

        def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
            return None

        def write_band(self, band: int, _arr: np.ndarray) -> None:
            self.written_bands.append(band)

    class _FakeRio:
        def __init__(self) -> None:
            self.crs = SimpleNamespace(CRS=lambda payload: payload)
            self.last_dst: _FakeDst | None = None

        def open(self, path: Path, mode: str = "r", **_kwargs: object) -> object:
            if mode == "w":
                self.last_dst = _FakeDst(Path(path))
                return self.last_dst
            return _FakeSrc(Path(path))

    commands: list[list[object]] = []

    def _run(cmd: list[object], capture_output: bool = False) -> SimpleNamespace:
        commands.append(cmd)
        out_path = Path(cmd[3])  # type: ignore[index]
        out_path.write_text("layer", encoding="utf-8")
        return SimpleNamespace(stdout=b"")

    prefix = tmp_path / "site_prod_bc_"
    out_tif = tmp_path / "siteprod.tif"
    fake_rio = _FakeRio()

    export_and_stack_siteprod_layers(
        arc_raster_rescue_exe_path=Path("arc_raster_rescue.exe"),
        site_prod_bc_gdb_path=Path("Site_Prod_BC.gdb"),
        site_prod_bc_layerspecies={1: "SW", 2: "PL"},
        siteprod_layerspecies={0: "SW", 1: "PL"},
        siteprod_tmpexport_tif_path_prefix=prefix,
        siteprod_tif_path=out_tif,
        run_fn=_run,
        rio_module=fake_rio,
        message_fn=lambda *_args: None,
    )

    assert len(commands) == 2
    assert out_tif.is_file()
    assert fake_rio.last_dst is not None
    assert fake_rio.last_dst.written_bands == [1, 2]
    assert (
        enumerate_siteprod_layer_tif_paths(siteprod_tmpexport_tif_path_prefix=prefix)
        == []
    )
