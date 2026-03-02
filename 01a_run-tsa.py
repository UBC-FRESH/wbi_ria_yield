# Auto-generated from 01a_run-tsa.ipynb


def run_tsa(
    *,
    tsa,
    stratum_col,
    f,
    si_levels,
    resume_effective,
    force_run_vdyp,
    kwarg_overrides_for_tsa,
    results,
    vdyp_results,
    vdyp_curves_smooth,
    scsi_au,
    au_scsi,
    tipsy_params,
    si_levelquants,
    species_list,
    vdyp_results_tsa_pickle_path_prefix,
    vdyp_results_pickle_path,
    vdyp_input_pandl_path,
    vdyp_ply_feather_path,
    vdyp_lyr_feather_path,
    vdyp_curves_smooth_tsa_feather_path_prefix,
    tipsy_params_columns,
    tipsy_params_path_prefix,
    vdyp_out_cache=None,
    curve_fit_impl=None,
):
    import operator
    import os

    import distance
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns

    from femic.pipeline.pre_vdyp import (
        load_vdyp_prep_checkpoint,
        save_vdyp_prep_checkpoint,
    )
    from femic.pipeline.vdyp_logging import (
        append_jsonl,
        append_text,
        build_tsa_vdyp_log_paths,
        resolve_run_id,
    )
    from femic.pipeline.vdyp_sampling import nsamples_from_curves
    from femic.pipeline.vdyp_io import import_vdyp_tables, write_vdyp_infiles_plylyr
    from femic.pipeline.vdyp_curves import process_vdyp_out
    from femic.pipeline.vdyp_stage import (
        build_curve_fit_adapter,
        build_smoothed_curve_table,
        execute_bootstrap_vdyp_runs,
        execute_curve_smoothing_runs,
        execute_vdyp_batch,
        load_vdyp_input_tables,
        load_or_build_vdyp_results_tsa,
        plot_curve_overlays,
    )
    from femic.pipeline.vdyp_overrides import vdyp_kwarg_overrides_for_tsa
    from femic.pipeline.tipsy import (
        build_tipsy_params_for_tsa,
        build_tipsy_input_table,
        write_tipsy_input_exports,
    )
    from femic.pipeline.tipsy_legacy import (
        build_tipsy_exclusion,
        get_legacy_tipsy_builders,
    )
    from femic.pipeline.tipsy_config import (
        resolve_tipsy_param_builder,
    )

    curve_fit = build_curve_fit_adapter(curve_fit_impl=curve_fit_impl, np_module=np)
    if kwarg_overrides_for_tsa is None:
        kwarg_overrides_for_tsa = vdyp_kwarg_overrides_for_tsa(tsa)

    # --- cell 1 ---
    print("processing tsa", tsa)

    # --- cell 2 ---
    f_ = f.loc[tsa].reset_index().set_index(stratum_col)

    # --- cell 4 ---
    target_nstrata = {"08": 9, "16": 13, "24": 8, "40": 7, "41": 10}

    # --- cell 5 ---
    totalarea = f_.FEATURE_AREA_SQM.sum()
    f_["totalarea_p"] = f_.FEATURE_AREA_SQM / totalarea

    # --- cell 7 ---
    min_standcount = 1000

    # --- cell 8 ---
    strata_gb1 = f_.groupby(level=stratum_col)
    totalarea_p_sum = strata_gb1.totalarea_p.sum().nlargest(target_nstrata[tsa])
    largestn_strata_codes = list(totalarea_p_sum.index.values)
    strata_gb2 = f_.groupby(level=stratum_col)
    site_index_std = strata_gb2.SITE_INDEX.std()
    site_index_iqr = strata_gb2.SITE_INDEX.quantile(
        0.75
    ) - strata_gb2.SITE_INDEX.quantile(0.25)
    site_index_median = strata_gb2.SITE_INDEX.median()
    stand_count = strata_gb2.FEATURE_ID.count()
    coverage = strata_gb2.totalarea_p.sum()
    crown_closure = strata_gb2.CROWN_CLOSURE.median()
    strata_df = pd.DataFrame(totalarea_p_sum)
    strata_df["site_index_std"] = site_index_std
    strata_df["site_index_iqr"] = site_index_iqr
    strata_df["site_index_median"] = site_index_median
    strata_df["stand_count"] = stand_count
    strata_df["coverage"] = coverage
    strata_df["crown_closure"] = crown_closure
    strata_df = strata_df[strata_df.stand_count >= min_standcount]
    strata_df = strata_df.head(target_nstrata[tsa])
    print("mean stratum SI IQR", site_index_iqr.mean())
    print("coverage", strata_df.coverage.sum())
    print("count", strata_df.shape[0])

    # --- cell 10 ---
    ax = strata_df.site_index_median.hist(bins=np.arange(25, step=1))
    ax.set_xlim([0, 25])

    # --- cell 12 ---
    strata_df["median_si"] = (
        f_[f_.index.isin(largestn_strata_codes)]
        .groupby(level=stratum_col)
        .SITE_INDEX.median()
    )
    plt.scatter(strata_df.totalarea_p, strata_df.median_si)

    # --- cell 14 ---
    figsize = (8, 12)
    alpha = 0.2
    linewidth = 1.0
    inner = "box"
    showfliers = False
    width = 0.8
    bw = "scott"
    cut = 0

    sort_lex = 0
    if sort_lex:
        stratum_props = list(strata_df.sort_index().totalarea_p.values)
        labels = sorted(strata_df.sort_index().index.values)
    else:  # sort by abundance
        stratum_props = list(strata_df.totalarea_p.values)
        labels = strata_df.index.values

    fig, ax = plt.subplots(figsize=figsize)
    ax2 = ax.twiny()
    sns.barplot(
        y=labels,
        x=stratum_props,
        ax=ax,
        alpha=alpha,
        label="Relative abundance of stratum (proportion of total area)",
    )
    sns.violinplot(
        y=stratum_col,
        x="SITE_INDEX",
        data=f_.reset_index(),
        ax=ax2,
        bw=bw,
        order=labels,
        linewidth=linewidth,
        inner=inner,
        width=width,
        cut=cut,
    )
    # sns.violinplot(y=stratum_col, x='siteprod', data=f_.reset_index(), ax=ax2, bw=bw, order=labels, linewidth=linewidth, inner=inner, width=width, cut=cut)
    ax.set_xlabel("Relative abundance of stratum (proportion of total area)")
    ax2.set_xlim([0, 30])
    plt.savefig("plots/strata-tsa%s.pdf" % tsa, bbox_inches="tight")
    plt.savefig("plots/strata-tsa%s.png" % tsa, facecolor="white", bbox_inches="tight")

    # --- cell 16 ---
    names1 = set(f_.loc[strata_df.index.values].stratum_lexmatch.dropna().unique())
    names2 = set(f_.stratum_lexmatch.dropna().unique()) - names1

    stratum_key = (
        f_.reset_index().groupby("%s_lexmatch" % stratum_col)[stratum_col].first()
    )
    totalarea_p_sum__ = f_.groupby("%s_lexmatch" % stratum_col).totalarea_p.sum()
    lev_dist = {
        n2: {n1: distance.levenshtein(n1, n2) for n1 in names1} for n2 in names2
    }
    lev_dist_low = {
        n2: {
            n1: (lev_dist[n2][n1], totalarea_p_sum__.loc[n1])
            for n1 in lev_dist[n2].keys()
            if lev_dist[n2][n1] == min(lev_dist[n2].values())
        }
        for n2 in names2
    }
    best_match = {
        stratum_key.loc[n2]: stratum_key[
            max(lev_dist_low[n2].items(), key=operator.itemgetter(1))[0]
        ]
        for n2 in names2
    }

    # --- cell 17 ---
    f_.reset_index(inplace=True)

    # --- cell 18 ---
    def match_stratum(r):
        key = r[stratum_col]
        if key in strata_df.index.values:
            return key
        return best_match.get(key, key)

    f_["%s_matched" % stratum_col] = f_.apply(match_stratum, axis=1)

    # --- cell 19 ---
    stratum_col = "%s_matched" % stratum_col

    # --- cell 20 ---
    f__ = f_.set_index(stratum_col)

    # --- cell 22 ---
    def fit_func1(x, a, b, c, s):
        return s * (a * ((x - c) ** b)) * np.exp(-a * (x - c))

    def fit_func1_bounds_func(x):
        return ([0.000, 0, 0, 0], [1.00, 50, max(1, min(np.min(x), 100)), 10])

    body_fit_func = fit_func1
    body_fit_func_bounds_func = fit_func1_bounds_func
    toe_fit_func = fit_func1
    toe_fit_func_bounds_func = fit_func1_bounds_func

    # --- cell 24 ---
    stratum_si_stats = f__.groupby(stratum_col).SITE_INDEX.describe(
        percentiles=[0, 0.05, 0.20, 0.35, 0.5, 0.65, 0.80, 0.95, 1]
    )

    # --- cell 26 ---
    def fit_stratum(
        f_,
        fit_func,
        fit_func_bounds_func,
        strata_df,
        stratum_si_stats,
        stratumi,
        plot=True,
        figsize=(6, 12),
        verbose=False,
        xlim=(0, 300),
        ylim=(0, 500),
        si_levelquants={"L": [5, 20, 35], "M": [35, 50, 65], "H": [65, 80, 95]},
        linestyles=["-", "--", ":"],
        markers=["x", "+", "*"],
        palette_flavours=["RdPu", "Blues", "Greens"],
        maxfev=100000,
        min_age=30,
        max_age=300,
        max_records=15000,
        sigma_exponent=1.0,
        window=10,
        min_periods=None,
        center=False,
        agg_type="median",
        sv_thresh=0.10,
        rawdata_alpha=0.05,
        fitattr_thresh=1.0,
        fit_rawdata=True,
        debug=False,
    ):
        palettes = [sns.color_palette(pf, 3) for pf in palette_flavours]
        pd.options.mode.chained_assignment = None  # default='warn'
        sc = strata_df.iloc[stratumi].name
        if verbose:
            print("processing stratum", sc)
        si_popt = {}
        if plot:
            fig, ax = plt.subplots(4, 1, figsize=figsize, sharex=True, sharey=True)
            palette = sns.color_palette("RdPu", 3)
            sns.set_palette(palette)
            ax_ = {}
            ax_["L"], ax_["M"], ax_["H"] = ax[1], ax[2], ax[3]
            palette_ = {v: palette[i] for i, v in enumerate("LMH")}
        result = {}
        for i, (si_level, Q) in enumerate(si_levelquants.items()):
            result[si_level] = {}
            # Keep `ss` as a DataFrame even when only one record matches `sc`.
            # With scalar `.loc[sc]`, pandas can return a Series, which then breaks
            # downstream boolean row filtering.
            ss = f_.loc[[sc]].copy()
            si_lo = stratum_si_stats.loc[sc].loc["%i%%" % Q[0]]
            si_md = stratum_si_stats.loc[sc].loc["%i%%" % Q[1]]
            si_hi = stratum_si_stats.loc[sc].loc["%i%%" % Q[2]]
            ss = ss[
                (ss.SITE_INDEX >= si_lo)
                & (ss.SITE_INDEX < si_hi)
                & (ss.PROJ_AGE_1 >= min_age)
                & (ss.PROJ_AGE_1 < max_age)
            ]
            #####################################################################################################################
            # Originally, we were using the siteprod data to define SI quantiles and for input to TIPSY (because ???).
            # Turns out that does not not work so well, but using VRI SI data for both VDYP and TIPSY seems to yield OK results.
            # Needs further investigation to better understand why anyone is claiming the siteprod data is "better".
            #
            # ss = ss[(ss.siteprod >= si_lo) & (ss.siteprod < si_hi) & (ss.PROJ_AGE_1 >= min_age) & (ss.PROJ_AGE_1 < max_age)]
            #####################################################################################################################
            ss = ss.sort_values("PROJ_AGE_1")
            stand_volume_total = ss["LIVE_STAND_VOLUME_125"].sum()
            if stand_volume_total <= 0:
                sv = pd.Series(dtype=float)
            else:
                sv = pd.Series(
                    {
                        species: (
                            ss["live_vol_per_ha_125_%s" % species].sum()
                            / stand_volume_total
                        )
                        for species in species_list
                    }
                ).sort_values(ascending=False)
                sv = sv[sv > sv_thresh]
            # print(type(ss))
            # assert type(ss) == pd.DataFrame
            result[si_level]["ss"] = ss
            if verbose:
                print("sv sum", sv.sum())
            if plot:
                x, y = [], []
                for j, species in enumerate(sv.index.values):
                    fitattr = "live_vol_per_ha_125_%s" % species
                    sss = ss[ss[fitattr] >= 1]
                    x.append(sss.PROJ_AGE_1.values)
                    y.append(sss[fitattr].values / sv.sum())
                x = np.concatenate(x)
                y = np.concatenate(y)
                ax_[si_level].scatter(
                    x,
                    y,
                    alpha=rawdata_alpha,
                    label="Raw data (%s SI, %s)" % (si_level, species),
                    color="grey",
                    marker=markers[j],
                )
            result[si_level]["species"] = {}
            for j, species in enumerate(sv.index.values):
                if verbose:
                    print(
                        "  fitting SI level %s (%2.1f), species %s"
                        % (si_level, si_md, species)
                    )
                fitattr = "live_vol_per_ha_125_%s" % species
                sss = ss[ss[fitattr] >= fitattr_thresh]
                if fit_rawdata:
                    x = sss.PROJ_AGE_1.values
                    y = sss[fitattr].values / sv.sum()
                    sigma = None
                    agg = None
                else:  # fit smoothed data
                    agg = sss.groupby("PROJ_AGE_1")[fitattr].agg(
                        ["mean", "median", "std", "count"]
                    )
                    agg = agg[agg["count"] > 2]
                    agg["sigma"] = (
                        (agg["std"].mean() + agg["std"]) / agg["count"]
                    ) ** 0.5
                    x = agg.index.values
                    y = agg[agg_type].values / sv.sum()
                    sigma = agg["sigma"].values
                # fit_func_bounds = ([0.000, 0, 0, 0],
                #                   [0.100, 3, min(np.min(x), 100), 1000])
                bounds = fit_func_bounds_func(x)
                try:
                    popt, pcov = curve_fit(
                        fit_func, x, y, bounds=bounds, maxfev=maxfev, sigma=sigma
                    )
                except Exception as exc:
                    print(
                        "fit error",
                        exc,
                        "stratum",
                        sc,
                        "si",
                        si_level,
                        "species",
                        species,
                        "n",
                        len(x),
                    )
                    continue

                if verbose:
                    print("fitting N raw data points", sss.shape[0])
                    print("popt", popt)
                if plot:
                    if not fit_rawdata:
                        ax_[si_level].scatter(
                            x,
                            y,
                            alpha=0.8,
                            label="Smoothed data (%s SI, %s)" % (si_level, species),
                            color="black",
                            marker=markers[j],
                        )
                    x_ = np.linspace(popt[2], 300, 30)
                    y_ = fit_func(x_, *popt)
                    sns.lineplot(
                        x_,
                        y_,
                        label="func fit (%s SI, %s)" % (si_level, species),
                        ax=ax[0],
                        color=palette_[si_level],
                        linestyle=linestyles[j],
                        linewidth=3,
                    )
                    sns.lineplot(
                        x_,
                        y_,
                        label="func fit (%s SI, %s)" % (si_level, species),
                        ax=ax_[si_level],
                        color=palette_[si_level],
                        linestyle=linestyles[j],
                        linewidth=3,
                    )
                result[si_level]["species"][species] = {}
                result[si_level]["species"][species]["si"] = si_md
                result[si_level]["species"][species]["pct"] = int(
                    round(100 * sv[species] / sv.sum())
                )
                age = int(round(np.min(x) * 1.0))
                # age = 100
                result[si_level]["species"][species]["age"] = (
                    age if not np.isnan(age) else None
                )
                jj = min(2, j + 1)
                ssss = sss[
                    (sss["PROJ_AGE_%i" % jj] >= age - 5)
                    & (sss["PROJ_AGE_%i" % jj] < age + 5)
                ]
                height = ssss["PROJ_HEIGHT_%i" % jj].median()
                result[si_level]["species"][species]["height"] = (
                    height if not np.isnan(height) else None
                )
                result[si_level]["species"][species]["fit_func"] = fit_func
                result[si_level]["species"][species]["popt"] = popt
                result[si_level]["species"][species]["pcov"] = pcov
        if plot:
            ax[0].set_title("Best-fit yield curves (stratum %s)" % sc)
            plt.legend(loc="best")
            plt.xlim(xlim)
            plt.ylim(ylim)
            plt.xlabel("Stand age (years)")
            plt.ylabel("Merch. volume (m3/ha)")
            plt.tight_layout()
            plt.savefig(
                "plots/yieldcurve_fit-%s-%s.png" % (str(stratumi).zfill(2), sc),
                facecolor="white",
            )
            plt.savefig(
                "plots/yieldcurve_fit-%s-%s.pdf" % (str(stratumi).zfill(2), sc),
                facecolor="white",
            )
        return result

    # --- cell 28 ---
    N = 30
    figsize = (8, 16)

    debug = 0
    fit_rawdata = 1
    min_age = 30
    agg_type = "median"
    verbose = False
    plot = False

    vdyp_prep_checkpoint_path = "./data/vdyp_prep-tsa%s.pkl" % tsa
    prep_loaded = False
    if resume_effective and os.path.isfile(vdyp_prep_checkpoint_path):
        try:
            results[tsa] = load_vdyp_prep_checkpoint(vdyp_prep_checkpoint_path)
            prep_loaded = True
            print("resume: loaded pre-VDYP checkpoint (%s strata)" % len(results[tsa]))
        except Exception as exc:
            print(
                "resume: failed to load pre-VDYP checkpoint %s: %s"
                % (vdyp_prep_checkpoint_path, exc)
            )

    if not prep_loaded:
        results[tsa] = []
        for stratumi, sc in enumerate(strata_df.index.values[:]):
            print("compiling stratum %s" % sc)
            fit_out = fit_stratum(
                f__,
                body_fit_func,
                body_fit_func_bounds_func,
                strata_df,
                stratum_si_stats,
                stratumi,
                fit_rawdata=fit_rawdata,
                min_age=min_age,
                agg_type=agg_type,
                plot=plot,
                figsize=figsize,
                verbose=verbose,
                ylim=[0, 600],
                xlim=[0, 400],
            )
            results[tsa].append([stratumi, sc, fit_out])
        saved_count = save_vdyp_prep_checkpoint(vdyp_prep_checkpoint_path, results[tsa])
        print(
            "saved pre-VDYP checkpoint with %s strata to %s"
            % (saved_count, vdyp_prep_checkpoint_path)
        )

    # --- cell 30/32 ---

    from datetime import datetime, timezone
    from pathlib import Path
    import time
    import traceback

    femic_run_id = resolve_run_id()

    def _tsa_log_path(kind, vdyp_io_dirname="vdyp_io"):
        return build_tsa_vdyp_log_paths(
            tsa_code=tsa,
            run_id=femic_run_id,
            vdyp_io_dirname=vdyp_io_dirname,
        )[kind]

    # --- cell 36 ---
    def run_vdyp(
        s,
        vdyp_ply,
        vdyp_lyr,
        vdyp_io_dirname="vdyp_io",
        vdyp_outfile="ConsoleOutput.txt",
        vdyp_params_infile="vdyp_params-landp",
        nsamples="auto",
        vdyp_binpath="VDYP7/VDYP7/VDYP7Console.exe",
        si_levels=["L", "M", "H"],
        nsamples_c1=0.01,
        nsamples_c2=0.1,
        verbose=False,
        confidence=95,
        half_rel_ci=0.05,
        min_samples=100,
        max_samples=640,
        ipp_mode=None,
        delete=True,
        vdyp_timeout=2.0,
        vdyp_out_cache=None,
        vdyp_log_path=None,
        vdyp_stdout_log_path=None,
        vdyp_stderr_log_path=None,
        log_context=None,
    ):
        import shutil
        from pathlib import Path

        global xxx
        if shutil.which("wine") is None:
            raise RuntimeError(
                "wine not found; VDYP7 requires wine to run on non-Windows systems"
            )
        vdyp_binpath_path = Path(vdyp_binpath)
        if not vdyp_binpath_path.exists():
            raise RuntimeError(
                f"VDYP executable not found: {vdyp_binpath_path.resolve()}"
            )
        vdyp_params_path = Path(vdyp_params_infile)
        if not vdyp_params_path.exists():
            raise RuntimeError(
                f"VDYP params path not found: {vdyp_params_path.resolve()}"
            )
        Path(vdyp_io_dirname).mkdir(parents=True, exist_ok=True)
        if vdyp_log_path is None:
            vdyp_log_path = _tsa_log_path("run", vdyp_io_dirname)
        if vdyp_stdout_log_path is None:
            vdyp_stdout_log_path = _tsa_log_path("stdout", vdyp_io_dirname)
        if vdyp_stderr_log_path is None:
            vdyp_stderr_log_path = _tsa_log_path("stderr", vdyp_io_dirname)
        base_context = dict(log_context) if log_context else {}
        base_context.setdefault("tsa", tsa)
        base_context.setdefault("run_id", femic_run_id)
        base_context.setdefault("vdyp_stdout_log", str(vdyp_stdout_log_path))
        base_context.setdefault("vdyp_stderr_log", str(vdyp_stderr_log_path))
        base_context.setdefault("vdyp_binpath", str(vdyp_binpath_path))
        base_context.setdefault("vdyp_params", str(vdyp_params_path))
        vdyp_output_path = "%s/%s" % (vdyp_io_dirname, vdyp_outfile)

        def _run_vdyp(
            feature_ids,
            vdyp_io_dirname="vdyp_io",
            timeout=None,
            cache_hits=0,
            phase=None,
        ):
            feature_ids = list(feature_ids)
            feature_count = len(feature_ids)
            if feature_count == 0:
                append_jsonl(
                    vdyp_log_path,
                    {
                        "event": "vdyp_run",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "status": "cache_only",
                        "phase": phase,
                        "feature_count": 0,
                        "cache_hits": int(cache_hits),
                        "context": base_context,
                    },
                )
                return {}
            append_jsonl(
                vdyp_log_path,
                {
                    "event": "vdyp_run",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "start",
                    "phase": phase,
                    "feature_count": int(feature_count),
                    "cache_hits": int(cache_hits),
                    "context": base_context,
                },
            )
            return execute_vdyp_batch(
                feature_ids=feature_ids,
                vdyp_ply=vdyp_ply,
                vdyp_lyr=vdyp_lyr,
                vdyp_binpath=vdyp_binpath,
                vdyp_params_infile=vdyp_params_infile,
                vdyp_io_dirname=vdyp_io_dirname,
                vdyp_log_path=vdyp_log_path,
                vdyp_stdout_log_path=vdyp_stdout_log_path,
                vdyp_stderr_log_path=vdyp_stderr_log_path,
                phase=phase or "unknown",
                cache_hits=cache_hits,
                timeout=timeout,
                run_id=femic_run_id,
                base_context=base_context,
                write_vdyp_infiles=write_vdyp_infiles_plylyr,
                import_vdyp_tables_fn=import_vdyp_tables,
                append_jsonl_fn=append_jsonl,
                append_text_fn=append_text,
            )

        if nsamples == "auto" and s.shape[0] < min_samples:
            if s.shape[0] == 0:
                return {}
            if verbose:
                print(
                    "auto mode: stratum has fewer than min_samples; "
                    f"running all {s.shape[0]} records"
                )
            vdyp_out = _run_vdyp(s.FEATURE_ID.values, phase="auto_small_sample")
            if vdyp_out_cache is not None:
                vdyp_out_cache.update(vdyp_out)
        elif (
            nsamples == "auto" and s.shape[0] >= min_samples
        ):  # automatically determine sample size
            ss = s.reset_index().set_index("index")
            samples = ss.sample(min(min_samples, ss.shape[0]))
            feature_ids = samples.FEATURE_ID.values
            vdyp_out = {}
            cache_hits = 0
            if vdyp_out_cache is not None:
                feature_ids_ = []
                for fid in feature_ids:
                    if fid in vdyp_out_cache:
                        vdyp_out[fid] = vdyp_out_cache[fid]
                    else:
                        feature_ids_.append(fid)
                cache_hits = len(feature_ids) - len(feature_ids_)
                feature_ids = feature_ids_
            vdyp_out = _run_vdyp(feature_ids, cache_hits=cache_hits, phase="initial")
            if vdyp_out_cache is not None:
                vdyp_out_cache.update(vdyp_out)
            ss.drop(samples.index, inplace=True)
            nsamples_target, _ = nsamples_from_curves(
                vdyp_out,
                curve_fit_fn=curve_fit,
                fit_func=body_fit_func,
                fit_func_bounds_func=body_fit_func_bounds_func,
                confidence=confidence,
                half_rel_ci=half_rel_ci,
            )
            nsamples_target = min(max(nsamples_target, min_samples), ss.shape[0])
            nsamples_gap = nsamples_target - len(vdyp_out)
            nsamples_gap_rel = nsamples_gap / nsamples_target
            while nsamples_gap_rel > nsamples_c1 and ss.shape[0]:
                if nsamples_gap_rel > nsamples_c2:
                    nsamples_new = int(nsamples_gap * (1 - nsamples_gap_rel))
                else:
                    nsamples_new = nsamples_gap
                nsamples_new = min(nsamples_new, max_samples, ss.shape[0])
                if nsamples_new <= 0:
                    break
                if verbose:
                    print(
                        "moe loop",
                        nsamples_target,
                        nsamples_new,
                        "%0.2f" % nsamples_gap_rel,
                        len(vdyp_out),
                        ss.shape[0],
                    )
                samples = ss.sample(nsamples_new)
                feature_ids = samples.FEATURE_ID.values
                timeout = 30 + (vdyp_timeout * feature_ids.shape[0] / len(rc))
                if not ipp_mode or samples.shape[0] < min_samples:
                    cache_hits = 0
                    if vdyp_out_cache is not None:
                        feature_ids_ = []
                        for fid in feature_ids:
                            if fid in vdyp_out_cache:
                                vdyp_out[fid] = vdyp_out_cache[fid]
                            else:
                                feature_ids_.append(fid)
                        cache_hits = len(feature_ids) - len(feature_ids_)
                        feature_ids = feature_ids_
                    vdyp_out_ = _run_vdyp(
                        feature_ids,
                        timeout=timeout,
                        cache_hits=cache_hits,
                        phase="gap_fill",
                    )
                    vdyp_out.update(vdyp_out_)
                    if vdyp_out_cache is not None:
                        vdyp_out_cache.update(vdyp_out)
                elif ipp_mode == "load_balanced":
                    assert False  # not working... do not use this
                    print(" ipp start", feature_ids.shape[0])
                    amr = lv.map(
                        _run_vdyp, np.array_split(feature_ids, len(rc)), ordered=False
                    )
                    print(" ipp done")
                    try:
                        amr.wait(timeout=timeout)
                        for chunk in amr:
                            vdyp_out.update(chunk)
                    except:
                        for msg_id in amr.msg_ids:
                            try:
                                chunk_amr = rc.get_result(msg_id)
                                chunk = chunk_amr.get()
                                vdyp_out.update(chunk)
                            except:
                                print("failed chunk", msg_id)
                ss.drop(samples.index, inplace=True)
                nsamples_target, _ = nsamples_from_curves(
                    vdyp_out,
                    curve_fit_fn=curve_fit,
                    fit_func=body_fit_func,
                    fit_func_bounds_func=body_fit_func_bounds_func,
                    confidence=confidence,
                    half_rel_ci=half_rel_ci,
                )
                nsamples_target = min(max(nsamples_target, min_samples), s.shape[0])
                nsamples_gap = nsamples_target - len(vdyp_out)
                nsamples_gap_rel = nsamples_gap / nsamples_target
            if verbose:
                print("final gap", nsamples_gap_rel)
        elif nsamples == "all":
            vdyp_out = _run_vdyp(s.FEATURE_ID.values, phase="all")
        elif isinstance(nsamples, int):
            samples = s.sample(nsamples)
            feature_ids = samples.FEATURE_ID.values
            vdyp_out = _run_vdyp(feature_ids, phase="fixed")
        else:
            assert False  # bad nsamples value
        return vdyp_out

    vdyp_run_events_path = _tsa_log_path("run", "vdyp_io")
    vdyp_curve_events_path = _tsa_log_path("curve", "vdyp_io")

    # --- cell 38 ---
    # --- cell 40 ---
    vdyp_ply, vdyp_lyr = load_vdyp_input_tables(
        vdyp_input_pandl_path=vdyp_input_pandl_path,
        vdyp_ply_feather_path=vdyp_ply_feather_path,
        vdyp_lyr_feather_path=vdyp_lyr_feather_path,
        read_from_source=False,
    )

    # --- cell 42 ---
    vdyp_results_tsa_pickle_path = "%s%s.pkl" % (
        vdyp_results_tsa_pickle_path_prefix,
        tsa,
    )
    si_levels = ["L", "M", "H"]
    half_rel_ci = 0.01  # use 0.01 for production
    si_levels_ = si_levels
    ipp_mode = None
    nsamples_c1 = 0.05
    vdyp_results[tsa] = load_or_build_vdyp_results_tsa(
        tsa=tsa,
        force_run_vdyp=bool(force_run_vdyp),
        vdyp_results_tsa_pickle_path=vdyp_results_tsa_pickle_path,
        vdyp_results_pickle_path=vdyp_results_pickle_path,
        run_bootstrap_fn=lambda: execute_bootstrap_vdyp_runs(
            tsa=tsa,
            run_id=femic_run_id,
            results_for_tsa=results[tsa][:],
            si_levels=si_levels_,
            vdyp_run_events_path=vdyp_run_events_path,
            append_jsonl_fn=append_jsonl,
            run_vdyp_fn=lambda s, **kwargs: run_vdyp(s, vdyp_ply, vdyp_lyr, **kwargs),
            vdyp_out_cache=vdyp_out_cache,
            verbose=True,
            half_rel_ci=half_rel_ci,
            ipp_mode=ipp_mode,
            nsamples_c1=nsamples_c1,
        ),
        print_fn=print,
    )

    # --- cell 44 ---
    # def toe_fit_func(x, a, b, c):
    #    return a*pow(x, b)

    def fit_func2(x, a, b):
        return a * pow(x, b) * pow(x, -a)

    def fit_func2_bounds_func(x):
        return (0, 0), (10, 10)

    # --- cell 45 ---
    vdyp_curves_smooth_tsa_feather_path = "%s%s.feather" % (
        vdyp_curves_smooth_tsa_feather_path_prefix,
        tsa,
    )
    if not os.path.isfile(vdyp_curves_smooth_tsa_feather_path):
        figsize = (8, 6)
        plot = 1
        palette_flavours = ["RdPu", "Blues", "Greens", "Greys"]
        palette = sns.color_palette("Greens", 3)
        sns.set_palette(palette)
        alphas = [1.0, 0.5, 0.1]
        smoothed_runs = execute_curve_smoothing_runs(
            tsa=tsa,
            run_id=femic_run_id,
            results_for_tsa=results[tsa],
            si_levels=si_levels,
            vdyp_results_for_tsa=vdyp_results.get(tsa, {}),
            kwarg_overrides_for_tsa=kwarg_overrides_for_tsa,
            process_vdyp_out_fn=process_vdyp_out,
            append_jsonl_fn=append_jsonl,
            vdyp_curve_events_path=vdyp_curve_events_path,
            curve_fit_fn=curve_fit,
            body_fit_func=body_fit_func,
            body_fit_func_bounds_func=body_fit_func_bounds_func,
            toe_fit_func=toe_fit_func,
            toe_fit_func_bounds_func=toe_fit_func_bounds_func,
            message_fn=print,
        )
        plot_curve_overlays(
            results_for_tsa=results[tsa],
            si_levels=si_levels,
            smoothed_runs=smoothed_runs,
            plot=bool(plot),
            figsize=figsize,
            palette=palette,
            pd_module=pd,
            plt_module=plt,
            dataframe_type=pd.core.frame.DataFrame,
            xlim=(0, 300),
            ylim=(0, 600),
            message_fn=print,
        )
        vdyp_curves_smooth[tsa] = build_smoothed_curve_table(
            smoothed_runs=smoothed_runs,
            pd_module=pd,
            output_path=vdyp_curves_smooth_tsa_feather_path,
        )
    else:
        vdyp_curves_smooth[tsa] = pd.read_feather(vdyp_curves_smooth_tsa_feather_path)

    tipsy_exclusion = build_tipsy_exclusion()
    legacy_tipsy_builders = get_legacy_tipsy_builders()
    tipsy_config_dir = os.environ.get("FEMIC_TIPSY_CONFIG_DIR", "config/tipsy")
    tipsy_use_legacy = os.environ.get("FEMIC_TIPSY_USE_LEGACY", "0") == "1"
    tipsy_param_builder, tipsy_param_builder_message = resolve_tipsy_param_builder(
        tsa_code=tsa,
        legacy_builder=legacy_tipsy_builders[tsa],
        config_dir=tipsy_config_dir,
        use_legacy=tipsy_use_legacy,
    )
    print(tipsy_param_builder_message)

    # --- cell 55 ---
    min_operable_years = 50
    verbose = 1
    si_iqrlo_quantile = 0.50
    (
        scsi_au[tsa],
        au_scsi[tsa],
        tipsy_params[tsa],
    ) = build_tipsy_params_for_tsa(
        tsa=tsa,
        results_for_tsa=results[tsa],
        si_levels=si_levels,
        vdyp_curves_smooth_tsa=vdyp_curves_smooth[tsa],
        vdyp_results_for_tsa=vdyp_results.get(tsa, {}),
        exclusion=tipsy_exclusion[tsa],
        tipsy_param_builder=tipsy_param_builder,
        vdyp_curve_events_path=vdyp_curve_events_path,
        append_jsonl_fn=append_jsonl,
        min_operable_years=min_operable_years,
        si_iqrlo_quantile=si_iqrlo_quantile,
        verbose=bool(verbose),
        message_fn=print,
    )

    # --- cell 57 ---
    try:
        df = build_tipsy_input_table(
            tipsy_params_for_tsa=tipsy_params[tsa],
            tipsy_params_columns=tipsy_params_columns,
            pd_module=pd,
        )
    except RuntimeError as exc:
        raise RuntimeError(
            f"No TIPSY parameter tables generated for TSA {tsa}; see "
            f"{vdyp_curve_events_path} for missing VDYP diagnostics."
        ) from exc
    write_tipsy_input_exports(
        tipsy_table=df,
        tsa=tsa,
        tipsy_params_path_prefix=tipsy_params_path_prefix,
    )


if __name__ == "__main__":
    raise SystemExit(
        "01a_run-tsa.py is intended to be launched by 00_data-prep.py or femic run."
    )
