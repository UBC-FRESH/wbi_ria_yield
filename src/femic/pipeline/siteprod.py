"""Helpers for legacy site productivity raster export/stack orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping


def parse_arc_raster_rescue_layer_mappings(
    *,
    stdout_text: str,
) -> tuple[dict[int, str], dict[str, int]]:
    """Parse ArcRasterRescue layer listing into index<->species mappings."""
    lines = [line.strip() for line in stdout_text.splitlines()[1:] if line.strip()]
    layer_species = {
        int(layer_index): layer_name[10:].upper()
        for layer_index, layer_name in (line.split(" ", 1) for line in lines)
    }
    species_layer = {species: layer for layer, species in layer_species.items()}
    return layer_species, species_layer


def list_siteprod_layers(
    *,
    arc_raster_rescue_exe_path: str | Path,
    siteprod_gdb_path: str | Path,
    run_fn: Callable[..., Any],
) -> tuple[dict[int, str], dict[str, int]]:
    """Run ArcRasterRescue layer listing and return parsed species mappings."""
    result = run_fn(
        [arc_raster_rescue_exe_path, siteprod_gdb_path],
        capture_output=True,
    )
    return parse_arc_raster_rescue_layer_mappings(
        stdout_text=result.stdout.decode(),
    )


def build_siteprod_layer_tif_path(
    *,
    siteprod_tmpexport_tif_path_prefix: str | Path,
    species: str,
) -> Path:
    """Build temporary GeoTIFF path for one species export."""
    prefix = Path(siteprod_tmpexport_tif_path_prefix)
    return prefix.parent / f"{prefix.name}{species}.tif"


def enumerate_siteprod_layer_tif_paths(
    *,
    siteprod_tmpexport_tif_path_prefix: str | Path,
) -> list[Path]:
    """Enumerate exported temporary siteprod layer GeoTIFF paths."""
    prefix = Path(siteprod_tmpexport_tif_path_prefix)
    return sorted(prefix.parent.glob(f"{prefix.name}*.tif"))


def export_and_stack_siteprod_layers(
    *,
    arc_raster_rescue_exe_path: str | Path,
    site_prod_bc_gdb_path: str | Path,
    site_prod_bc_layerspecies: Mapping[int, str],
    siteprod_layerspecies: Mapping[int, str],
    siteprod_tmpexport_tif_path_prefix: str | Path,
    siteprod_tif_path: str | Path,
    run_fn: Callable[..., Any],
    rio_module: Any,
    message_fn: Callable[..., Any] = print,
) -> None:
    """Export per-species rasters, stack into one GeoTIFF, and clean temps."""
    for layer_index, species in site_prod_bc_layerspecies.items():
        message_fn("... processing species", species)
        run_fn(
            [
                arc_raster_rescue_exe_path,
                site_prod_bc_gdb_path,
                str(layer_index),
                build_siteprod_layer_tif_path(
                    siteprod_tmpexport_tif_path_prefix=siteprod_tmpexport_tif_path_prefix,
                    species=species,
                ),
            ]
        )

    file_list = enumerate_siteprod_layer_tif_paths(
        siteprod_tmpexport_tif_path_prefix=siteprod_tmpexport_tif_path_prefix
    )
    with rio_module.open(file_list[0]) as src:
        meta = src.meta
        meta.update(
            count=len(file_list),
            compress="lzw",
            crs=rio_module.crs.CRS({"init": "epsg:3005"}),
        )

    with rio_module.open(siteprod_tif_path, "w", **meta) as dst:
        message_fn(
            "\nStacking siteprod raster data into a single multiband GeoTIFF file..."
        )
        for idx, layer in enumerate(file_list, start=1):
            message_fn("... processing species", siteprod_layerspecies[idx - 1])
            with rio_module.open(layer) as src:
                dst.write_band(idx, src.read(1))
            layer.unlink()
