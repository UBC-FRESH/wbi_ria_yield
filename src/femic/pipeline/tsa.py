"""TSA-level constants and helpers."""

from __future__ import annotations


TARGET_NSTRATA_BY_TSA: dict[str, int] = {
    "08": 9,
    "16": 13,
    "24": 8,
    "40": 7,
    "41": 10,
}


def target_nstrata_for(tsa_code: str) -> int:
    """Return configured target number of strata for a TSA code."""
    tsa = str(tsa_code).zfill(2)
    return TARGET_NSTRATA_BY_TSA[tsa]
