"""Helpers for legacy species-volume compilation orchestration."""

from __future__ import annotations

import itertools
from typing import Any, Callable, Sequence


def species_volume_input_columns(
    *,
    slot_count: int = 6,
) -> list[str]:
    """Build required input columns for per-species live-volume compilation."""
    return list(
        itertools.chain.from_iterable(
            [f"LIVE_VOL_PER_HA_SPP{idx}_125", f"SPECIES_CD_{idx}"]
            for idx in range(1, int(slot_count) + 1)
        )
    )


def compile_species_volume_series(
    table: Any,
    species: str,
    *,
    slot_count: int = 6,
) -> Any:
    """Compile one species live-volume series from per-slot species columns."""
    return table.apply(
        lambda row: sum(
            row[f"LIVE_VOL_PER_HA_SPP{idx}_125"]
            for idx in range(1, int(slot_count) + 1)
            if row[f"SPECIES_CD_{idx}"] == species
        ),
        axis=1,
    )


def compile_species_volume_columns(
    *,
    f_table: Any,
    species_list: Sequence[str],
    map_async_fn: Callable[..., Any],
    wait_fn: Callable[[], Any],
    compile_fn: Callable[..., Any] = compile_species_volume_series,
    slot_count: int = 6,
    out_col_prefix: str = "live_vol_per_ha_125_",
    ordered: bool = True,
    message_fn: Callable[..., Any] = print,
) -> Any:
    """Dispatch per-species compilation and assign resulting output columns."""
    out = f_table.copy()
    cols = species_volume_input_columns(slot_count=slot_count)
    table = out[cols]
    result = map_async_fn(
        compile_fn,
        [table] * len(species_list),
        list(species_list),
        ordered=ordered,
    )
    wait_fn()

    for idx, species in enumerate(species_list):
        message_fn("compiling species", species)
        out[f"{out_col_prefix}{species}"] = result[idx]
    return out
