# Auto-generated from 01a_run-tsa.ipynb


def run_tsa():
    global vdyp_out_cache, tsa, stratum_col, f, si_levels
    import copy
    if "vdyp_out_cache" not in globals():
        vdyp_out_cache = None
    _curve_fit_local = globals().get("_curve_fit")
    if _curve_fit_local is None:
        from scipy.optimize import curve_fit as _curve_fit_local
    import functools

    _wraps = globals().get("wraps", functools.wraps)

    @_wraps(_curve_fit_local)
    def curve_fit(*args, **kwargs):
        b = kwargs["bounds"] if "bounds" in kwargs else None
        if b and np.any(np.isfinite(b)) and "max_nfev" not in kwargs:
            kwargs["max_nfev"] = kwargs.pop("maxfev", None)
        return _curve_fit_local(*args, **kwargs)

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

    def _serialize_vdyp_prep_payload(results_tsa):
        payload = []
        for stratumi, sc, fit_out in results_tsa:
            fit_out_clean = copy.deepcopy(fit_out)
            for si_level_data in fit_out_clean.values():
                for species_data in si_level_data["species"].values():
                    species_data.pop("fit_func", None)
            payload.append([stratumi, sc, fit_out_clean])
        return payload

    vdyp_prep_checkpoint_path = "./data/vdyp_prep-tsa%s.pkl" % tsa
    prep_loaded = False
    if _femic_resume_effective and os.path.isfile(vdyp_prep_checkpoint_path):
        try:
            results[tsa] = pickle.load(open(vdyp_prep_checkpoint_path, "rb"))
            prep_loaded = True
            print(
                "resume: loaded pre-VDYP checkpoint (%s strata)"
                % len(results[tsa])
            )
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
        checkpoint_payload = _serialize_vdyp_prep_payload(results[tsa])
        pickle.dump(checkpoint_payload, open(vdyp_prep_checkpoint_path, "wb"))
        print(
            "saved pre-VDYP checkpoint with %s strata to %s"
            % (len(results[tsa]), vdyp_prep_checkpoint_path)
        )

    # --- cell 30 ---
    def write_vdyp_infiles_plylyr(
        feature_ids,
        vdyp_ply,
        vdyp_lyr,
        vdyp_io_dirname="vdyp_io",
        vdyp_ply_csv="vdyp_ply.csv",
        vdyp_lyr_csv="vdyp_lyr.csv",
    ):
        vdyp_ply_ = vdyp_ply[vdyp_ply.FEATURE_ID.isin(feature_ids)]
        vdyp_ply_.sort_values(by="FEATURE_ID", inplace=True)
        vdyp_ply_.to_csv(
            "%s/%s" % (vdyp_io_dirname, vdyp_ply_csv),
            columns=list(vdyp_ply.columns)[:-5],
            index=False,
            quoting=csv.QUOTE_NONNUMERIC,
        )
        vdyp_lyr_ = vdyp_lyr[vdyp_lyr.FEATURE_ID.isin(vdyp_ply_.FEATURE_ID)]
        vdyp_lyr_.sort_values(by="FEATURE_ID", inplace=True)
        vdyp_lyr_.to_csv(
            "%s/%s" % (vdyp_io_dirname, vdyp_lyr_csv),
            columns=list(vdyp_lyr.columns)[:-5],
            index=False,
            quoting=csv.QUOTE_NONNUMERIC,
        )

    # --- cell 32 ---
    def import_vdyp_tables(filename):
        import re, io

        chunks = re.findall(
            r"(?<=vvvvvvvvvv.).*?(?=\^)", open(filename).read(), re.DOTALL
        )
        result = {}
        for chunk in chunks:
            lines = chunk.split("\n")
            polygon_id = int(re.search(r"(?<=Polygon:.)\d+", lines[0]).group())
            result_ = pd.read_fwf(
                io.StringIO(chunk), skiprows=[0, 2], index_col="Age", infer_nrows=200
            )
            if type(result_) == pd.core.frame.DataFrame:
                result[polygon_id] = result_
        return result

    # --- cell 34 ---
    def nsamples_from_curves(
        vdyp_out,
        col="Vdwb",
        fit_func=body_fit_func,
        fit_func_bounds_func=body_fit_func_bounds_func,
        maxfev=10000,
        confidence=95,
        half_rel_ci=0.01,
        window=30,
        min_samples=10,
        max_samples=1000,
    ):
        if len(vdyp_out) < min_samples:
            return np.inf, None
        global xxx

        z = {95: 1.96}[confidence]
        frames = [
            v
            for v in vdyp_out.values()
            if isinstance(v, pd.core.frame.DataFrame) and not v.empty
        ]
        if not frames:
            print("warning: VDYP bootstrap returned no valid curve tables; retrying sample")
            return np.inf, None
        vdyp_out_concat = pd.concat(frames)
        c = vdyp_out_concat.groupby(level="Age")[col].median()
        c = c[c > 0]
        c = c[c.index >= 30]
        x = c.index.values
        y = c.rolling(window=window).median().values
        x, y = x[y > 0], y[y > 0]
        if len(x) == 0 or len(y) == 0:
            print("warning: VDYP bootstrap produced no positive age/volume points; retrying sample")
            return np.inf, None
        popt, pcov = curve_fit(
            fit_func, x, y, bounds=fit_func_bounds_func(x), maxfev=maxfev
        )
        y_ = fit_func(x, *popt)
        y_mai = pd.Series(y_ / x, x)
        y_mai_max_age = y_mai.idxmax()
        sigma = vdyp_out_concat.groupby(level="Age")[col].std().loc[y_mai_max_age]
        moe = c.loc[y_mai_max_age] * half_rel_ci * 2
        nsamples = (
            min(int((z * sigma / moe) ** 2) + 1, max_samples)
            if not np.isnan(sigma)
            else max_samples
        )
        return nsamples, (y_mai_max_age, c.loc[y_mai_max_age], moe, sigma)

    from datetime import datetime, timezone
    import json
    import os
    from pathlib import Path
    import time
    import traceback

    def _append_jsonl(path, payload):
        try:
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(payload, default=str) + "\n")
        except Exception as exc:
            print(f"warning: failed to write VDYP log to {path}: {exc}")

    def _append_text(path, text):
        try:
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as fh:
                fh.write(text)
        except Exception as exc:
            print(f"warning: failed to write VDYP text log to {path}: {exc}")

    def _vdyp_log_base(vdyp_io_dirname):
        log_dir_env = os.environ.get("FEMIC_LOG_DIR")
        if log_dir_env:
            return Path(log_dir_env)
        return Path(vdyp_io_dirname) / "logs"

    femic_run_id = os.environ.get("FEMIC_RUN_ID")
    if not femic_run_id:
        femic_run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    def _vdyp_run_log_path(vdyp_io_dirname="vdyp_io"):
        return _vdyp_log_base(vdyp_io_dirname) / f"vdyp_runs-tsa{tsa}-{femic_run_id}.jsonl"

    def _vdyp_curve_log_path(vdyp_io_dirname="vdyp_io"):
        return (
            _vdyp_log_base(vdyp_io_dirname)
            / f"vdyp_curve_events-tsa{tsa}-{femic_run_id}.jsonl"
        )

    def _vdyp_stdout_log_path(vdyp_io_dirname="vdyp_io"):
        return _vdyp_log_base(vdyp_io_dirname) / f"vdyp_stdout-tsa{tsa}-{femic_run_id}.log"

    def _vdyp_stderr_log_path(vdyp_io_dirname="vdyp_io"):
        return _vdyp_log_base(vdyp_io_dirname) / f"vdyp_stderr-tsa{tsa}-{femic_run_id}.log"

    def _prepend_quasi_origin_point(x, y, age=1, epsilon=1e-6):
        x = np.asarray(x)
        y = np.asarray(y)
        if x.size == 0:
            return np.array([age]), np.array([epsilon])
        if x[0] == age:
            y = y.copy()
            y[0] = epsilon
            return x, y
        return np.insert(x, 0, age), np.insert(y, 0, epsilon)

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
        import subprocess
        import shlex
        import shutil

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
            vdyp_log_path = _vdyp_run_log_path(vdyp_io_dirname)
        if vdyp_stdout_log_path is None:
            vdyp_stdout_log_path = _vdyp_stdout_log_path(vdyp_io_dirname)
        if vdyp_stderr_log_path is None:
            vdyp_stderr_log_path = _vdyp_stderr_log_path(vdyp_io_dirname)
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
            import tempfile

            run_started = time.time()
            feature_ids = list(feature_ids)
            feature_count = len(feature_ids)
            if feature_count == 0:
                _append_jsonl(
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
            vdyp_ply_csv_ = tempfile.NamedTemporaryFile(
                dir=vdyp_io_dirname, delete=delete
            )
            vdyp_lyr_csv_ = tempfile.NamedTemporaryFile(
                dir=vdyp_io_dirname, delete=delete
            )
            vdyp_out_txt_ = tempfile.NamedTemporaryFile(
                dir=vdyp_io_dirname, delete=delete
            )
            vdyp_err_txt_ = tempfile.NamedTemporaryFile(
                dir=vdyp_io_dirname, delete=delete
            )
            vdyp_ply_csv = vdyp_ply_csv_.name.split("/")[-1]
            vdyp_lyr_csv = vdyp_lyr_csv_.name.split("/")[-1]
            vdyp_out_txt = vdyp_out_txt_.name.split("/")[-1]
            vdyp_err_txt = vdyp_err_txt_.name.split("/")[-1]
            _append_jsonl(
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
            ply_rows = int(vdyp_ply.FEATURE_ID.isin(feature_ids).sum())
            lyr_rows = int(vdyp_lyr.FEATURE_ID.isin(feature_ids).sum())
            write_vdyp_infiles_plylyr(
                feature_ids,
                vdyp_ply,
                vdyp_lyr,
                vdyp_io_dirname,
                vdyp_ply_csv,
                vdyp_lyr_csv,
            )
            ply_path = Path(vdyp_io_dirname) / vdyp_ply_csv
            lyr_path = Path(vdyp_io_dirname) / vdyp_lyr_csv
            out_path = Path(vdyp_io_dirname) / vdyp_out_txt
            err_path = Path(vdyp_io_dirname) / vdyp_err_txt
            args = "wine %s -p %s -ip .\\\\%s\\\\%s -il .\\\\%s\\\\%s" % (
                vdyp_binpath,
                vdyp_params_infile,
                vdyp_io_dirname,
                vdyp_ply_csv,
                vdyp_io_dirname,
                vdyp_lyr_csv,
            )
            args += " -o .\\\\%s\\\\%s -e .\\\\%s\\\\%s" % (
                vdyp_io_dirname,
                vdyp_out_txt,
                vdyp_io_dirname,
                vdyp_err_txt,
            )
            try:
                result = subprocess.run(
                    shlex.split(args),
                    timeout=timeout,
                    capture_output=True,
                    text=True,
                )
            except subprocess.TimeoutExpired as exc:
                _append_jsonl(
                    vdyp_log_path,
                    {
                        "event": "vdyp_run",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "status": "timeout",
                        "phase": phase,
                        "feature_count": int(feature_count),
                        "cache_hits": int(cache_hits),
                        "ply_rows": int(ply_rows),
                        "lyr_rows": int(lyr_rows),
                        "cmd": args,
                        "timeout_sec": timeout,
                        "error": str(exc),
                        "context": base_context,
                    },
                )
                return {}
            except Exception as exc:
                _append_jsonl(
                    vdyp_log_path,
                    {
                        "event": "vdyp_run",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "status": "error",
                        "phase": phase,
                        "feature_count": int(feature_count),
                        "cache_hits": int(cache_hits),
                        "ply_rows": int(ply_rows),
                        "lyr_rows": int(lyr_rows),
                        "cmd": args,
                        "error": str(exc),
                        "traceback": traceback.format_exc(),
                        "context": base_context,
                    },
                )
                return {}
            stream_header = (
                f"\n=== {datetime.now(timezone.utc).isoformat()} "
                f"phase={phase} feature_count={feature_count} cache_hits={cache_hits} ===\n"
                f"cmd: {args}\n"
            )
            if result.stdout:
                _append_text(vdyp_stdout_log_path, stream_header + result.stdout + "\n")
            if result.stderr:
                _append_text(vdyp_stderr_log_path, stream_header + result.stderr + "\n")
            err_size = err_path.stat().st_size if err_path.exists() else 0
            err_head = ""
            if err_size:
                err_head = err_path.read_text(encoding="utf-8", errors="ignore")[:500]
            out_size = out_path.stat().st_size if out_path.exists() else 0
            proc_stdout_head = (result.stdout or "")[:500]
            proc_stderr_head = (result.stderr or "")[:500]
            try:
                vdyp_out = import_vdyp_tables(
                    "./%s/%s" % (vdyp_io_dirname, vdyp_out_txt)
                )
            except Exception as exc:
                _append_jsonl(
                    vdyp_log_path,
                    {
                        "event": "vdyp_run",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "status": "parse_error",
                        "phase": phase,
                        "feature_count": int(feature_count),
                        "cache_hits": int(cache_hits),
                        "ply_rows": int(ply_rows),
                        "lyr_rows": int(lyr_rows),
                        "cmd": args,
                        "returncode": getattr(result, "returncode", None),
                        "duration_sec": round(time.time() - run_started, 3),
                        "out_size": int(out_size),
                        "err_size": int(err_size),
                        "err_head": err_head,
                        "proc_stdout_head": proc_stdout_head,
                        "proc_stderr_head": proc_stderr_head,
                        "error": str(exc),
                        "traceback": traceback.format_exc(),
                        "context": base_context,
                    },
                )
                return {}
            vdyp_ply_csv_.close()
            vdyp_lyr_csv_.close()
            vdyp_out_txt_.close()
            vdyp_err_txt_.close()
            _append_jsonl(
                vdyp_log_path,
                {
                    "event": "vdyp_run",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "ok" if vdyp_out else "empty_output",
                    "phase": phase,
                    "feature_count": int(feature_count),
                    "cache_hits": int(cache_hits),
                    "ply_rows": int(ply_rows),
                    "lyr_rows": int(lyr_rows),
                    "cmd": args,
                    "returncode": getattr(result, "returncode", None),
                    "duration_sec": round(time.time() - run_started, 3),
                    "out_size": int(out_size),
                    "err_size": int(err_size),
                    "err_head": err_head,
                    "proc_stdout_head": proc_stdout_head,
                    "proc_stderr_head": proc_stderr_head,
                    "vdyp_out_tables": int(len(vdyp_out)),
                    "context": base_context,
                },
            )
            return vdyp_out

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
                vdyp_out, confidence=confidence, half_rel_ci=half_rel_ci
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
                    vdyp_out, confidence=confidence, half_rel_ci=half_rel_ci
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

    vdyp_run_events_path = _vdyp_run_log_path("vdyp_io")
    vdyp_curve_events_path = _vdyp_curve_log_path("vdyp_io")

    # --- cell 38 ---
    # if not os.path.isfile(vdyp_ply_feather_path):
    if 0:
        vdyp_ply = gpd.read_file(vdyp_input_pandl_path, driver="FileGDB", layer=0)
        vdyp_ply.to_feather(vdyp_ply_feather_path)
    else:
        vdyp_ply = gpd.read_feather(vdyp_ply_feather_path)

    # --- cell 40 ---
    # if not os.path.isfile(vdyp_lyr_feather_path):
    if 0:
        vdyp_lyr = gpd.read_file(vdyp_input_pandl_path, driver="FileGDB", layer=1)
        vdyp_lyr.to_feather(vdyp_lyr_feather_path)
    else:
        vdyp_lyr = gpd.read_feather(vdyp_lyr_feather_path)

    # --- cell 42 ---
    vdyp_results_tsa_pickle_path = "%s%s.pkl" % (
        vdyp_results_tsa_pickle_path_prefix,
        tsa,
    )
    if force_run_vdyp:
        print()
        vdyp_results[tsa] = {}
        si_levels = ["L", "M", "H"]
        half_rel_ci = 0.01  # use 0.01 for production
        si_levels_ = si_levels
        ipp_mode = None
        nsamples_c1 = 0.05
        for stratumi, sc, result in results[tsa][:]:
            vdyp_results[tsa][stratumi] = {}
            for si_level in si_levels_:
                print("running VDYP in bootstrap sample mode (%s, %s)" % (sc, si_level))
                run_context = {
                    "run_id": femic_run_id,
                    "tsa": tsa,
                    "stratum_index": int(stratumi),
                    "stratum_code": sc,
                    "si_level": si_level,
                }
                _append_jsonl(
                    vdyp_run_events_path,
                    {
                        "event": "vdyp_run",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "status": "dispatch",
                        "phase": "bootstrap",
                        "context": run_context,
                    },
                )
                try:
                    vdyp_out = run_vdyp(
                        result[si_level]["ss"],
                        vdyp_ply,
                        vdyp_lyr,
                        verbose=True,
                        half_rel_ci=half_rel_ci,
                        ipp_mode=ipp_mode,
                        nsamples_c1=nsamples_c1,
                        vdyp_out_cache=vdyp_out_cache,
                        log_context=run_context,
                    )
                except Exception as exc:
                    _append_jsonl(
                        vdyp_run_events_path,
                        {
                            "event": "vdyp_run",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "status": "dispatch_error",
                            "phase": "bootstrap",
                            "error_type": type(exc).__name__,
                            "error": str(exc),
                            "error_repr": repr(exc),
                            "traceback": traceback.format_exc(),
                            "context": run_context,
                        },
                    )
                    raise
                vdyp_results[tsa][stratumi][si_level] = vdyp_out
                print()
        pickle.dump(vdyp_results[tsa], open(vdyp_results_tsa_pickle_path, "wb"))
    elif (not os.path.isfile(vdyp_results_tsa_pickle_path)) and os.path.isfile(
        vdyp_results_pickle_path
    ):
        try:
            vdyp_results_all = pickle.load(open(vdyp_results_pickle_path, "rb"))
        except ModuleNotFoundError:
            import pandas.compat.pickle_compat as _pickle_compat

            with open(vdyp_results_pickle_path, "rb") as _f:
                vdyp_results_all = _pickle_compat.load(_f)
        vdyp_key = tsa
        if vdyp_key not in vdyp_results_all:
            try:
                vdyp_key = int(tsa)
            except (TypeError, ValueError):
                vdyp_key = tsa
        if vdyp_key in vdyp_results_all:
            vdyp_results[tsa] = vdyp_results_all[vdyp_key]
        else:
            vdyp_results[tsa] = {}
    elif not os.path.isfile(vdyp_results_tsa_pickle_path):
        print()
        vdyp_results[tsa] = {}
        si_levels = ["L", "M", "H"]
        half_rel_ci = 0.01  # use 0.01 for production
        si_levels_ = si_levels
        ipp_mode = None
        nsamples_c1 = 0.05
        for stratumi, sc, result in results[tsa][:]:
            vdyp_results[tsa][stratumi] = {}
            for si_level in si_levels_:
                print("running VDYP in bootstrap sample mode (%s, %s)" % (sc, si_level))
                run_context = {
                    "run_id": femic_run_id,
                    "tsa": tsa,
                    "stratum_index": int(stratumi),
                    "stratum_code": sc,
                    "si_level": si_level,
                }
                _append_jsonl(
                    vdyp_run_events_path,
                    {
                        "event": "vdyp_run",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "status": "dispatch",
                        "phase": "bootstrap",
                        "context": run_context,
                    },
                )
                try:
                    vdyp_out = run_vdyp(
                        result[si_level]["ss"],
                        vdyp_ply,
                        vdyp_lyr,
                        verbose=True,
                        half_rel_ci=half_rel_ci,
                        ipp_mode=ipp_mode,
                        nsamples_c1=nsamples_c1,
                        vdyp_out_cache=vdyp_out_cache,
                        log_context=run_context,
                    )
                except Exception as exc:
                    _append_jsonl(
                        vdyp_run_events_path,
                        {
                            "event": "vdyp_run",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "status": "dispatch_error",
                            "phase": "bootstrap",
                            "error_type": type(exc).__name__,
                            "error": str(exc),
                            "error_repr": repr(exc),
                            "traceback": traceback.format_exc(),
                            "context": run_context,
                        },
                    )
                    raise
                vdyp_results[tsa][stratumi][si_level] = vdyp_out
                print()
        pickle.dump(vdyp_results[tsa], open(vdyp_results_tsa_pickle_path, "wb"))
    else:
        vdyp_results[tsa] = pickle.load(open(vdyp_results_tsa_pickle_path, "rb"))

    # --- cell 44 ---
    @wraps(_curve_fit)
    def curve_fit(*args, **kwargs):
        b = kwargs["bounds"] if "bounds" in kwargs else None
        if b and np.any(np.isfinite(b)) and "max_nfev" not in kwargs:
            kwargs["max_nfev"] = kwargs.pop("maxfev", None)
        return _curve_fit(*args, **kwargs)

    # def toe_fit_func(x, a, b, c):
    #    return a*pow(x, b)

    def fit_func2(x, a, b):
        return a * pow(x, b) * pow(x, -a)

    def fit_func2_bounds_func(x):
        return (0, 0), (10, 10)

    def fill_curve_left(
        x,
        y,
        toe_fit_func=toe_fit_func,
        toe_fit_func_bounds_func=toe_fit_func_bounds_func,
        maxfev=10000,
        transpose_df=True,
        force_origin=True,
        skip=10,
        dx=0,
        di=20,
        cy=0.1,
    ):
        x_, y_ = x, y
        i1 = np.argmax(y_ > 0.0)
        x__ = np.concatenate(([1 + dx, 2 + dx, 3 + dx], x_[i1 + skip : i1 + skip + di]))
        y__ = np.concatenate(([1 * cy, 2 * cy, 3 * cy], y_[i1 + skip : i1 + skip + di]))
        bounds = toe_fit_func_bounds_func(x__)
        popt, _ = curve_fit(toe_fit_func, x__, y__, maxfev=maxfev, bounds=bounds)
        y_[: i1 + skip] = toe_fit_func(x_[: i1 + skip], *popt)
        return x_, y_, (i1 + skip, popt)

    def plot_smoothed_toe(x, y, verbose=False, force_origin=True, skijump_skip=15):
        x_, y_, i1, popt = fill_curve_left(
            testf1, x, y, force_origin=force_origin, skijump_skip=skijump_skip
        )
        # return x_, y_, popt
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.plot(x_, y_, linestyle="--", color="b")
        plt.plot(x_[i1:], y_[i1:], linewidth=2, color="r")
        plt.xlim([0, 300])
        plt.ylim([0, 600])
        if verbose:
            print(popt)
        return fig, ax

    def process_vdyp_out(
        vdyp_out,
        volume_flavour="Vdwb",
        min_age=30,
        max_age=300,
        sigma_c1=10,
        sigma_c2=0.4,
        dx_c1=0.5,
        dx_c2=10,
        window=10,
        skip1=0,
        skip2=30,
        maxfev=100000,
        body_fit_func=body_fit_func,
        body_fit_func_bounds_func=body_fit_func_bounds_func,
        toe_fit_func=toe_fit_func,
        toe_fit_func_bounds_func=toe_fit_func_bounds_func,
        curve_context=None,
        curve_log_path=None,
        max_skip_increase=30,
        skip_step=1,
    ):
        if curve_log_path is None:
            curve_log_path = _vdyp_curve_log_path("vdyp_io")
        base_event = {
            "event": "vdyp_curve",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": dict(curve_context) if curve_context else {},
        }

        def _fallback_curve(stage, reason, x_raw=None, y_raw=None, exc=None):
            if x_raw is None or y_raw is None:
                x_arr = np.array([], dtype=float)
                y_arr = np.array([], dtype=float)
            else:
                x_arr = np.asarray(x_raw, dtype=float)
                y_arr = np.asarray(y_raw, dtype=float)
                mask = np.isfinite(x_arr) & np.isfinite(y_arr) & (y_arr > 0)
                x_arr, y_arr = x_arr[mask], y_arr[mask]
                if x_arr.size:
                    order = np.argsort(x_arr)
                    x_arr, y_arr = x_arr[order], y_arr[order]
                    x_arr, unique_idx = np.unique(x_arr, return_index=True)
                    y_arr = y_arr[unique_idx]
            x_arr, y_arr = _prepend_quasi_origin_point(x_arr, y_arr)
            payload = {
                **base_event,
                "status": "warning",
                "stage": stage,
                "reason": reason,
                "first_age": float(x_arr[0]),
                "first_volume": float(y_arr[0]),
            }
            if exc is not None:
                payload["error"] = str(exc)
                payload["error_type"] = type(exc).__name__
                payload["traceback"] = traceback.format_exc()
            _append_jsonl(curve_log_path, payload)
            return x_arr, y_arr

        vdyp_tables = [
            v for v in vdyp_out.values() if type(v) == pd.core.frame.DataFrame
        ]
        if not vdyp_tables:
            return _fallback_curve(
                "preflight",
                "empty_vdyp_out",
            )
        vdyp_out_concat = pd.concat(vdyp_tables)
        c_all = vdyp_out_concat.groupby(level="Age")[volume_flavour].median()
        c_all = c_all[c_all > 0]
        c = c_all[c_all.index >= min_age]
        if c.empty:
            return _fallback_curve(
                "body_input",
                "no_points_after_min_age_filter",
                c_all.index.values,
                c_all.values,
            )
        x = c.index.values
        y = c.rolling(window=window, center=True).median().values
        x, y = x[y > 0], y[y > 0]
        x, y = x[skip1:], y[skip1:]
        if len(x) < 4 or len(y) < 4:
            return _fallback_curve(
                "body_input",
                "insufficient_points_after_smoothing",
                c.index.values,
                c.values,
            )
        y_mai = pd.Series(y / x, x)
        if y_mai.empty:
            return _fallback_curve(
                "body_input",
                "empty_mai_series",
                c.index.values,
                c.values,
            )
        y_mai_max_age = y_mai.idxmax()
        sigma = (np.abs(x - y_mai_max_age) + sigma_c1) ** sigma_c2
        try:
            popt, pcov = curve_fit(
                body_fit_func,
                x,
                y,
                bounds=body_fit_func_bounds_func(x),
                maxfev=maxfev,
                sigma=sigma,
            )
        except Exception as exc:
            _append_jsonl(
                curve_log_path,
                {
                    **base_event,
                    "status": "error",
                    "stage": "body_fit",
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                    "vdyp_tables": int(len(vdyp_tables)),
                    "x_points": int(len(x)),
                    "skip1": int(skip1),
                    "skip2": int(skip2),
                },
            )
            return _fallback_curve(
                "body_fit_fallback",
                "body_fit_exception",
                x,
                y,
                exc=exc,
            )
        x = np.array(range(1, max_age))
        y = fit_func1(x, *popt)
        dx = max(0, dx_c1 * popt[2] - dx_c2)
        print(dx)
        used_skip = None
        last_exc = None
        for extra in range(0, max_skip_increase + 1, skip_step):
            try:
                x_, y_, (i1, popt_toe) = fill_curve_left(
                    x.copy(),
                    y.copy(),
                    skip=skip2 + extra,
                    dx=dx,
                    maxfev=maxfev,
                    toe_fit_func=toe_fit_func,
                    toe_fit_func_bounds_func=toe_fit_func_bounds_func,
                )
                used_skip = skip2 + extra
                if used_skip != skip2:
                    print(f"vdyp toe fit: increased skip to {used_skip}")
                print(popt_toe)
                x_, y_ = _prepend_quasi_origin_point(x_, y_)
                _append_jsonl(
                    curve_log_path,
                    {
                        **base_event,
                        "status": "ok",
                        "stage": "toe_fit",
                        "vdyp_tables": int(len(vdyp_tables)),
                        "x_points": int(len(x)),
                        "skip1": int(skip1),
                        "skip2": int(skip2),
                        "skip_used": int(used_skip),
                        "dx": float(dx),
                        "first_age": float(x_[0]),
                        "first_volume": float(y_[0]),
                    },
                )
                return x_, y_
            except Exception as exc:
                last_exc = exc
                continue
        _append_jsonl(
            curve_log_path,
            {
                **base_event,
                "status": "warning",
                "stage": "toe_fit",
                "vdyp_tables": int(len(vdyp_tables)),
                "x_points": int(len(x)),
                "skip1": int(skip1),
                "skip2": int(skip2),
                "skip_max": int(skip2 + max_skip_increase),
                "dx": float(dx),
                "error": str(last_exc),
            },
        )
        print(
            "vdyp toe fit failed; returning body fit curve with quasi-origin "
            "(1, epsilon) anchor"
        )
        x, y = _prepend_quasi_origin_point(x, y)
        _append_jsonl(
            curve_log_path,
            {
                **base_event,
                "event": "vdyp_curve_anchor",
                "status": "warning",
                "stage": "quasi_origin_anchor",
                "first_age": float(x[0]),
                "first_volume": float(y[0]),
            },
        )
        return x, y

    # --- cell 45 ---
    vdyp_curves_smooth_tsa_feather_path = "%s%s.feather" % (
        vdyp_curves_smooth_tsa_feather_path_prefix,
        tsa,
    )
    if not os.path.isfile(vdyp_curves_smooth_tsa_feather_path):
        figsize = (8, 6)
        plot = 1
        vdyp_smoothxy = {}
        palette_flavours = ["RdPu", "Blues", "Greens", "Greys"]
        palette = sns.color_palette("Greens", 3)
        sns.set_palette(palette)
        alphas = [1.0, 0.5, 0.1]
        for stratumi, sc, result in results[tsa]:
            # if stratumi != 10: continue
            if plot:
                fig, ax = plt.subplots(1, 1, figsize=figsize)
            print("stratum", stratumi, sc)
            for i, si_level in enumerate(si_levels):
                # for i, si_level in enumerate(['H']):
                print("processing", sc, si_level)
                kwargs = {}
                if (sc, si_level) in kwarg_overrides[tsa]:
                    kwargs.update(kwarg_overrides[tsa][(sc, si_level)])
                curve_context = {
                    "run_id": femic_run_id,
                    "tsa": tsa,
                    "stratum_index": int(stratumi),
                    "stratum_code": sc,
                    "si_level": si_level,
                }
                vdyp_out = vdyp_results.get(tsa, {}).get(stratumi, {}).get(si_level)
                if not isinstance(vdyp_out, dict) or len(vdyp_out) == 0:
                    print("  missing vdyp results for", sc, si_level)
                    _append_jsonl(
                        vdyp_curve_events_path,
                        {
                            "event": "vdyp_curve_fit",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "status": "warning",
                            "stage": "curve_input",
                            "reason": "missing_vdyp_output",
                            "context": curve_context,
                        },
                    )
                    continue
                x, y = process_vdyp_out(vdyp_out, curve_context=curve_context, **kwargs)
                df = pd.DataFrame(zip(x, y), columns=["age", "volume"])
                df = df[df.volume > 0]
                df["stratum_code"] = sc
                df["si_level"] = si_level
                vdyp_smoothxy[(sc, si_level)] = df
                if plot:
                    vdyp_out_concat = pd.concat(
                        [
                            v
                            for v in vdyp_out.values()
                            if type(v) == pd.core.frame.DataFrame
                        ]
                    )
                    c = vdyp_out_concat.groupby(level="Age")["Vdwb"].median()
                    c = c[c > 0]
                    c = c[c.index >= 30]
                    x_ = c.index.values
                    y_ = c.values
                    plt.plot(
                        x_,
                        y_,
                        linestyle=":",
                        label="VDYP->agg (%s %s)" % (sc, si_level),
                        linewidth=2,
                        color=palette[i],
                    )
                    plt.plot(x, y, label="%s %s" % (sc, si_level))
            if plot:
                plt.legend()
                plt.xlim([0, 300])
                plt.ylim([0, 600])
                plt.tight_layout()
        vdyp_curves_smooth[tsa] = pd.concat(
            vdyp_smoothxy.values()
        ).reset_index()  # .set_index(['stratum_code', 'si_level'])
        vdyp_curves_smooth[tsa].to_feather(vdyp_curves_smooth_tsa_feather_path)
    else:
        vdyp_curves_smooth[tsa] = pd.read_feather(vdyp_curves_smooth_tsa_feather_path)

    # --- cell 49 ---
    species_spruce = ["S", "SB", "SE", "SN", "SS", "SW", "SX", "SXE", "SXL", "SXW"]
    species_pine = ["P", "PA", "PJ", "PL", "PLC", "PLI", "PM"]
    species_fir = ["B", "BA", "BB", "BG", "BL", "BM", "BP"]
    species_larch = ["L", "LA", "LS", "LT", "LW"]
    species_cedar = ["C", "CW"]
    species_hemlock = ["HM", "HWI", "HW"]
    species_douglasfir = ["F", "FD", "FDC", "FDI"]

    species_aspen = ["AC", "ACB", "ACT", "AD", "AT", "AX"]
    species_birch = ["E", "EA", "EB", "EE", "EP", "EW", "EXP"]
    species_willow = ["W", "WA", "WB", "WD", "WP", "WS"]
    species_alder = ["D", "DR"]
    species_cherry = ["V"]
    species_dogwood = ["GP"]
    species_oak = ["Q"]
    species_maple = ["M", "MB", "MV"]

    # --- cell 50 ---
    def tipsy_minsi_tsa08(leading_species):
        if leading_species in species_pine:
            return 15.0
        elif leading_species in species_aspen:
            return 15.0
        else:
            return 10.0

    # --- cell 52 ---
    tipsy_exclusion = {
        "08": {
            "min_si": tipsy_minsi_tsa08,
            "min_vol": lambda s: 140.0,
            "excl_bec": [],
            "excl_leading_species": list(
                itertools.chain(
                    species_aspen,
                    species_birch,
                    species_larch,
                    species_willow,
                    species_alder,
                    species_cherry,
                    species_dogwood,
                    species_oak,
                    ["SB"],
                )
            ),
        },
        "16": {
            "min_si": lambda s: 5.0,
            "min_vol": lambda s: 151.0,
            "excl_bec": [],
            "excl_leading_species": list(
                itertools.chain(species_willow, species_birch, species_larch)
            ),
        },
        "24": {
            "min_si": lambda s: 5.0,
            "min_vol": lambda s: 140.0 if s in species_pine else 182.0,
            "excl_bec": ["ICH"],
            "excl_leading_species": list(
                itertools.chain(species_hemlock, species_aspen, species_hemlock, ["SB"])
            ),
        },  # plus "non-commercial deciduous"... whatever that means (no definition of commercial species in TSR data package)
        "40": {
            "min_si": lambda s: 5.0,
            "min_vol": lambda s: 140.0,
            "excl_bec": [],
            "excl_leading_species": list(
                itertools.chain(species_birch, species_larch, ["SB", "ACT"])
            ),
        },
        "41": {
            "min_si": lambda s: 5.0,
            "min_vol": lambda s: 120.0,
            "excl_bec": [],
            "excl_leading_species": list(
                itertools.chain(
                    species_cedar,
                    species_hemlock,
                    species_larch,
                    species_fir,
                    species_alder,
                    species_maple,
                    species_birch,
                    ["SB"],
                )
            ),
        },
    }

    # --- cell 54 ---
    def tipsy_params_tsa08(au_id, au_data, vdyp_out):
        tp = {"e": {}, "f": {}}
        # spp_pct = {spp:data['pct'] for spp, data in au_data['species'].items()}
        # spp_1 = list(spp_pct.keys())[0]
        spp_1 = list(au_data["species"].keys())[0]
        if spp_1 in species_spruce:
            if spp_1 == "SX":
                spp_1 = "SW"  # no SX in TIPSY
            tp["e"]["Density"] = 1472
            tp["f"]["Density"] = 1416
            tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 17.5
        elif spp_1 in species_pine:
            tp["e"]["Density"] = 1624
            tp["f"]["Density"] = 1285
            tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 12.5
        else:
            assert False  # only planting spruce and pine
        # si = au_data['ss'].siteprod.median()
        si = round(au_data["ss"].SITE_INDEX.median(), 1)
        # cc = au_data['ss'].CROWN_CLOSURE.median() * 0.01
        bec = au_data["ss"].BEC_ZONE_CODE.iloc[0]
        #####################################################
        # compile OAF1 from mean stockability from VDYP output
        # (messy!... something about the stupid '%' symbol in the fieldname
        #  breaks compiling tmp in a list comprehension)
        tmp = []
        for k, v in vdyp_out.items():
            try:
                tmp.append(v["% Stk"].iloc[0])
            except:
                pass
        oaf1 = round(np.mean(tmp) * 0.01, 2)
        #####################################################
        # tp['e']['AU'] = tp['f']['AU'] = au_id
        tp["e"]["AU"] = tp["e"]["TBLno"] = 10000 + au_id
        tp["f"]["AU"] = tp["f"]["TBLno"] = 20000 + au_id
        tp["e"]["BEC"] = tp["f"]["BEC"] = bec
        tp["e"]["Proportion"] = tp["f"]["Proportion"] = 1
        tp["e"]["Regen_Delay"] = 2
        tp["f"]["Regen_Delay"] = 1
        tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
        tp["e"]["OAF1"] = tp["f"]["OAF1"] = au_data["ss"] = (
            oaf1  # round(0.85 + (0.15 * cc), 2)
        )
        tp["e"]["OAF2"] = tp["f"]["OAF2"] = 0.95
        tp["e"]["FIZ"] = tp["f"]["FIZ"] = "I"
        tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = spp_1
        tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 100
        tp["e"]["SI"] = tp["f"]["SI"] = si
        tp["e"]["GW_1"] = tp["f"]["GW_1"] = None
        tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = None
        for i in range(2, 6):
            tp["e"]["SPP_%i" % i] = tp["f"]["SPP_%i" % i] = None
            tp["e"]["PCT_%i" % i] = tp["f"]["PCT_%i" % i] = None
            tp["e"]["GW_%i" % i] = tp["f"]["GW_%i" % i] = None
            tp["e"]["GW_age_%i" % i] = tp["f"]["GW_age_%i" % i] = None
        return tp

    def tipsy_params_tsa16(au_id, au_data, vdyp_out):
        tp = {"e": {}, "f": {}}
        spp_1 = list(au_data["species"].keys())[0]
        if spp_1 in species_aspen:
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
            tp["e"]["Density"], tp["f"]["Density"] = 1317, 1405
            tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "AT"
            tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "PLI"
            tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "SW"
            tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = "BL"
            tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
            tp["e"]["PCT_1"], tp["f"]["PCT_1"] = 45, 49
            tp["e"]["PCT_2"], tp["f"]["PCT_2"] = 33, 33
            tp["e"]["PCT_3"], tp["f"]["PCT_3"] = 19, 14
            tp["e"]["PCT_4"], tp["f"]["PCT_4"] = 4, 4
            tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
            tp["e"]["GW_1"] = tp["f"]["GW_1"] = None
            tp["e"]["GW_2"], tp["f"]["GW_2"] = None, 2
            tp["e"]["GW_3"], tp["f"]["GW_3"] = None, 1
            tp["e"]["GW_4"] = tp["f"]["GW_4"] = None
            tp["e"]["GW_5"] = tp["f"]["GW_5"] = None
            tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = None
            tp["e"]["GW_age_2"], tp["f"]["GW_age_2"] = (
                None,
                12,
            )  # not specified in TSR data package (12 is "default" says Cosmin Man)
            tp["e"]["GW_age_3"], tp["f"]["GW_age_3"] = (
                None,
                12,
            )  # not specified in TSR data package (12 is "default" says Cosmin Man)
            tp["e"]["GW_age_4"] = tp["f"]["GW_age_4"] = None
            tp["e"]["GW_age_5"] = tp["f"]["GW_age_5"] = None
            tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 17.5
        elif spp_1 in species_fir:
            tp["e"]["Regen_Delay"], tp["f"]["Regen_Delay"] = 2, 1
            tp["e"]["Density"], tp["f"]["Density"] = 1126, 1216
            tp["e"]["SPP_1"], tp["f"]["SPP_1"] = "BL", "SW"
            tp["e"]["SPP_2"], tp["f"]["SPP_2"] = "SW", "PLI"
            tp["e"]["SPP_3"], tp["f"]["SPP_3"] = "PLI", "BL"
            tp["e"]["SPP_4"], tp["f"]["SPP_4"] = "AT", "AT"
            tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
            tp["e"]["PCT_1"], tp["f"]["PCT_1"] = 53, 50
            tp["e"]["PCT_2"], tp["f"]["PCT_2"] = 24, 27
            tp["e"]["PCT_3"], tp["f"]["PCT_3"] = 17, 21
            tp["e"]["PCT_4"], tp["f"]["PCT_4"] = 6, 2
            tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
            tp["e"]["GW_1"], tp["f"]["GW_1"] = None, 4
            tp["e"]["GW_2"] = tp["f"]["GW_2"] = None
            tp["e"]["GW_3"] = tp["f"]["GW_3"] = None
            tp["e"]["GW_4"] = tp["f"]["GW_4"] = None
            tp["e"]["GW_5"] = tp["f"]["GW_5"] = None
            tp["e"]["GW_age_1"], tp["f"]["GW_age_1"] = (
                None,
                12,
            )  # not specified in TSR data package (12 is "default" says Cosmin Man)
            tp["e"]["GW_age_2"] = tp["f"]["GW_age_2"] = None
            tp["e"]["GW_age_3"] = tp["f"]["GW_age_3"] = None
            tp["e"]["GW_age_4"] = tp["f"]["GW_age_4"] = None
            tp["e"]["GW_age_5"] = tp["f"]["GW_age_5"] = None
            tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 17.5
        elif spp_1 in species_pine:
            tp["e"]["Regen_Delay"], tp["f"]["Regen_Delay"] = 2, 1
            tp["e"]["Density"], tp["f"]["Density"] = 1196, 1231
            tp["e"]["SPP_1"], tp["f"]["SPP_1"] = "PLI", "PLI"
            tp["e"]["SPP_2"], tp["f"]["SPP_2"] = None, None
            tp["e"]["SPP_3"], tp["f"]["SPP_3"] = None, None
            tp["e"]["SPP_4"], tp["f"]["SPP_4"] = None, None
            tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
            tp["e"]["PCT_1"], tp["f"]["PCT_1"] = 100, 100
            tp["e"]["PCT_2"], tp["f"]["PCT_2"] = None, None
            tp["e"]["PCT_3"], tp["f"]["PCT_3"] = None, None
            tp["e"]["PCT_4"], tp["f"]["PCT_4"] = None, None
            tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
            tp["e"]["GW_1"] = tp["f"]["GW_1"] = None
            tp["e"]["GW_2"], tp["f"]["GW_2"] = None, None
            tp["e"]["GW_3"] = tp["f"]["GW_3"] = None
            tp["e"]["GW_4"] = tp["f"]["GW_4"] = None
            tp["e"]["GW_5"] = tp["f"]["GW_5"] = None
            tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = None
            tp["e"]["GW_age_2"], tp["f"]["GW_age_2"] = None, None
            tp["e"]["GW_age_3"] = tp["f"]["GW_age_3"] = None
            tp["e"]["GW_age_4"] = tp["f"]["GW_age_4"] = None
            tp["e"]["GW_age_5"] = tp["f"]["GW_age_5"] = None
            tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 12.5
        elif spp_1 in species_spruce:
            tp["e"]["Regen_Delay"], tp["f"]["Regen_Delay"] = 2, 1
            tp["e"]["Density"], tp["f"]["Density"] = 1147, 1245
            tp["e"]["SPP_1"], tp["f"]["SPP_1"] = "SW", "SW"
            tp["e"]["SPP_2"], tp["f"]["SPP_2"] = "BL", "PLI"
            tp["e"]["SPP_3"], tp["f"]["SPP_3"] = "PLI", "AT"
            tp["e"]["SPP_4"], tp["f"]["SPP_4"] = "AT", "BL"
            tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
            tp["e"]["PCT_1"], tp["f"]["PCT_1"] = 51, 43
            tp["e"]["PCT_2"], tp["f"]["PCT_2"] = 19, 38
            tp["e"]["PCT_3"], tp["f"]["PCT_3"] = 15, 12
            tp["e"]["PCT_4"], tp["f"]["PCT_4"] = 15, 8
            tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
            tp["e"]["GW_1"] = tp["f"]["GW_1"] = None
            tp["e"]["GW_2"], tp["f"]["GW_2"] = None, 2
            tp["e"]["GW_3"] = tp["f"]["GW_3"] = None
            tp["e"]["GW_4"] = tp["f"]["GW_4"] = None
            tp["e"]["GW_5"] = tp["f"]["GW_5"] = None
            tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = None
            tp["e"]["GW_age_2"], tp["f"]["GW_age_2"] = (
                None,
                12,
            )  # not specified in TSR data package (12 is "default" says Cosmin Man)
            tp["e"]["GW_age_3"] = tp["f"]["GW_age_3"] = None
            tp["e"]["GW_age_4"] = tp["f"]["GW_age_4"] = None
            tp["e"]["GW_age_5"] = tp["f"]["GW_age_5"] = None
            tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 17.5
        else:
            assert False  # bad leading species
        tp["e"]["AU"] = tp["e"]["TBLno"] = 10000 + au_id
        tp["f"]["AU"] = tp["f"]["TBLno"] = 20000 + au_id
        # si = au_data['ss'].SITE_INDEX.median()
        si = np.mean([df["SI"].mean() for df in vdyp_out.values()])
        # si /= (au_data['ss'].SITE_INDEX / au_data['ss'].siteprod).median()
        # si = au_data['ss'].siteprod.median()
        tp["e"]["SI"] = tp["f"]["SI"] = round(si, 1)
        tp["e"]["BEC"] = tp["f"]["BEC"] = au_data["ss"].BEC_ZONE_CODE.iloc[0]
        #####################################################
        # compile OAF1 from mean stockability from VDYP output
        # messy!...
        # something about the stupid '%' symbol in the fieldname breaks compiling tmp in a comprehension
        # also the hasty VDYP fixed-width text file import to DataFrame sometimes imports '% Stk' as two fieldnames (skip over broken tables with try/except)
        tmp = []
        for k, v in vdyp_out.items():
            try:
                tmp.append(v["% Stk"].iloc[0])
            except:
                pass
        oaf1 = round(np.mean(tmp) * 0.01, 2)
        #####################################################
        tp["e"]["OAF1"] = tp["f"]["OAF1"] = oaf1
        tp["e"]["OAF2"] = tp["f"]["OAF2"] = 0.95
        tp["e"]["FIZ"] = tp["f"]["FIZ"] = "I"
        tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
        tp["e"]["Proportion"] = tp["f"]["Proportion"] = 1

        return tp

    def tipsy_params_tsa24(au_id, au_data, vdyp_out):
        tp = {"e": {}, "f": {}}
        spp_1 = list(au_data["species"].keys())[0]
        si = round(np.mean([df["SI"].mean() for df in vdyp_out.values()]), 1)
        bec = au_data["ss"].BEC_ZONE_CODE.iloc[0]
        tp["e"]["SI"] = tp["f"]["SI"] = si
        tp["e"]["BEC"] = tp["f"]["BEC"] = bec
        tp["e"]["AU"] = tp["e"]["TBLno"] = 10000 + au_id
        tp["f"]["AU"] = tp["f"]["TBLno"] = 20000 + au_id
        #####################################################
        # compile OAF1 from mean stockability from VDYP output
        # messy!...
        # something about the stupid '%' symbol in the fieldname breaks compiling tmp in a comprehension
        # also the hasty VDYP fixed-width text file import to DataFrame sometimes imports '% Stk' as two fieldnames (skip over broken tables with try/except)
        tmp = []
        for k, v in vdyp_out.items():
            try:
                tmp.append(v["% Stk"].iloc[0])
            except:
                pass
        oaf1 = round(np.mean(tmp) * 0.01, 2)
        #####################################################
        tp["e"]["OAF1"] = tp["f"]["OAF1"] = oaf1
        tp["e"]["OAF2"] = tp["f"]["OAF2"] = 0.95
        tp["e"]["FIZ"] = tp["f"]["FIZ"] = "I"
        tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
        tp["e"]["Proportion"] = tp["f"]["Proportion"] = 1
        tp["e"]["GW_3"] = tp["f"]["GW_3"] = None
        tp["e"]["GW_4"] = tp["f"]["GW_4"] = None
        tp["e"]["GW_5"] = tp["f"]["GW_5"] = None
        tp["e"]["GW_age_3"] = tp["f"]["GW_age_3"] = None
        tp["e"]["GW_age_4"] = tp["f"]["GW_age_4"] = None
        tp["e"]["GW_age_5"] = tp["f"]["GW_age_5"] = None
        tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 17.5
        if bec == "SBS":
            if spp_1 in species_pine:
                tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
                tp["e"]["Density"], tp["f"]["Density"] = 5700, 1700
                tp["e"]["Regen_Method"] = "N"
                tp["e"]["SPP_1"], tp["f"]["SPP_1"] = "PL", "PL"
                tp["e"]["SPP_2"], tp["f"]["SPP_2"] = "SW", "SW"
                tp["e"]["SPP_3"], tp["f"]["SPP_3"] = "BL", None
                tp["e"]["SPP_4"], tp["f"]["SPP_4"] = "FDI", None
                tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
                tp["e"]["PCT_1"], tp["f"]["PCT_1"] = 69, 67
                tp["e"]["PCT_2"], tp["f"]["PCT_2"] = 13, 33
                tp["e"]["PCT_3"], tp["f"]["PCT_3"] = 11, None
                tp["e"]["PCT_4"], tp["f"]["PCT_4"] = 7, None
                tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
                tp["e"]["GW_1"], tp["f"]["GW_1"] = None, 2
                tp["e"]["GW_2"], tp["f"]["GW_2"] = None, 18
                tp["e"]["GW_age_1"], tp["f"]["GW_age_1"] = (
                    None,
                    12,
                )  # not specified in TSR data package (12 is "default" says Cosmin Man)
                tp["e"]["GW_age_2"], tp["f"]["GW_age_2"] = (
                    None,
                    12,
                )  # not specified in TSR data package (12 is "default" says Cosmin Man)
            elif spp_1 in species_spruce:
                tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
                tp["e"]["Density"], tp["f"]["Density"] = 1600, 1600
                tp["e"]["SPP_1"], tp["f"]["SPP_1"] = "SW", "SW"
                tp["e"]["SPP_2"], tp["f"]["SPP_2"] = "PL", "PL"
                tp["e"]["SPP_3"], tp["f"]["SPP_3"] = "FDI", "FDI"
                tp["e"]["SPP_4"], tp["f"]["SPP_4"] = "BL", None
                tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
                tp["e"]["PCT_1"], tp["f"]["PCT_1"] = 55, 55
                tp["e"]["PCT_2"], tp["f"]["PCT_2"] = 38, 38
                tp["e"]["PCT_3"], tp["f"]["PCT_3"] = 5, 7
                tp["e"]["PCT_4"], tp["f"]["PCT_4"] = 2, None
                tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
                tp["e"]["GW_1"], tp["f"]["GW_1"] = 18, 18
                tp["e"]["GW_2"], tp["f"]["GW_2"] = 1, 1
                tp["e"]["GW_age_1"], tp["f"]["GW_age_1"] = (
                    12,
                    12,
                )  # not specified in TSR data package (12 is "default" says Cosmin Man)
                tp["e"]["GW_age_2"], tp["f"]["GW_age_2"] = (
                    12,
                    12,
                )  # not specified in TSR data package (12 is "default" says Cosmin Man)
            elif spp_1 in species_cedar:
                tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
                tp["e"]["Density"] = tp["f"]["Density"] = 2200
                tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "SW"
                tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "PL"
                tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "FDI"
                tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = "BL"
                tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
                tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 55
                tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 21
                tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 16
                tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = 8
                tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
                tp["e"]["GW_1"] = tp["f"]["GW_1"] = 21
                tp["e"]["GW_2"] = tp["f"]["GW_2"] = 2
                tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = (
                    12  # not specified in TSR data package (12 is "default" says Cosmin Man)
                )
                tp["e"]["GW_age_2"] = tp["f"]["GW_age_2"] = (
                    12  # not specified in TSR data package (12 is "default" says Cosmin Man)
                )
            elif spp_1 in species_fir:
                tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
                tp["e"]["Density"] = tp["f"]["Density"] = 2500
                tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "SW"
                tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "PL"
                tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "BL"
                tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = "FDI"
                tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
                tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 57
                tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 25
                tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 10
                tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = 8
                tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
                tp["e"]["GW_1"] = tp["f"]["GW_1"] = 15
                tp["e"]["GW_2"] = tp["f"]["GW_2"] = 1
                tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = (
                    12  # not specified in TSR data package (12 is "default" says Cosmin Man)
                )
                tp["e"]["GW_age_2"] = tp["f"]["GW_age_2"] = (
                    12  # not specified in TSR data package (12 is "default" says Cosmin Man)
                )
            elif spp_1 in species_douglasfir:
                tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
                tp["e"]["Density"] = tp["f"]["Density"] = 1600
                tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "FDI"
                tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = None
                tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = None
                tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = None
                tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
                tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 100
                tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = None
                tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = None
                tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = None
                tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
                tp["e"]["GW_1"] = tp["f"]["GW_1"] = None
                tp["e"]["GW_2"] = tp["f"]["GW_2"] = None
                tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = None
                tp["e"]["GW_age_2"] = tp["f"]["GW_age_2"] = None
            else:
                print(spp_1)
                assert False  # bad species
        elif bec == "ESSF":
            if spp_1 in species_fir:
                tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
                tp["e"]["Density"] = tp["f"]["Density"] = 1500
                tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "SE"
                tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "PL"
                tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "BL"
                tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = None
                tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
                tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 73
                tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 21
                tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 6
                tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = None
                tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
                tp["e"]["GW_1"] = tp["f"]["GW_1"] = 12
                tp["e"]["GW_2"] = tp["f"]["GW_2"] = 2
                tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = (
                    12  # not specified in TSR data package (12 is "default" says Cosmin Man)
                )
                tp["e"]["GW_age_2"] = tp["f"]["GW_age_2"] = (
                    12  # not specified in TSR data package (12 is "default" says Cosmin Man)
                )
            elif spp_1 in species_spruce:
                tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
                tp["e"]["Density"] = tp["f"]["Density"] = 1500
                tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "SE"
                tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "PL"
                tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "BL"
                tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = None
                tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
                tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 82
                tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 13
                tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 5
                tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = None
                tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
                tp["e"]["GW_1"] = tp["f"]["GW_1"] = 18
                tp["e"]["GW_2"] = tp["f"]["GW_2"] = 2
                tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = (
                    12  # not specified in TSR data package (12 is "default" says Cosmin Man)
                )
                tp["e"]["GW_age_2"] = tp["f"]["GW_age_2"] = (
                    12  # not specified in TSR data package (12 is "default" says Cosmin Man)
                )
            elif spp_1 in species_pine:
                tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
                tp["e"]["Density"] = tp["f"]["Density"] = 2900
                tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "PL"
                tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "BL"
                tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "SE"
                tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = None
                tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
                tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 62
                tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 21
                tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 17
                tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = None
                tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
                tp["e"]["GW_1"] = tp["f"]["GW_1"] = 1
                tp["e"]["GW_2"] = tp["f"]["GW_2"] = 13
                tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = (
                    12  # not specified in TSR data package (12 is "default" says Cosmin Man)
                )
                tp["e"]["GW_age_2"] = tp["f"]["GW_age_2"] = (
                    12  # not specified in TSR data package (12 is "default" says Cosmin Man)
                )
                tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 12.5
            else:
                print(spp_1)
                assert False  # bad species
        else:
            print(bec)
            assert False  # bad BEC zone
        return tp

    def tipsy_params_tsa40(au_id, au_data, vdyp_out):
        tp = {"e": {}, "f": {}}
        spp_1 = list(au_data["species"].keys())[0]
        si = round(np.mean([df["SI"].mean() for df in vdyp_out.values()]), 1)
        bec = au_data["ss"].BEC_ZONE_CODE.iloc[0]
        tp["e"]["SI"] = tp["f"]["SI"] = si
        tp["e"]["BEC"] = tp["f"]["BEC"] = bec
        tp["e"]["AU"] = tp["e"]["TBLno"] = 10000 + au_id
        tp["f"]["AU"] = tp["f"]["TBLno"] = 20000 + au_id
        #####################################################
        # compile OAF1 from mean stockability from VDYP output
        # messy!...
        # something about the stupid '%' symbol in the fieldname breaks compiling tmp in a comprehension
        # also the hasty VDYP fixed-width text file import to DataFrame sometimes imports '% Stk' as two fieldnames (skip over broken tables with try/except)
        tmp = []
        for k, v in vdyp_out.items():
            try:
                tmp.append(v["% Stk"].iloc[0])
            except:
                pass
        oaf1 = round(np.mean(tmp) * 0.01, 2)
        #####################################################
        tp["e"]["OAF1"] = tp["f"]["OAF1"] = oaf1
        tp["e"]["OAF2"] = tp["f"]["OAF2"] = 0.95
        tp["e"]["FIZ"] = tp["f"]["FIZ"] = "I"
        tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
        tp["e"]["Proportion"] = tp["f"]["Proportion"] = 1
        tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = (
            17.5 if spp_1 not in [species_pine] else 12.5
        )
        spp_pct = [(spp, au_data["species"][spp]["pct"]) for spp in au_data["species"]]
        for i in range(1, 6):
            try:
                spp, pct = spp_pct[i - 1]
                if spp == "SX":
                    spp = "SW"
            except:
                spp = pct = None
            for j in ["e", "f"]:
                tp[j]["SPP_%i" % i] = spp
                tp[j]["PCT_%i" % i] = pct
                tp[j]["GW_%i" % i] = None
                tp[j]["GW_age_%i" % i] = None

        if bec == "BWBS":
            if spp_1 in species_aspen:
                tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
                tp["e"]["Density"] = tp["f"]["Density"] = 4444
                tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = (
                    "N"  # TSR data package says to use 'N', but then stands break up very early suddenly
                )
            elif spp_1 in species_pine:
                tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
                tp["e"]["Density"] = tp["f"]["Density"] = 1348
                tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
            elif spp_1 in species_spruce:
                tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
                tp["e"]["Density"] = tp["f"]["Density"] = 1167
                tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
            else:
                print("bad species", spp_1)
                assert False
        elif bec == "ESSF":
            if spp_1 in species_pine:
                tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
                tp["e"]["Density"] = tp["f"]["Density"] = 1186
                tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
            elif spp_1 in species_spruce:
                tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
                tp["e"]["Density"] = tp["f"]["Density"] = 1070
                tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
            else:
                print("bad species", spp_1)
                assert False
        elif bec == "SWB":
            if spp_1 in species_pine:
                tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
                tp["e"]["Density"] = tp["f"]["Density"] = 1338
                tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
            elif spp_1 in species_spruce:
                tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
                tp["e"]["Density"] = tp["f"]["Density"] = 1338
                tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
            else:
                print("bad species", spp_1)
                assert False
        else:
            print("bad BEC", bec)
            assert False
        return tp

    def tipsy_params_tsa41(au_id, au_data, vdyp_out):
        tp = {"e": {}, "f": {}}
        si = round(np.mean([df["SI"].mean() for df in vdyp_out.values()]), 1)
        bec = au_data["ss"].BEC_ZONE_CODE.iloc[0]
        forest_type = au_data["ss"]["forest_type"].mode().iloc[0]
        tp["e"]["SI"] = tp["f"]["SI"] = si
        tp["e"]["BEC"] = tp["f"]["BEC"] = bec
        tp["e"]["AU"] = tp["e"]["TBLno"] = 10000 + au_id
        tp["f"]["AU"] = tp["f"]["TBLno"] = 20000 + au_id
        #####################################################
        # compile OAF1 from mean stockability from VDYP output
        # messy!...
        # something about the stupid '%' symbol in the fieldname breaks compiling tmp in a comprehension
        # also the hasty VDYP fixed-width text file import to DataFrame sometimes imports '% Stk' as two fieldnames (skip over broken tables with try/except)
        tmp = []
        for k, v in vdyp_out.items():
            try:
                tmp.append(v["% Stk"].iloc[0])
            except:
                pass
        oaf1 = round(np.mean(tmp) * 0.01, 2)
        #####################################################
        tp["e"]["OAF1"] = tp["f"]["OAF1"] = oaf1
        tp["e"]["OAF2"] = tp["f"]["OAF2"] = 0.95
        tp["e"]["FIZ"] = tp["f"]["FIZ"] = "I"
        tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
        tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
        tp["e"]["Proportion"] = tp["f"]["Proportion"] = 1
        tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
        tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
        spp_pct = [(spp, au_data["species"][spp]["pct"]) for spp in au_data["species"]]
        spp_1, pct_1 = spp_pct[0]
        for i in range(1, 6):
            for j in ["e", "f"]:
                tp[j]["GW_%i" % i] = tp["f"]["GW_age_%i" % i] = None
        if spp_1 in species_spruce:
            if forest_type == 1:  # pure conifer
                tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "SW"
                tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "PL"
                tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "BL"
                tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = "AT"
                tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 63
                tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 21
                tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 17
                tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = 1
                tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
                tp["e"]["Density"] = tp["f"]["Density"] = 1335
            elif forest_type == 2:  # conifer mix
                assert False
                tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "BL"
                tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "BL"
                tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = ""
                tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = "AT"
                tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 63
                tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 21
                tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 17
                tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = 1
                tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
                tp["e"]["Density"] = tp["f"]["Density"] = 1335
            else:
                print(spp_pct)
                assert False  # not implemented (don't need to?)
            tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 17.5
        elif spp_1 in species_fir:
            if forest_type == 1:  # pure conifer
                tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "SW"
                tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "BL"
                tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "PL"
                tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = "AT"
                tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 64
                tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 29
                tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 6
                tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = 1
                tp["e"]["Density"] = tp["f"]["Density"] = 1064
            else:
                assert False  # not implemented (don't need to?)
            tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 17.5
        elif spp_1 in species_pine:
            if forest_type == 1:  # pure conifer
                tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "PL"
                tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "SW"
                tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "BL"
                tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = "AT"
                tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 63
                tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 27
                tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 8
                tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = 2
                tp["e"]["Density"] = tp["f"]["Density"] = 1219
            else:
                assert False  # not implemented (don't need to?)
            tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 12.5
        elif spp_1 in species_aspen:
            if forest_type == 4:  # pure conifer
                tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "AT"
                tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = None
                tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = None
                tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = None
                tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 100
                tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = None
                tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = None
                tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = None
                tp["e"]["Density"] = tp["f"]["Density"] = 3134
                tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "N"
            else:
                assert False  # not implemented (don't need to?)
            tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 12.5
        else:
            print("bad species", spp_1)
            assert False
        return tp

    tipsy_params_dispatch = {
        "08": tipsy_params_tsa08,
        "16": tipsy_params_tsa16,
        "24": tipsy_params_tsa24,
        "40": tipsy_params_tsa40,
        "41": tipsy_params_tsa41,
    }

    # --- cell 55 ---
    min_operable_years = 50
    verbose = 1
    si_iqrlo_quantile = 0.50
    scsi_au[tsa] = {}
    au_scsi[tsa] = {}
    tipsy_params[tsa] = {}
    # for i in range(30):
    vdyp_indexed = vdyp_curves_smooth[tsa].set_index(["stratum_code", "si_level"])
    vdyp_strata = set(vdyp_indexed.index.get_level_values("stratum_code"))
    for stratumi, sc, result in results[tsa]:
        print(sc)
        if sc not in vdyp_strata:
            if verbose:
                print("  missing vdyp curves for stratum", sc)
            continue
        for i, si_level in enumerate(si_levels, start=1):
            au = 1000 * i + stratumi
            te = tipsy_exclusion[tsa]
            try:
                df = vdyp_indexed.loc[sc, si_level]
            except KeyError:
                if verbose:
                    print("  missing vdyp curves for", sc, si_level)
                continue
            max_vol = df.volume.max()
            min_vol = te["min_vol"](sc.split("_")[1][0])
            if max_vol < min_vol:
                if verbose:
                    print("  ", si_level, "max_vol too low", max_vol, te["min_vol"])
                continue
            operable_ages = df[df.volume >= min_vol].age
            operable_years = operable_ages.max() - operable_ages.min()
            if operable_years < min_operable_years:
                if verbose:
                    print(
                        "  ",
                        si_level,
                        "operability window too narrow",
                        operable_years,
                        min_operable_years,
                    )
                continue
            try:
                si_vri_iqrlo = result[si_level]["ss"].SITE_INDEX.quantile(
                    si_iqrlo_quantile
                )
            except:
                print(sc, si_level)
                print(result[si_level]["ss"])
                assert False
            si_spr_iqrlo = result[si_level]["ss"].siteprod.quantile(si_iqrlo_quantile)
            si_vri_med = result[si_level]["ss"].SITE_INDEX.median()
            si_spr_med = result[si_level]["ss"].siteprod.median()
            species_map = result[si_level]["species"]
            if not species_map:
                if verbose:
                    print("  ", si_level, "no species candidates after filtering")
                _append_jsonl(
                    vdyp_curve_events_path,
                    {
                        "event": "vdyp_curve_fit",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "status": "warning",
                        "stage": "tipsy_input",
                        "reason": "no_species_candidates",
                        "context": {
                            "tsa": tsa,
                            "stratum_index": int(stratumi),
                            "stratum_code": sc,
                            "si_level": si_level,
                            "au": int(au),
                        },
                    },
                )
                continue
            leading_species = list(species_map.keys())[0]
            min_si = te["min_si"](leading_species)
            if min(si_vri_iqrlo, si_spr_iqrlo) < min_si:
                if verbose:
                    print(
                        "  ",
                        si_level,
                        "SI too low (using %0.2f quantile)" % si_iqrlo_quantile,
                        "%2.1f" % si_vri_iqrlo,
                        "%2.1f" % si_spr_iqrlo,
                        min_si,
                    )
                continue
            if leading_species in te["excl_leading_species"]:
                if verbose:
                    print("  ", si_level, "bad leading species", leading_species)
                continue
            bec = sc.split("_")[0]
            if bec in te["excl_bec"]:
                if verbose:
                    print("  ", si_level, "bad bec", bec)
                continue

            print("  ", si_level, au)
            print("    median SI (VRI)               ", ("%2.1f" % si_vri_med).rjust(4))
            print("    median SI (siteprod)          ", ("%2.1f" % si_spr_med).rjust(4))
            print(
                "    median SI ratio (VRI/siteprod) ",
                "%0.2f" % (si_vri_med / si_spr_med),
            )
            for species, v in species_map.items():
                print("    species", species.ljust(3), "%3.0f" % v["pct"])
            vdyp_result = vdyp_results.get(tsa, {}).get(stratumi, {}).get(si_level)
            if not isinstance(vdyp_result, dict):
                if verbose:
                    print("    missing vdyp result table for", sc, si_level)
                _append_jsonl(
                    vdyp_curve_events_path,
                    {
                        "event": "vdyp_curve_fit",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "status": "warning",
                        "stage": "tipsy_input",
                        "reason": "missing_vdyp_output",
                        "context": {
                            "tsa": tsa,
                            "stratum_index": int(stratumi),
                            "stratum_code": sc,
                            "si_level": si_level,
                            "au": int(au),
                        },
                    },
                )
                continue
            scsi_au[tsa][(sc, si_level)] = au
            au_scsi[tsa][au] = (sc, si_level)
            tipsy_params[tsa][au] = tipsy_params_dispatch[tsa](
                au, result[si_level], vdyp_result
            )
            print()

    # --- cell 56 ---
    if 0:
        tipsy_params_ = []
        for tsa in tipsy_params:
            for au in tipsy_params[tsa]:
                print(tsa, au)
                tp = tipsy_params[tsa][au]
                tipsy_params_.append(pd.DataFrame(tp["e"], index=[tp["e"]["TBLno"]]))
                tipsy_params_.append(pd.DataFrame(tp["f"], index=[tp["f"]["TBLno"]]))
            df = pd.concat(tipsy_params_)[tipsy_params_columns]
            df.to_excel(
                "%s%s.xlsx" % (tipsy_params_path_prefix, tsa),
                index=False,
                sheet_name="TIPSY_inputTBL",
            )

    # --- cell 57 ---
    tipsy_params_ = []
    for au in tipsy_params[tsa]:
        tp = tipsy_params[tsa][au]
        # tipsy_params_.append(pd.DataFrame(tp['e'], index=[tp['e']['TBLno']]))
        tipsy_params_.append(pd.DataFrame(tp["f"], index=[tp["f"]["TBLno"]]))
    if not tipsy_params_:
        raise RuntimeError(
            f"No TIPSY parameter tables generated for TSA {tsa}; see "
            f"{vdyp_curve_events_path} for missing VDYP diagnostics."
        )
    df = pd.concat(tipsy_params_)[tipsy_params_columns]
    df.to_excel(
        "%s%s.xlsx" % (tipsy_params_path_prefix, tsa),
        index=False,
        sheet_name="TIPSY_inputTBL",
    )

    # --- cell 58 ---
    df.fillna("").to_string("./data/02_input-tsa%s.dat" % tsa, index=False)


if __name__ == "__main__":
    run_tsa()
