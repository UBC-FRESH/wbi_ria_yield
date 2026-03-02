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
        fit_stratum_curves,
        load_vdyp_input_tables,
        load_or_build_vdyp_results_tsa,
        plot_curve_overlays,
    )
    from femic.pipeline.tsa import (
        build_strata_summary,
        build_stratum_lexmatch_alias_map,
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

    # --- cell 5 ---
    totalarea = f_.FEATURE_AREA_SQM.sum()
    f_["totalarea_p"] = f_.FEATURE_AREA_SQM / totalarea

    # --- cell 8 ---
    strata_df, _largestn_strata_codes, site_index_iqr_mean = build_strata_summary(
        f_table=f_,
        stratum_col=stratum_col,
        pd_module=pd,
        tsa_code=tsa,
    )
    print("mean stratum SI IQR", site_index_iqr_mean)
    print("coverage", strata_df.coverage.sum())
    print("count", strata_df.shape[0])

    # --- cell 10 ---
    ax = strata_df.site_index_median.hist(bins=np.arange(25, step=1))
    ax.set_xlim([0, 25])

    # --- cell 12 ---
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
    selected_strata_codes = list(strata_df.index.values)
    best_match = build_stratum_lexmatch_alias_map(
        f_table=f_,
        stratum_col=stratum_col,
        selected_strata_codes=selected_strata_codes,
        levenshtein_fn=distance.levenshtein,
    )

    # --- cell 17 ---
    f_.reset_index(inplace=True)

    # --- cell 18 ---
    def match_stratum(r):
        key = r[stratum_col]
        if key in selected_strata_codes:
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
            fit_out = fit_stratum_curves(
                f_table=f__,
                fit_func=body_fit_func,
                fit_func_bounds_func=body_fit_func_bounds_func,
                strata_df=strata_df,
                stratum_si_stats=stratum_si_stats,
                stratumi=stratumi,
                species_list=species_list,
                curve_fit_fn=curve_fit,
                np_module=np,
                pd_module=pd,
                sns_module=sns,
                plt_module=plt,
                fit_rawdata=fit_rawdata,
                min_age=min_age,
                agg_type=agg_type,
                plot=plot,
                figsize=figsize,
                verbose=verbose,
                ylim=[0, 600],
                xlim=[0, 400],
                message_fn=print,
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
    vdyp_results[tsa] = load_or_build_vdyp_results_tsa(
        tsa=tsa,
        force_run_vdyp=bool(force_run_vdyp),
        vdyp_results_tsa_pickle_path=vdyp_results_tsa_pickle_path,
        vdyp_results_pickle_path=vdyp_results_pickle_path,
        run_bootstrap_fn=lambda: execute_bootstrap_vdyp_runs(
            tsa=tsa,
            run_id=femic_run_id,
            results_for_tsa=results[tsa][:],
            si_levels=si_levels,
            vdyp_run_events_path=vdyp_run_events_path,
            append_jsonl_fn=append_jsonl,
            run_vdyp_fn=lambda s, **kwargs: run_vdyp(s, vdyp_ply, vdyp_lyr, **kwargs),
            vdyp_out_cache=vdyp_out_cache,
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
