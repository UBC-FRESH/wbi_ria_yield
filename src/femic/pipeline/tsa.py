"""TSA-level constants and helpers."""

from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

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


def build_stratum_lexmatch_alias_map(
    *,
    f_table: Any,
    stratum_col: str,
    selected_strata_codes: Sequence[str],
    levenshtein_fn: Callable[[str, str], int],
) -> dict[str, str]:
    """Build best-match aliases from non-selected lexmatch strata to selected strata."""
    selected_codes = list(selected_strata_codes)
    names1 = set(f_table.loc[selected_codes].stratum_lexmatch.dropna().unique())
    names2 = set(f_table.stratum_lexmatch.dropna().unique()) - names1
    if not names1 or not names2:
        return {}

    stratum_key = (
        f_table.reset_index().groupby(f"{stratum_col}_lexmatch")[stratum_col].first()
    )
    totalarea_p_sum = f_table.groupby(f"{stratum_col}_lexmatch").totalarea_p.sum()
    lev_dist = {n2: {n1: levenshtein_fn(n1, n2) for n1 in names1} for n2 in names2}
    lev_dist_low = {
        n2: {
            n1: (lev_dist[n2][n1], totalarea_p_sum.loc[n1])
            for n1 in lev_dist[n2]
            if lev_dist[n2][n1] == min(lev_dist[n2].values())
        }
        for n2 in names2
    }
    return {
        stratum_key.loc[n2]: stratum_key[
            max(lev_dist_low[n2].items(), key=lambda i: i[1])[0]
        ]
        for n2 in names2
    }


def apply_stratum_alias_map(
    *,
    f_table: Any,
    stratum_col: str,
    selected_strata_codes: Sequence[str],
    best_match: Mapping[str, str],
) -> str:
    """Apply selected+alias stratum mapping and return matched-column name."""
    selected = set(selected_strata_codes)
    matched_col = f"{stratum_col}_matched"
    f_table[matched_col] = [
        key if key in selected else best_match.get(key, key)
        for key in f_table[stratum_col].values
    ]
    return matched_col
