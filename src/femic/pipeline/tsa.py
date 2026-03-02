"""TSA-level constants and helpers."""

from __future__ import annotations

from typing import Any

TARGET_NSTRATA_BY_TSA: dict[str, int] = {
    "08": 9,
    "16": 13,
    "24": 8,
    "40": 7,
    "41": 10,
}
MIN_STANDCOUNT = 1000


def target_nstrata_for(tsa_code: str) -> int:
    """Return configured target number of strata for a TSA code."""
    tsa = str(tsa_code).zfill(2)
    return TARGET_NSTRATA_BY_TSA[tsa]


def build_strata_summary(
    *,
    f_table: Any,
    stratum_col: str,
    pd_module: Any,
    tsa_code: str | None = None,
    target_nstrata: int | None = None,
    min_standcount: int = MIN_STANDCOUNT,
) -> tuple[Any, list[str], float]:
    """Build per-stratum summary table used by legacy TSA orchestration."""
    resolved_target = target_nstrata
    if resolved_target is None:
        if tsa_code is None:
            raise ValueError("either target_nstrata or tsa_code must be provided")
        resolved_target = target_nstrata_for(tsa_code)

    strata_gb1 = f_table.groupby(level=stratum_col)
    totalarea_p_sum = strata_gb1.totalarea_p.sum().nlargest(resolved_target)
    largestn_strata_codes = list(totalarea_p_sum.index.values)
    strata_gb2 = f_table.groupby(level=stratum_col)
    site_index_iqr = strata_gb2.SITE_INDEX.quantile(
        0.75
    ) - strata_gb2.SITE_INDEX.quantile(0.25)
    strata_df = pd_module.DataFrame(totalarea_p_sum)
    strata_df["site_index_std"] = strata_gb2.SITE_INDEX.std()
    strata_df["site_index_iqr"] = site_index_iqr
    strata_df["site_index_median"] = strata_gb2.SITE_INDEX.median()
    strata_df["stand_count"] = strata_gb2.FEATURE_ID.count()
    strata_df["coverage"] = strata_gb2.totalarea_p.sum()
    strata_df["crown_closure"] = strata_gb2.CROWN_CLOSURE.median()
    strata_df = strata_df[strata_df.stand_count >= min_standcount]
    strata_df = strata_df.head(resolved_target)
    strata_df["median_si"] = (
        f_table[f_table.index.isin(largestn_strata_codes)]
        .groupby(level=stratum_col)
        .SITE_INDEX.median()
    )
    return strata_df, largestn_strata_codes, float(site_index_iqr.mean())
