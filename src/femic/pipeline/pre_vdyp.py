"""Pre-VDYP stage helpers extracted from legacy TSA runner."""

from __future__ import annotations

import copy
from pathlib import Path
import pickle
from typing import Any


def serialize_vdyp_prep_payload(results_tsa: list[list[Any]]) -> list[list[Any]]:
    """Copy and sanitize pre-VDYP fit payload for checkpoint persistence."""
    payload: list[list[Any]] = []
    for stratumi, sc, fit_out in results_tsa:
        fit_out_clean = copy.deepcopy(fit_out)
        for si_level_data in fit_out_clean.values():
            for species_data in si_level_data["species"].values():
                species_data.pop("fit_func", None)
        payload.append([stratumi, sc, fit_out_clean])
    return payload


def pre_vdyp_checkpoint_path(
    *,
    tsa_code: str,
    base_dir: str | Path = "data",
) -> Path:
    """Build per-TSA pre-VDYP checkpoint path."""
    tsa = str(tsa_code).zfill(2)
    return Path(base_dir) / f"vdyp_prep-tsa{tsa}.pkl"


def load_vdyp_prep_checkpoint(path: str | Path) -> list[list[Any]]:
    """Load pre-VDYP checkpoint payload from pickle."""
    checkpoint_path = Path(path)
    with checkpoint_path.open("rb") as f:
        loaded = pickle.load(f)
    if not isinstance(loaded, list):
        raise TypeError("pre-VDYP checkpoint payload must be a list")
    return loaded


def save_vdyp_prep_checkpoint(path: str | Path, results_tsa: list[list[Any]]) -> int:
    """Persist sanitized pre-VDYP payload and return number of strata saved."""
    checkpoint_path = Path(path)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    payload = serialize_vdyp_prep_payload(results_tsa)
    with checkpoint_path.open("wb") as f:
        pickle.dump(payload, f)
    return len(payload)
