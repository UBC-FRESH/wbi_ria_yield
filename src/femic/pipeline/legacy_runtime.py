"""Typed runtime payloads for legacy 00/01a/01b orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class Legacy01ARuntimeConfig:
    """Runtime payload passed from `00_data-prep.py` into `01a_run-tsa.py`."""

    resume_effective: bool
    force_run_vdyp: bool
    kwarg_overrides_for_tsa: dict[str, dict[str, Any]] | None
    vdyp_results_pickle_path: str | Path
    vdyp_input_pandl_path: str | Path
    vdyp_ply_feather_path: str | Path
    vdyp_lyr_feather_path: str | Path
    tipsy_params_columns: Sequence[str]
    tipsy_params_path_prefix: str | Path
    vdyp_cache_paths: Mapping[str, Path]
    vdyp_out_cache: dict[str, Any] | None = None
    curve_fit_impl: Any = None
