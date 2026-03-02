"""TSA-level constants and helpers."""

from __future__ import annotations

from pathlib import Path
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


def assign_stratum_matches_from_au_table(
    *,
    f_table: Any,
    au_table: Any,
    tsa_list: Sequence[str],
    stratum_col: str,
    levenshtein_fn: Callable[[str, str], int] | None = None,
    message_fn: Callable[[str], Any] = print,
) -> Any:
    """Assign `stratum_matched` values by TSA using AU-table strata as targets."""
    matched_col = f"{stratum_col}_matched"
    if levenshtein_fn is None:
        distance_mod = __import__("distance")
        levenshtein_fn = distance_mod.levenshtein
    table = f_table.copy()
    if "FEATURE_ID" not in table.columns:
        table = table.reset_index()
    if matched_col not in table.columns:
        table[matched_col] = None

    table = table.set_index("FEATURE_ID")
    for tsa in tsa_list:
        message_fn(f"matching tsa {tsa}")
        strata_candidates = au_table.loc[
            au_table["tsa"] == tsa, "stratum_code"
        ].unique()
        selected_strata_codes = [str(code) for code in strata_candidates]
        if not selected_strata_codes:
            continue

        tsa_rows = table.loc[table["tsa_code"] == tsa].copy().reset_index()
        if tsa_rows.empty:
            continue
        tsa_rows = tsa_rows.set_index(stratum_col)
        totalarea = tsa_rows.FEATURE_AREA_SQM.sum()
        if float(totalarea) <= 0.0:
            continue
        tsa_rows["totalarea_p"] = tsa_rows.FEATURE_AREA_SQM / totalarea
        best_match = build_stratum_lexmatch_alias_map(
            f_table=tsa_rows,
            stratum_col=stratum_col,
            selected_strata_codes=selected_strata_codes,
            levenshtein_fn=levenshtein_fn,
        )
        tsa_rows = tsa_rows.reset_index()
        apply_stratum_alias_map(
            f_table=tsa_rows,
            stratum_col=stratum_col,
            selected_strata_codes=selected_strata_codes,
            best_match=best_match,
        )
        matched = tsa_rows[["FEATURE_ID", matched_col]].set_index("FEATURE_ID")[
            matched_col
        ]
        table[matched_col] = matched.where(~matched.isnull(), table[matched_col])
    return table


def assign_si_levels_from_stratum_quantiles(
    *,
    f_table: Any,
    si_levelquants: Mapping[str, Sequence[int]],
    stratum_matched_col: str = "stratum_matched",
    site_index_col: str = "SITE_INDEX",
    si_level_col: str = "si_level",
    message_fn: Callable[[str], Any] = print,
) -> tuple[Any, Any]:
    """Assign SI-level labels within each matched stratum from configured quantile bands."""
    table = f_table.copy()
    stratum_si_stats = table.groupby(stratum_matched_col)[site_index_col].describe(
        percentiles=[0, 0.05, 0.20, 0.35, 0.5, 0.65, 0.80, 0.95, 1]
    )
    for stratum_code in stratum_si_stats.index:
        message_fn(str(stratum_code))
        for si_level, quantiles in si_levelquants.items():
            q_lo, _q_mid, q_hi = [int(v) for v in quantiles]
            si_lo = stratum_si_stats.loc[stratum_code].loc[f"{q_lo}%"]
            si_hi = stratum_si_stats.loc[stratum_code].loc[f"{q_hi}%"]
            table.loc[
                (table[stratum_matched_col] == stratum_code)
                & (table[site_index_col] >= si_lo)
                & (table[site_index_col] <= si_hi),
                si_level_col,
            ] = si_level
    return table, stratum_si_stats


def lookup_scsi_au_base(
    *,
    scsi_au: Mapping[str, Mapping[tuple[str, str], int]],
    tsa_code: Any,
    stratum_code: Any,
    si_level: Any,
) -> int | None:
    """Lookup base AU id for a TSA/stratum/SI combination."""
    tsa_map = scsi_au.get(str(tsa_code))
    if not tsa_map:
        return None
    return tsa_map.get((str(stratum_code), str(si_level)))


def assign_au_ids_from_scsi(
    *,
    f_table: Any,
    scsi_au: Mapping[str, Mapping[tuple[str, str], int]],
    tsa_col: str = "tsa_code",
    stratum_matched_col: str = "stratum_matched",
    si_level_col: str = "si_level",
    au_col: str = "au",
) -> Any:
    """Assign absolute AU ids from `scsi_au` lookup map."""
    table = f_table.copy()
    table[au_col] = [
        (
            None
            if (
                (
                    au_base := lookup_scsi_au_base(
                        scsi_au=scsi_au,
                        tsa_code=tsa_code,
                        stratum_code=stratum_code,
                        si_level=si_level,
                    )
                )
                is None
            )
            else (100000 * int(tsa_code) + au_base)
        )
        for tsa_code, stratum_code, si_level in zip(
            table[tsa_col].values,
            table[stratum_matched_col].values,
            table[si_level_col].values,
        )
    ]
    return table


def summarize_missing_au_mappings(
    *,
    f_table: Any,
    au_col: str = "au",
    tsa_col: str = "tsa_code",
    stratum_matched_col: str = "stratum_matched",
    si_level_col: str = "si_level",
    top_n: int = 10,
) -> Any:
    """Return top-N missing AU mapping combinations for diagnostics."""
    return (
        f_table.loc[
            f_table[au_col].isnull(), [tsa_col, stratum_matched_col, si_level_col]
        ]
        .value_counts()
        .head(top_n)
    )


def emit_missing_au_mapping_warning(
    *,
    summary: Any,
    message_fn: Callable[[Any], Any] = print,
    header: str = "Warning: missing AU mappings for some strata (top 10 shown):",
) -> None:
    """Emit legacy warning lines for missing AU mapping diagnostics."""
    message_fn(header)
    message_fn(summary)


def build_au_assignment_null_summary(
    *,
    f_table: Any,
    site_index_col: str = "SITE_INDEX",
    stratum_matched_col: str = "stratum_matched",
    si_level_col: str = "si_level",
) -> dict[str, int | None]:
    """Build null-diagnostics summary used when AU assignment yields no rows."""
    return {
        "rows": int(len(f_table)),
        "site_index_null": int(f_table[site_index_col].isnull().sum())
        if site_index_col in f_table
        else None,
        "stratum_matched_null": int(f_table[stratum_matched_col].isnull().sum())
        if stratum_matched_col in f_table
        else None,
        "si_level_null": int(f_table[si_level_col].isnull().sum())
        if si_level_col in f_table
        else None,
    }


def validate_nonempty_au_assignment(
    *,
    f_table: Any,
    au_col: str = "au",
    site_index_col: str = "SITE_INDEX",
    stratum_matched_col: str = "stratum_matched",
    si_level_col: str = "si_level",
) -> None:
    """Raise with null diagnostics when AU assignment produces no mapped rows."""
    if not f_table[au_col].isnull().all():
        return
    null_summary = build_au_assignment_null_summary(
        f_table=f_table,
        site_index_col=site_index_col,
        stratum_matched_col=stratum_matched_col,
        si_level_col=si_level_col,
    )
    raise ValueError(
        "AU assignment produced no rows; check SITE_INDEX/stratum matching and "
        f"si_level assignment. Summary: {null_summary}"
    )


def assign_thlb_area_and_flag(
    *,
    f_table: Any,
    species_spruce: Sequence[str],
    species_pine: Sequence[str],
    species_aspen: Sequence[str],
    species_fir: Sequence[str],
    tsa_col: str = "tsa_code",
    thlb_raw_col: str = "thlb_raw",
    area_col: str = "FEATURE_AREA_SQM",
    species_col: str = "SPECIES_CD_1",
    site_index_col: str = "SITE_INDEX",
    thlb_area_col: str = "thlb_area",
    thlb_col: str = "thlb",
) -> Any:
    """Assign THLB area and THLB binary flag using legacy TSA-specific rules."""
    table = f_table.copy()
    spruce = set(species_spruce)
    pine = set(species_pine)
    aspen = set(species_aspen)
    fir = set(species_fir)
    excluded_tsa08_species = {"SB", "E", "EA", "EB", "LT"}

    thlb_area_values: list[float] = []
    thlb_values: list[int] = []
    for row in table.itertuples(index=False):
        tsa_code = getattr(row, tsa_col)
        thlb_raw = getattr(row, thlb_raw_col)
        species = getattr(row, species_col)
        site_index = getattr(row, site_index_col)
        feature_area = getattr(row, area_col)

        thlb_area = float(thlb_raw) * float(feature_area) * 0.000001
        if str(tsa_code) == "08":
            if thlb_raw < 90:
                thlb_area = 0.0
            elif species in spruce and site_index < 10:
                thlb_area = 0.0
            elif species in pine and site_index < 15:
                thlb_area = 0.0
            elif species in aspen and site_index < 15:
                thlb_area = 0.0
            elif species in fir and site_index < 10:
                thlb_area = 0.0
            elif species in excluded_tsa08_species:
                thlb_area = 0.0

        thlb_thresh = 50
        if str(tsa_code) == "08":
            thlb_thresh = 93
        elif str(tsa_code) == "24":
            thlb_thresh = 69
        thlb_flag = 1 if thlb_raw > thlb_thresh else 0

        thlb_area_values.append(thlb_area)
        thlb_values.append(thlb_flag)

    table[thlb_area_col] = thlb_area_values
    table[thlb_col] = thlb_values
    return table


def mean_thlb_for_geometry(
    *,
    geometry: Any,
    raster_src: Any,
    mask_fn: Callable[..., Any],
    np_module: Any,
    default_on_error: float = 0.0,
) -> float:
    """Compute mean THLB raster value for one geometry with legacy error fallback."""
    try:
        array, _ = mask_fn(raster_src, [geometry], crop=True)
    except Exception:
        return float(default_on_error)
    return float(np_module.mean(array[array >= 0]))


def assign_thlb_raw_from_raster(
    *,
    f_table: Any,
    thlb_raster_path: str | Path,
    rio_module: Any,
    mask_fn: Callable[..., Any],
    np_module: Any,
    row_apply_fn: Callable[..., Any],
    geometry_col: str = "geometry",
    out_col: str = "thlb_raw",
    default_on_error: float = 0.0,
) -> Any:
    """Assign per-row raw THLB values by masking a THLB raster."""
    table = f_table.copy()
    with rio_module.open(thlb_raster_path) as src:

        def _mean(row: Any) -> float:
            try:
                geometry = row[geometry_col]
            except Exception:
                geometry = getattr(row, geometry_col)
            return mean_thlb_for_geometry(
                geometry=geometry,
                raster_src=src,
                mask_fn=mask_fn,
                np_module=np_module,
                default_on_error=default_on_error,
            )

        table[out_col] = row_apply_fn(table, _mean, axis=1)
    return table
