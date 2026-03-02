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
    from pathlib import Path

    import distance
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns

    from femic.pipeline.pre_vdyp import (
        load_vdyp_prep_checkpoint,
        pre_vdyp_checkpoint_path,
        save_vdyp_prep_checkpoint,
    )
    from femic.pipeline.vdyp_logging import (
        append_jsonl,
        build_tsa_vdyp_log_paths,
        resolve_run_id,
    )
    from femic.pipeline.vdyp import build_vdyp_cache_paths
    from femic.pipeline.vdyp_curves import (
        legacy_fit_func1,
        legacy_fit_func1_bounds_func,
        process_vdyp_out,
    )
    from femic.pipeline.vdyp_stage import (
        build_bootstrap_vdyp_results_runner,
        build_curve_fit_adapter,
        build_curve_smoothing_plot_config,
        build_stratum_fit_run_config,
        build_fit_stratum_curves_runner,
        build_run_vdyp_for_stratum_runner,
        build_smoothed_curve_table,
        compile_strata_fit_results,
        execute_curve_smoothing_runs,
        load_vdyp_input_tables,
        load_or_build_vdyp_results_tsa,
        plot_curve_overlays,
    )
    from femic.pipeline.tsa import (
        apply_stratum_alias_map,
        build_strata_summary,
        build_stratum_lexmatch_alias_map,
    )
    from femic.pipeline.plots import (
        build_strata_distribution_plot_config,
        plot_strata_site_index_diagnostics,
        render_strata_distribution_plot,
        resolve_strata_plot_ordering,
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
        resolve_tipsy_runtime_options,
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

    # --- cell 10/12 ---
    plot_strata_site_index_diagnostics(
        strata_df=strata_df,
        np_module=np,
        plt_module=plt,
    )

    # --- cell 14 ---
    strata_plot_cfg = build_strata_distribution_plot_config()

    stratum_props, labels = resolve_strata_plot_ordering(
        strata_df=strata_df,
        sort_lex=False,
    )

    render_strata_distribution_plot(
        tsa_code=tsa,
        f_table=f_,
        stratum_col=stratum_col,
        labels=labels,
        stratum_props=stratum_props,
        plot_config=strata_plot_cfg,
        sns_module=sns,
        plt_module=plt,
    )

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
    stratum_col = apply_stratum_alias_map(
        f_table=f_,
        stratum_col=stratum_col,
        selected_strata_codes=selected_strata_codes,
        best_match=best_match,
    )

    # --- cell 20 ---
    f__ = f_.set_index(stratum_col)

    # --- cell 22 ---
    body_fit_func = legacy_fit_func1
    body_fit_func_bounds_func = legacy_fit_func1_bounds_func
    toe_fit_func = legacy_fit_func1
    toe_fit_func_bounds_func = legacy_fit_func1_bounds_func

    # --- cell 24 ---
    stratum_si_stats = f__.groupby(stratum_col).SITE_INDEX.describe(
        percentiles=[0, 0.05, 0.20, 0.35, 0.5, 0.65, 0.80, 0.95, 1]
    )

    # --- cell 28 ---
    N = 30
    stratum_fit_cfg = build_stratum_fit_run_config()

    vdyp_prep_checkpoint_path = pre_vdyp_checkpoint_path(tsa_code=tsa)
    prep_loaded = False
    if resume_effective and Path(vdyp_prep_checkpoint_path).is_file():
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
        compile_one_fn = build_fit_stratum_curves_runner(
            f_table=f__,
            fit_func=body_fit_func,
            fit_func_bounds_func=body_fit_func_bounds_func,
            strata_df=strata_df,
            stratum_si_stats=stratum_si_stats,
            species_list=species_list,
            curve_fit_fn=curve_fit,
            np_module=np,
            pd_module=pd,
            sns_module=sns,
            plt_module=plt,
            fit_rawdata=stratum_fit_cfg.fit_rawdata,
            min_age=stratum_fit_cfg.min_age,
            agg_type=stratum_fit_cfg.agg_type,
            plot=stratum_fit_cfg.plot,
            figsize=stratum_fit_cfg.figsize,
            verbose=stratum_fit_cfg.verbose,
            ylim=stratum_fit_cfg.ylim,
            xlim=stratum_fit_cfg.xlim,
            message_fn=print,
        )
        results[tsa] = compile_strata_fit_results(
            strata_df=strata_df,
            compile_one_fn=compile_one_fn,
            message_fn=print,
        )
        saved_count = save_vdyp_prep_checkpoint(vdyp_prep_checkpoint_path, results[tsa])
        print(
            "saved pre-VDYP checkpoint with %s strata to %s"
            % (saved_count, vdyp_prep_checkpoint_path)
        )

    # --- cell 30/32 ---

    femic_run_id = resolve_run_id()
    vdyp_log_paths = build_tsa_vdyp_log_paths(
        tsa_code=tsa,
        run_id=femic_run_id,
        vdyp_io_dirname="vdyp_io",
    )
    vdyp_run_events_path = vdyp_log_paths["run"]
    vdyp_curve_events_path = vdyp_log_paths["curve"]
    vdyp_stdout_log_path = vdyp_log_paths["stdout"]
    vdyp_stderr_log_path = vdyp_log_paths["stderr"]

    # --- cell 38 ---
    # --- cell 40 ---
    vdyp_ply, vdyp_lyr = load_vdyp_input_tables(
        vdyp_input_pandl_path=vdyp_input_pandl_path,
        vdyp_ply_feather_path=vdyp_ply_feather_path,
        vdyp_lyr_feather_path=vdyp_lyr_feather_path,
        read_from_source=False,
    )

    # --- cell 42 ---
    vdyp_cache_paths = build_vdyp_cache_paths(
        tsa_code=tsa,
        vdyp_results_tsa_pickle_path_prefix=vdyp_results_tsa_pickle_path_prefix,
        vdyp_curves_smooth_tsa_feather_path_prefix=vdyp_curves_smooth_tsa_feather_path_prefix,
    )
    vdyp_results_tsa_pickle_path = vdyp_cache_paths["vdyp_results_tsa_pickle_path"]
    run_vdyp_fn = build_run_vdyp_for_stratum_runner(
        tsa=tsa,
        run_id=femic_run_id,
        vdyp_ply=vdyp_ply,
        vdyp_lyr=vdyp_lyr,
        rc_len=len(rc),
        curve_fit_fn=curve_fit,
        fit_func=body_fit_func,
        fit_func_bounds_func=body_fit_func_bounds_func,
        append_jsonl_fn=append_jsonl,
        vdyp_log_path=vdyp_run_events_path,
        vdyp_stdout_log_path=vdyp_stdout_log_path,
        vdyp_stderr_log_path=vdyp_stderr_log_path,
    )
    run_bootstrap_fn = build_bootstrap_vdyp_results_runner(
        tsa=tsa,
        run_id=femic_run_id,
        results_for_tsa=results[tsa][:],
        si_levels=si_levels,
        vdyp_run_events_path=vdyp_run_events_path,
        append_jsonl_fn=append_jsonl,
        run_vdyp_fn=run_vdyp_fn,
        vdyp_out_cache=vdyp_out_cache,
    )
    vdyp_results[tsa] = load_or_build_vdyp_results_tsa(
        tsa=tsa,
        force_run_vdyp=bool(force_run_vdyp),
        vdyp_results_tsa_pickle_path=vdyp_results_tsa_pickle_path,
        vdyp_results_pickle_path=vdyp_results_pickle_path,
        run_bootstrap_fn=run_bootstrap_fn,
        print_fn=print,
    )

    # --- cell 45 ---
    vdyp_curves_smooth_tsa_feather_path = vdyp_cache_paths[
        "vdyp_curves_smooth_tsa_feather_path"
    ]
    if not Path(vdyp_curves_smooth_tsa_feather_path).is_file():
        smooth_plot_cfg = build_curve_smoothing_plot_config(sns_module=sns)
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
            plot=smooth_plot_cfg.plot,
            figsize=smooth_plot_cfg.figsize,
            palette=smooth_plot_cfg.palette,
            pd_module=pd,
            plt_module=plt,
            dataframe_type=pd.core.frame.DataFrame,
            xlim=smooth_plot_cfg.xlim,
            ylim=smooth_plot_cfg.ylim,
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
    tipsy_config_dir, tipsy_use_legacy = resolve_tipsy_runtime_options()
    tipsy_param_builder, tipsy_param_builder_message = resolve_tipsy_param_builder(
        tsa_code=tsa,
        legacy_builder=legacy_tipsy_builders[tsa],
        config_dir=tipsy_config_dir,
        use_legacy=tipsy_use_legacy,
    )
    print(tipsy_param_builder_message)

    # --- cell 55 ---
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
