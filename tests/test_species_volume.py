from __future__ import annotations

import pandas as pd

from femic.pipeline.species_volume import (
    compile_species_volume_columns,
    compile_species_volume_series,
    species_volume_input_columns,
)


def test_species_volume_input_columns_defaults() -> None:
    cols = species_volume_input_columns()
    assert cols[0] == "LIVE_VOL_PER_HA_SPP1_125"
    assert cols[1] == "SPECIES_CD_1"
    assert cols[-2] == "LIVE_VOL_PER_HA_SPP6_125"
    assert cols[-1] == "SPECIES_CD_6"


def test_compile_species_volume_series_sums_matching_slots() -> None:
    table = pd.DataFrame(
        {
            "LIVE_VOL_PER_HA_SPP1_125": [10.0, 5.0],
            "SPECIES_CD_1": ["SW", "PL"],
            "LIVE_VOL_PER_HA_SPP2_125": [3.0, 7.0],
            "SPECIES_CD_2": ["SW", "SW"],
            "LIVE_VOL_PER_HA_SPP3_125": [1.0, 2.0],
            "SPECIES_CD_3": ["PL", "SW"],
            "LIVE_VOL_PER_HA_SPP4_125": [0.0, 0.0],
            "SPECIES_CD_4": ["X", "X"],
            "LIVE_VOL_PER_HA_SPP5_125": [0.0, 0.0],
            "SPECIES_CD_5": ["X", "X"],
            "LIVE_VOL_PER_HA_SPP6_125": [0.0, 0.0],
            "SPECIES_CD_6": ["X", "X"],
        }
    )
    out = compile_species_volume_series(table, "SW")
    assert list(out) == [13.0, 9.0]


def test_compile_species_volume_columns_dispatches_and_assigns() -> None:
    frame = pd.DataFrame(
        {
            "LIVE_VOL_PER_HA_SPP1_125": [10.0],
            "SPECIES_CD_1": ["SW"],
            "LIVE_VOL_PER_HA_SPP2_125": [4.0],
            "SPECIES_CD_2": ["PL"],
            "LIVE_VOL_PER_HA_SPP3_125": [0.0],
            "SPECIES_CD_3": ["X"],
            "LIVE_VOL_PER_HA_SPP4_125": [0.0],
            "SPECIES_CD_4": ["X"],
            "LIVE_VOL_PER_HA_SPP5_125": [0.0],
            "SPECIES_CD_5": ["X"],
            "LIVE_VOL_PER_HA_SPP6_125": [0.0],
            "SPECIES_CD_6": ["X"],
        }
    )
    waits: list[bool] = []
    calls: list[tuple[object, list[pd.DataFrame], list[str], bool]] = []

    def _map_async(
        func: object, tables: list[pd.DataFrame], species_list: list[str], ordered: bool
    ) -> list[pd.Series]:
        calls.append((func, tables, species_list, ordered))
        return [
            compile_species_volume_series(tables[0], species)
            for species in species_list
        ]

    def _wait() -> None:
        waits.append(True)

    messages: list[tuple[str, str]] = []
    out = compile_species_volume_columns(
        f_table=frame,
        species_list=["SW", "PL"],
        map_async_fn=_map_async,
        wait_fn=_wait,
        message_fn=lambda *args: messages.append((str(args[0]), str(args[1]))),
    )

    assert waits == [True]
    assert calls and calls[0][3] is True
    assert out["live_vol_per_ha_125_SW"].iloc[0] == 10.0
    assert out["live_vol_per_ha_125_PL"].iloc[0] == 4.0
    assert ("compiling species", "SW") in messages
