"""VDYP table I/O helpers extracted from legacy TSA runner."""

from __future__ import annotations

import csv
import io
import importlib
from pathlib import Path
import re
from typing import Any


def write_vdyp_infiles_plylyr(
    feature_ids: list[int] | Any,
    vdyp_ply: Any,
    vdyp_lyr: Any,
    vdyp_io_dirname: str = "vdyp_io",
    vdyp_ply_csv: str = "vdyp_ply.csv",
    vdyp_lyr_csv: str = "vdyp_lyr.csv",
) -> None:
    """Write filtered/sorted VDYP polygon and layer CSV input tables."""
    vdyp_io_dir = Path(vdyp_io_dirname)
    vdyp_io_dir.mkdir(parents=True, exist_ok=True)

    vdyp_ply_ = vdyp_ply[vdyp_ply.FEATURE_ID.isin(feature_ids)].copy()
    vdyp_ply_.sort_values(by="FEATURE_ID", inplace=True)
    vdyp_ply_.to_csv(
        vdyp_io_dir / vdyp_ply_csv,
        columns=list(vdyp_ply.columns)[:-5],
        index=False,
        quoting=csv.QUOTE_NONNUMERIC,
    )

    vdyp_lyr_ = vdyp_lyr[vdyp_lyr.FEATURE_ID.isin(vdyp_ply_.FEATURE_ID)].copy()
    vdyp_lyr_.sort_values(by="FEATURE_ID", inplace=True)
    vdyp_lyr_.to_csv(
        vdyp_io_dir / vdyp_lyr_csv,
        columns=list(vdyp_lyr.columns)[:-5],
        index=False,
        quoting=csv.QUOTE_NONNUMERIC,
    )


def import_vdyp_tables(filename: str | Path) -> dict[int, Any]:
    """Parse VDYP console output tables keyed by polygon id."""
    pd = importlib.import_module("pandas")

    text = Path(filename).read_text(encoding="utf-8", errors="ignore")
    chunks = re.findall(r"(?<=vvvvvvvvvv.).*?(?=\^)", text, re.DOTALL)
    result: dict[int, Any] = {}
    for chunk in chunks:
        lines = chunk.split("\n")
        polygon_match = re.search(r"(?<=Polygon:.)\d+", lines[0])
        if polygon_match is None:
            continue
        polygon_id = int(polygon_match.group())
        result_ = pd.read_fwf(
            io.StringIO(chunk),
            skiprows=[0, 2],
            index_col="Age",
            infer_nrows=200,
        )
        if isinstance(result_, pd.DataFrame):
            result[polygon_id] = result_
    return result
