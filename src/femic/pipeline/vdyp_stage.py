"""VDYP execution stage helpers for legacy notebook migration."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import functools
import importlib
import pickle
import shlex
import subprocess
import tempfile
import time
import traceback
from pathlib import Path
from typing import Any, cast

from femic.pipeline.diagnostics import (
    build_contextual_error_message,
    build_timestamped_event,
)


@dataclass(frozen=True)
class SmoothedCurveResult:
    """One smoothed curve result for a stratum/SI combination."""

    stratumi: int
    stratum_code: str
    si_level: str
    x: Sequence[float]
    y: Sequence[float]
    vdyp_out: dict[Any, Any]


@dataclass(frozen=True)
class CurveSmoothingPlotConfig:
    """Plot defaults for legacy VDYP curve-smoothing overlays."""

    plot: bool
    figsize: tuple[float, float]
    palette: tuple[Any, ...]
    palette_flavours: tuple[str, ...]
    alphas: tuple[float, ...]
    xlim: tuple[float, float]
    ylim: tuple[float, float]


@dataclass(frozen=True)
class StratumFitRunConfig:
    """Defaults for pre-VDYP stratum curve-fit compilation runs."""

    fit_rawdata: bool
    min_age: int
    agg_type: str
    plot: bool
    verbose: bool
    figsize: tuple[float, float]
    ylim: tuple[float, float]
    xlim: tuple[float, float]


def _curve_fit_skip_exception_types() -> tuple[type[Exception], ...]:
    """Curve-fit failures that should skip one species and continue."""
    return (
        RuntimeError,
        ValueError,
        TypeError,
        OverflowError,
        FloatingPointError,
    )


def _subprocess_run_exception_types() -> tuple[type[Exception], ...]:
    """Subprocess launch/exec failures that should emit VDYP run error records."""
    return (OSError, ValueError, subprocess.SubprocessError)


def _vdyp_parse_exception_types() -> tuple[type[Exception], ...]:
    """VDYP output parse/import failures that should emit parse_error records."""
    return (OSError, ValueError, TypeError, KeyError, UnicodeError)


def _bootstrap_dispatch_exception_types() -> tuple[type[Exception], ...]:
    """VDYP dispatch failures that should emit bootstrap dispatch_error events."""
    return (
        RuntimeError,
        ValueError,
        TypeError,
        OSError,
        KeyError,
        subprocess.SubprocessError,
    )


def build_vdyp_batch_command(
    *,
    vdyp_binpath: str,
    vdyp_params_infile: str,
    vdyp_io_dir: str | Path,
    vdyp_ply_csv: str,
    vdyp_lyr_csv: str,
    vdyp_out_txt: str,
    vdyp_err_txt: str,
) -> str:
    """Build legacy VDYP command text used for execution and logging metadata."""
    vdyp_io_dir_str = str(vdyp_io_dir)
    args = "wine %s -p %s -ip .\\\\%s\\\\%s -il .\\\\%s\\\\%s" % (
        vdyp_binpath,
        vdyp_params_infile,
        vdyp_io_dir_str,
        vdyp_ply_csv,
        vdyp_io_dir_str,
        vdyp_lyr_csv,
    )
    args += " -o .\\\\%s\\\\%s -e .\\\\%s\\\\%s" % (
        vdyp_io_dir_str,
        vdyp_out_txt,
        vdyp_io_dir_str,
        vdyp_err_txt,
    )
    return args


def collect_vdyp_batch_run_metadata(
    *,
    result: Any,
    out_path: Path,
    err_path: Path,
    run_started: float,
    time_fn: Callable[[], float] = time.time,
) -> dict[str, Any]:
    """Collect subprocess/file metadata shared by parse-error and success events."""
    err_size = err_path.stat().st_size if err_path.exists() else 0
    err_head = ""
    if err_size:
        err_head = err_path.read_text(encoding="utf-8", errors="ignore")[:500]
    out_size = out_path.stat().st_size if out_path.exists() else 0
    return {
        "returncode": getattr(result, "returncode", None),
        "duration_sec": round(time_fn() - run_started, 3),
        "out_size": int(out_size),
        "err_size": int(err_size),
        "err_head": err_head,
        "proc_stdout_head": (result.stdout or "")[:500],
        "proc_stderr_head": (result.stderr or "")[:500],
    }


def build_vdyp_run_context(
    *,
    base_context: Mapping[str, Any] | None = None,
    tsa: str | None = None,
    run_id: str | None = None,
    vdyp_stdout_log_path: str | Path | None = None,
    vdyp_stderr_log_path: str | Path | None = None,
    vdyp_binpath: str | Path | None = None,
    vdyp_params: str | Path | None = None,
) -> dict[str, Any]:
    """Build VDYP run context payload while preserving caller-provided values."""
    context = dict(base_context or {})
    if tsa is not None:
        context.setdefault("tsa", tsa)
    if run_id is not None:
        context.setdefault("run_id", run_id)
    if vdyp_stdout_log_path is not None:
        context.setdefault("vdyp_stdout_log", str(vdyp_stdout_log_path))
    if vdyp_stderr_log_path is not None:
        context.setdefault("vdyp_stderr_log", str(vdyp_stderr_log_path))
    if vdyp_binpath is not None:
        context.setdefault("vdyp_binpath", str(vdyp_binpath))
    if vdyp_params is not None:
        context.setdefault("vdyp_params", str(vdyp_params))
    return context


def build_stratum_fit_run_config(
    *,
    fit_rawdata: bool = True,
    min_age: int = 30,
    agg_type: str = "median",
    plot: bool = False,
    verbose: bool = False,
    figsize: tuple[float, float] = (8, 16),
    ylim: tuple[float, float] = (0, 600),
    xlim: tuple[float, float] = (0, 400),
) -> StratumFitRunConfig:
    """Build defaults for pre-VDYP stratum fit stage settings."""
    return StratumFitRunConfig(
        fit_rawdata=bool(fit_rawdata),
        min_age=int(min_age),
        agg_type=str(agg_type),
        plot=bool(plot),
        verbose=bool(verbose),
        figsize=figsize,
        ylim=ylim,
        xlim=xlim,
    )


def build_curve_smoothing_plot_config(
    *,
    sns_module: Any,
    plot: bool = True,
    figsize: tuple[float, float] = (8, 6),
    palette_name: str = "Greens",
    palette_size: int = 3,
    palette_flavours: Sequence[str] = ("RdPu", "Blues", "Greens", "Greys"),
    alphas: Sequence[float] = (1.0, 0.5, 0.1),
    xlim: tuple[float, float] = (0, 300),
    ylim: tuple[float, float] = (0, 600),
) -> CurveSmoothingPlotConfig:
    """Build and apply legacy curve-smoothing plot defaults."""
    palette = tuple(sns_module.color_palette(palette_name, palette_size))
    sns_module.set_palette(palette)
    return CurveSmoothingPlotConfig(
        plot=bool(plot),
        figsize=figsize,
        palette=palette,
        palette_flavours=tuple(str(v) for v in palette_flavours),
        alphas=tuple(float(v) for v in alphas),
        xlim=xlim,
        ylim=ylim,
    )


def build_curve_fit_adapter(
    *,
    curve_fit_impl: Callable[..., Any] | None = None,
    np_module: Any | None = None,
) -> Callable[..., Any]:
    """Build legacy-compatible curve_fit wrapper handling maxfev/max_nfev."""
    curve_fit_fn = curve_fit_impl
    if curve_fit_fn is None:
        scipy_optimize = importlib.import_module("scipy.optimize")
        curve_fit_fn = scipy_optimize.curve_fit
    np_mod = np_module or importlib.import_module("numpy")

    @functools.wraps(curve_fit_fn)
    def curve_fit(*args: Any, **kwargs: Any) -> Any:
        bounds = kwargs.get("bounds")
        if bounds is not None and np_mod.any(np_mod.isfinite(bounds)):
            if "max_nfev" not in kwargs:
                kwargs["max_nfev"] = kwargs.pop("maxfev", None)
        return curve_fit_fn(*args, **kwargs)

    return curve_fit


def load_vdyp_input_tables(
    *,
    vdyp_input_pandl_path: str | Path,
    vdyp_ply_feather_path: str | Path,
    vdyp_lyr_feather_path: str | Path,
    read_from_source: bool = False,
    gpd_module: Any | None = None,
) -> tuple[Any, Any]:
    """Load VDYP polygon/layer tables from feather cache or source geodatabase."""
    gpd_mod = gpd_module or importlib.import_module("geopandas")
    if read_from_source:
        vdyp_ply = gpd_mod.read_file(vdyp_input_pandl_path, driver="FileGDB", layer=0)
        vdyp_ply.to_feather(vdyp_ply_feather_path)
        vdyp_lyr = gpd_mod.read_file(vdyp_input_pandl_path, driver="FileGDB", layer=1)
        vdyp_lyr.to_feather(vdyp_lyr_feather_path)
        return vdyp_ply, vdyp_lyr
    vdyp_ply = gpd_mod.read_feather(vdyp_ply_feather_path)
    vdyp_lyr = gpd_mod.read_feather(vdyp_lyr_feather_path)
    return vdyp_ply, vdyp_lyr


def _default_load_pickle(path: str | Path) -> Any:
    with Path(path).open("rb") as handle:
        return pickle.load(handle)


def _default_dump_pickle(value: Any, path: str | Path) -> None:
    with Path(path).open("wb") as handle:
        pickle.dump(value, handle)


def _default_load_compat_pickle(path: str | Path) -> Any:
    pickle_compat = importlib.import_module("pandas.compat.pickle_compat")
    with Path(path).open("rb") as handle:
        return pickle_compat.load(handle)


def load_or_build_vdyp_results_tsa(
    *,
    tsa: str,
    force_run_vdyp: bool,
    vdyp_results_tsa_pickle_path: str | Path,
    vdyp_results_pickle_path: str | Path,
    run_bootstrap_fn: Callable[[], dict[int, dict[str, dict[Any, Any]]]],
    print_fn: Callable[..., Any] = print,
    load_pickle_fn: Callable[[str | Path], Any] = _default_load_pickle,
    dump_pickle_fn: Callable[[Any, str | Path], None] = _default_dump_pickle,
    load_compat_pickle_fn: Callable[[str | Path], Any] = _default_load_compat_pickle,
) -> dict[int, dict[str, dict[Any, Any]]]:
    """Resolve per-TSA VDYP results from cache, combined cache, or fresh bootstrap."""
    tsa_path = Path(vdyp_results_tsa_pickle_path)
    combined_path = Path(vdyp_results_pickle_path)

    def _bootstrap_and_cache() -> dict[int, dict[str, dict[Any, Any]]]:
        print_fn()
        result = run_bootstrap_fn()
        dump_pickle_fn(result, tsa_path)
        return result

    if force_run_vdyp:
        return _bootstrap_and_cache()

    if (not tsa_path.is_file()) and combined_path.is_file():
        try:
            vdyp_results_all = load_pickle_fn(combined_path)
        except ModuleNotFoundError:
            vdyp_results_all = load_compat_pickle_fn(combined_path)
        vdyp_key: Any = tsa
        if vdyp_key not in vdyp_results_all:
            try:
                vdyp_key = int(tsa)
            except (TypeError, ValueError):
                vdyp_key = tsa
        if vdyp_key in vdyp_results_all:
            return vdyp_results_all[vdyp_key]
        return {}

    if not tsa_path.is_file():
        return _bootstrap_and_cache()

    return load_pickle_fn(tsa_path)


def plot_curve_overlays(
    *,
    results_for_tsa: Sequence[tuple[int, str, Any]],
    si_levels: Sequence[str],
    smoothed_runs: Sequence[SmoothedCurveResult],
    plot: bool,
    figsize: tuple[float, float],
    palette: Sequence[Any],
    pd_module: Any,
    plt_module: Any,
    dataframe_type: type,
    xlim: tuple[float, float] = (0, 300),
    ylim: tuple[float, float] = (0, 600),
    message_fn: Callable[..., Any] = print,
) -> None:
    """Render legacy VDYP overlay plots for smoothed curves."""
    if not plot:
        return
    smoothed_run_map = {(r.stratumi, r.si_level): r for r in smoothed_runs}
    for stratumi, sc, _result in results_for_tsa:
        plt_module.subplots(1, 1, figsize=figsize)
        message_fn("stratum", stratumi, sc)
        for i, si_level in enumerate(si_levels):
            message_fn("processing", sc, si_level)
            run = smoothed_run_map.get((int(stratumi), si_level))
            if run is None:
                continue
            x, y = run.x, run.y
            vdyp_out = run.vdyp_out
            vdyp_out_concat = pd_module.concat(
                [v for v in vdyp_out.values() if isinstance(v, dataframe_type)]
            )
            c = vdyp_out_concat.groupby(level="Age")["Vdwb"].median()
            c = c[c > 0]
            c = c[c.index >= 30]
            x_ = c.index.values
            y_ = c.values
            plt_module.plot(
                x_,
                y_,
                linestyle=":",
                label="VDYP->agg (%s %s)" % (sc, si_level),
                linewidth=2,
                color=palette[i],
            )
            plt_module.plot(x, y, label="%s %s" % (sc, si_level))
        plt_module.legend()
        plt_module.xlim(xlim)
        plt_module.ylim(ylim)
        plt_module.tight_layout()


def build_smoothed_curve_table(
    *,
    smoothed_runs: Sequence[SmoothedCurveResult],
    pd_module: Any,
    output_path: str | Path | None = None,
) -> Any:
    """Build and optionally persist the smoothed VDYP curve table."""
    frames = []
    for run in smoothed_runs:
        df = pd_module.DataFrame(zip(run.x, run.y), columns=["age", "volume"])
        df = df[df.volume > 0]
        df["stratum_code"] = run.stratum_code
        df["si_level"] = run.si_level
        frames.append(df)
    curve_table = pd_module.concat(frames).reset_index()
    if output_path is not None:
        curve_table.to_feather(output_path)
    return curve_table


def fit_stratum_curves(
    *,
    f_table: Any,
    fit_func: Callable[..., Any],
    fit_func_bounds_func: Callable[[Any], Any],
    strata_df: Any,
    stratum_si_stats: Any,
    stratumi: int,
    species_list: Sequence[str],
    curve_fit_fn: Callable[..., Any],
    np_module: Any,
    pd_module: Any,
    sns_module: Any,
    plt_module: Any,
    plot: bool = True,
    figsize: tuple[float, float] = (6, 12),
    verbose: bool = False,
    xlim: tuple[float, float] = (0, 300),
    ylim: tuple[float, float] = (0, 500),
    si_levelquants: Mapping[str, Sequence[float]] | None = None,
    linestyles: Sequence[str] | None = None,
    markers: Sequence[str] | None = None,
    palette_flavours: Sequence[str] | None = None,
    maxfev: int = 100000,
    min_age: int = 30,
    max_age: int = 300,
    max_records: int = 15000,
    sigma_exponent: float = 1.0,
    window: int = 10,
    min_periods: int | None = None,
    center: bool = False,
    agg_type: str = "median",
    sv_thresh: float = 0.10,
    rawdata_alpha: float = 0.05,
    fitattr_thresh: float = 1.0,
    fit_rawdata: bool = True,
    debug: bool = False,
    message_fn: Callable[..., Any] = print,
) -> dict[str, Any]:
    """Fit per-SI species curves for one stratum using legacy notebook logic."""
    del max_records, sigma_exponent, window, min_periods, center, debug
    if si_levelquants is None:
        si_levelquants = {
            "L": [5, 20, 35],
            "M": [35, 50, 65],
            "H": [65, 80, 95],
        }
    if linestyles is None:
        linestyles = ["-", "--", ":"]
    if markers is None:
        markers = ["x", "+", "*"]
    if palette_flavours is None:
        palette_flavours = ["RdPu", "Blues", "Greens"]

    _palettes = [sns_module.color_palette(pf, 3) for pf in palette_flavours]
    pd_module.options.mode.chained_assignment = None
    sc = strata_df.iloc[stratumi].name
    if verbose:
        message_fn("processing stratum", sc)
    if plot:
        _fig, ax = plt_module.subplots(4, 1, figsize=figsize, sharex=True, sharey=True)
        palette = sns_module.color_palette("RdPu", 3)
        sns_module.set_palette(palette)
        ax_ = {
            "L": ax[1],
            "M": ax[2],
            "H": ax[3],
        }
        palette_ = {v: palette[i] for i, v in enumerate("LMH")}
    result: dict[str, Any] = {}
    for i, (si_level, q_values) in enumerate(si_levelquants.items()):
        del i
        result[si_level] = {}
        ss = f_table.loc[[sc]].copy()
        si_lo = stratum_si_stats.loc[sc].loc["%i%%" % q_values[0]]
        si_md = stratum_si_stats.loc[sc].loc["%i%%" % q_values[1]]
        si_hi = stratum_si_stats.loc[sc].loc["%i%%" % q_values[2]]
        ss = ss[
            (ss.SITE_INDEX >= si_lo)
            & (ss.SITE_INDEX < si_hi)
            & (ss.PROJ_AGE_1 >= min_age)
            & (ss.PROJ_AGE_1 < max_age)
        ]
        ss = ss.sort_values("PROJ_AGE_1")
        stand_volume_total = ss["LIVE_STAND_VOLUME_125"].sum()
        if stand_volume_total <= 0:
            sv = pd_module.Series(dtype=float)
        else:
            sv = pd_module.Series(
                {
                    species: (
                        ss[f"live_vol_per_ha_125_{species}"].sum() / stand_volume_total
                    )
                    for species in species_list
                }
            ).sort_values(ascending=False)
            sv = sv[sv > sv_thresh]
        result[si_level]["ss"] = ss
        if verbose:
            message_fn("sv sum", sv.sum())
        if plot:
            x, y = [], []
            for j, species in enumerate(sv.index.values):
                fitattr = f"live_vol_per_ha_125_{species}"
                sss = ss[ss[fitattr] >= 1]
                x.append(sss.PROJ_AGE_1.values)
                y.append(sss[fitattr].values / sv.sum())
            x = np_module.concatenate(x)
            y = np_module.concatenate(y)
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
                message_fn(
                    "  fitting SI level %s (%2.1f), species %s"
                    % (si_level, si_md, species)
                )
            fitattr = f"live_vol_per_ha_125_{species}"
            sss = ss[ss[fitattr] >= fitattr_thresh]
            if fit_rawdata:
                x = sss.PROJ_AGE_1.values
                y = sss[fitattr].values / sv.sum()
                sigma = None
            else:
                agg = sss.groupby("PROJ_AGE_1")[fitattr].agg(
                    ["mean", "median", "std", "count"]
                )
                agg = agg[agg["count"] > 2]
                agg["sigma"] = ((agg["std"].mean() + agg["std"]) / agg["count"]) ** 0.5
                x = agg.index.values
                y = agg[agg_type].values / sv.sum()
                sigma = agg["sigma"].values
            bounds = fit_func_bounds_func(x)
            try:
                popt, pcov = curve_fit_fn(
                    fit_func,
                    x,
                    y,
                    bounds=bounds,
                    maxfev=maxfev,
                    sigma=sigma,
                )
            except _curve_fit_skip_exception_types() as exc:
                message_fn(
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
                message_fn("fitting N raw data points", sss.shape[0])
                message_fn("popt", popt)
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
                x_ = np_module.linspace(popt[2], 300, 30)
                y_ = fit_func(x_, *popt)
                sns_module.lineplot(
                    x_,
                    y_,
                    label="func fit (%s SI, %s)" % (si_level, species),
                    ax=ax[0],
                    color=palette_[si_level],
                    linestyle=linestyles[j],
                    linewidth=3,
                )
                sns_module.lineplot(
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
            age = int(round(np_module.min(x) * 1.0))
            result[si_level]["species"][species]["age"] = (
                age if not np_module.isnan(age) else None
            )
            jj = min(2, j + 1)
            ssss = sss[
                (sss[f"PROJ_AGE_{jj}"] >= age - 5) & (sss[f"PROJ_AGE_{jj}"] < age + 5)
            ]
            height = ssss[f"PROJ_HEIGHT_{jj}"].median()
            result[si_level]["species"][species]["height"] = (
                height if not np_module.isnan(height) else None
            )
            result[si_level]["species"][species]["fit_func"] = fit_func
            result[si_level]["species"][species]["popt"] = popt
            result[si_level]["species"][species]["pcov"] = pcov
    if plot:
        ax[0].set_title("Best-fit yield curves (stratum %s)" % sc)
        plt_module.legend(loc="best")
        plt_module.xlim(xlim)
        plt_module.ylim(ylim)
        plt_module.xlabel("Stand age (years)")
        plt_module.ylabel("Merch. volume (m3/ha)")
        plt_module.tight_layout()
        plt_module.savefig(
            "plots/yieldcurve_fit-%s-%s.png" % (str(stratumi).zfill(2), sc),
            facecolor="white",
        )
        plt_module.savefig(
            "plots/yieldcurve_fit-%s-%s.pdf" % (str(stratumi).zfill(2), sc),
            facecolor="white",
        )
    return result


def build_fit_stratum_curves_runner(
    *,
    f_table: Any,
    fit_func: Callable[..., Any],
    fit_func_bounds_func: Callable[..., Any],
    strata_df: Any,
    stratum_si_stats: Any,
    species_list: Sequence[str],
    curve_fit_fn: Callable[..., Any],
    fit_rawdata: bool,
    min_age: int,
    agg_type: str,
    plot: bool,
    figsize: tuple[int, int],
    verbose: bool,
    ylim: Sequence[float],
    xlim: Sequence[float],
    np_module: Any,
    pd_module: Any,
    sns_module: Any,
    plt_module: Any,
    message_fn: Callable[..., Any] = print,
    fit_stratum_curves_fn: Callable[..., Any] = fit_stratum_curves,
) -> Callable[[int, str], Any]:
    """Build a compile-one callback that runs `fit_stratum_curves(...)` for one stratum."""

    def _compile_one(stratumi: int, _sc: str) -> Any:
        return fit_stratum_curves_fn(
            f_table=f_table,
            fit_func=fit_func,
            fit_func_bounds_func=fit_func_bounds_func,
            strata_df=strata_df,
            stratum_si_stats=stratum_si_stats,
            stratumi=stratumi,
            species_list=species_list,
            curve_fit_fn=curve_fit_fn,
            np_module=np_module,
            pd_module=pd_module,
            sns_module=sns_module,
            plt_module=plt_module,
            fit_rawdata=fit_rawdata,
            min_age=min_age,
            agg_type=agg_type,
            plot=plot,
            figsize=figsize,
            verbose=verbose,
            ylim=ylim,
            xlim=xlim,
            message_fn=message_fn,
        )

    return _compile_one


def compile_strata_fit_results(
    *,
    strata_df: Any,
    compile_one_fn: Callable[[int, str], Any],
    message_fn: Callable[..., Any] = print,
) -> list[list[Any]]:
    """Compile fit payloads for each selected stratum index/code pair."""
    compiled: list[list[Any]] = []
    for stratumi, sc in enumerate(strata_df.index.values[:]):
        message_fn("compiling stratum %s" % sc)
        fit_out = compile_one_fn(stratumi, sc)
        compiled.append([stratumi, sc, fit_out])
    return compiled


def run_vdyp_sampling(
    *,
    sample_table: Any,
    nsamples: str | int,
    min_samples: int,
    max_samples: int,
    nsamples_c1: float,
    nsamples_c2: float,
    confidence: float,
    half_rel_ci: float,
    ipp_mode: str | None,
    vdyp_timeout: float,
    rc_len: int,
    verbose: bool,
    vdyp_out_cache: dict[Any, Any] | None,
    run_batch_fn: Callable[..., dict[Any, Any]],
    nsamples_from_curves_fn: Callable[..., tuple[int, Any]],
    message_fn: Callable[..., Any] = print,
) -> dict[Any, Any]:
    """Run legacy VDYP sampling flow (auto/all/fixed) for one stratum sample table."""

    def _take_cached(
        feature_ids: Sequence[Any], vdyp_out: dict[Any, Any]
    ) -> tuple[list[Any], int]:
        if vdyp_out_cache is None:
            return list(feature_ids), 0
        uncached: list[Any] = []
        for fid in feature_ids:
            if fid in vdyp_out_cache:
                vdyp_out[fid] = vdyp_out_cache[fid]
            else:
                uncached.append(fid)
        cache_hits = len(feature_ids) - len(uncached)
        return uncached, cache_hits

    if nsamples == "auto" and sample_table.shape[0] < min_samples:
        if sample_table.shape[0] == 0:
            return {}
        if verbose:
            message_fn(
                "auto mode: stratum has fewer than min_samples; "
                f"running all {sample_table.shape[0]} records"
            )
        vdyp_out = run_batch_fn(
            sample_table.FEATURE_ID.values, phase="auto_small_sample"
        )
        if vdyp_out_cache is not None:
            vdyp_out_cache.update(vdyp_out)
        return vdyp_out

    if nsamples == "auto" and sample_table.shape[0] >= min_samples:
        ss = sample_table.reset_index().set_index("index")
        samples = ss.sample(min(min_samples, ss.shape[0]))
        vdyp_out = {}
        feature_ids, cache_hits = _take_cached(
            samples.FEATURE_ID.values, vdyp_out=vdyp_out
        )
        vdyp_out_new = run_batch_fn(feature_ids, cache_hits=cache_hits, phase="initial")
        vdyp_out.update(vdyp_out_new)
        if vdyp_out_cache is not None:
            vdyp_out_cache.update(vdyp_out)
        ss.drop(samples.index, inplace=True)
        nsamples_target, _ = nsamples_from_curves_fn(
            vdyp_out,
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
                message_fn(
                    "moe loop",
                    nsamples_target,
                    nsamples_new,
                    "%0.2f" % nsamples_gap_rel,
                    len(vdyp_out),
                    ss.shape[0],
                )
            samples = ss.sample(nsamples_new)
            feature_ids = samples.FEATURE_ID.values
            timeout = 30 + (vdyp_timeout * feature_ids.shape[0] / rc_len)
            if not ipp_mode or samples.shape[0] < min_samples:
                feature_ids, cache_hits = _take_cached(feature_ids, vdyp_out=vdyp_out)
                vdyp_out_ = run_batch_fn(
                    feature_ids,
                    timeout=timeout,
                    cache_hits=cache_hits,
                    phase="gap_fill",
                )
                vdyp_out.update(vdyp_out_)
                if vdyp_out_cache is not None:
                    vdyp_out_cache.update(vdyp_out)
            elif ipp_mode == "load_balanced":
                raise NotImplementedError(
                    build_contextual_error_message(
                        prefix="Unsupported VDYP sampling mode",
                        context={"ipp_mode": ipp_mode, "nsamples": nsamples},
                    )
                )
            ss.drop(samples.index, inplace=True)
            nsamples_target, _ = nsamples_from_curves_fn(
                vdyp_out,
                confidence=confidence,
                half_rel_ci=half_rel_ci,
            )
            nsamples_target = min(
                max(nsamples_target, min_samples), sample_table.shape[0]
            )
            nsamples_gap = nsamples_target - len(vdyp_out)
            nsamples_gap_rel = nsamples_gap / nsamples_target
        if verbose:
            message_fn("final gap", nsamples_gap_rel)
        return vdyp_out

    if nsamples == "all":
        return run_batch_fn(sample_table.FEATURE_ID.values, phase="all")
    if isinstance(nsamples, int):
        samples = sample_table.sample(nsamples)
        return run_batch_fn(samples.FEATURE_ID.values, phase="fixed")
    raise ValueError(
        build_contextual_error_message(
            prefix="Unsupported nsamples mode in run_vdyp_sampling",
            context={
                "nsamples": repr(nsamples),
                "expected": "'auto' | 'all' | int",
            },
            skip_none=False,
        )
    )


def run_vdyp_for_stratum(
    *,
    sample_table: Any,
    tsa: str,
    run_id: str,
    vdyp_ply: Any,
    vdyp_lyr: Any,
    rc_len: int,
    curve_fit_fn: Callable[..., Any],
    fit_func: Callable[..., Any],
    fit_func_bounds_func: Callable[..., Any],
    nsamples: str | int = "auto",
    vdyp_io_dirname: str = "vdyp_io",
    vdyp_params_infile: str = "vdyp_params-landp",
    vdyp_binpath: str = "VDYP7/VDYP7/VDYP7Console.exe",
    nsamples_c1: float = 0.01,
    nsamples_c2: float = 0.1,
    verbose: bool = False,
    confidence: float = 95,
    half_rel_ci: float = 0.05,
    min_samples: int = 100,
    max_samples: int = 640,
    ipp_mode: str | None = None,
    vdyp_timeout: float = 2.0,
    vdyp_out_cache: dict[Any, Any] | None = None,
    vdyp_log_path: str | Path | None = None,
    vdyp_stdout_log_path: str | Path | None = None,
    vdyp_stderr_log_path: str | Path | None = None,
    log_context: Mapping[str, Any] | None = None,
    which_fn: Callable[[str], str | None] | None = None,
    build_tsa_vdyp_log_paths_fn: Callable[..., Mapping[str, str | Path]] | None = None,
    append_jsonl_fn: Callable[[str | Path, Any], None] | None = None,
    append_text_fn: Callable[[str | Path, str], None] | None = None,
    execute_vdyp_batch_fn: Callable[..., dict[Any, Any]] | None = None,
    write_vdyp_infiles_fn: Callable[..., None] | None = None,
    import_vdyp_tables_fn: Callable[[str], dict[Any, Any]] | None = None,
    nsamples_from_curves_fn: Callable[..., tuple[int, Any]] | None = None,
    message_fn: Callable[..., Any] = print,
) -> dict[Any, Any]:
    """Run VDYP for one stratum sample table with logging and sampling orchestration."""
    import shutil

    if which_fn is None:
        which_fn = shutil.which
    if build_tsa_vdyp_log_paths_fn is None:
        from femic.pipeline.vdyp_logging import build_tsa_vdyp_log_paths

        build_tsa_vdyp_log_paths_fn = build_tsa_vdyp_log_paths
    if append_jsonl_fn is None:
        from femic.pipeline.vdyp_logging import append_jsonl

        append_jsonl_fn = append_jsonl
    if append_text_fn is None:
        from femic.pipeline.vdyp_logging import append_text

        append_text_fn = append_text
    if write_vdyp_infiles_fn is None:
        from femic.pipeline.vdyp_io import write_vdyp_infiles_plylyr

        write_vdyp_infiles_fn = write_vdyp_infiles_plylyr
    if import_vdyp_tables_fn is None:
        from femic.pipeline.vdyp_io import import_vdyp_tables

        import_vdyp_tables_fn = import_vdyp_tables
    if nsamples_from_curves_fn is None:
        from femic.pipeline.vdyp_sampling import nsamples_from_curves

        def _default_nsamples_from_curves(
            vdyp_out: dict[Any, Any], **kwargs: Any
        ) -> tuple[int, Any]:
            nsamples_target, fit_out = nsamples_from_curves(vdyp_out, **kwargs)
            return int(nsamples_target), fit_out

        nsamples_from_curves_fn = _default_nsamples_from_curves
    if execute_vdyp_batch_fn is None:
        execute_vdyp_batch_fn = execute_vdyp_batch

    build_tsa_vdyp_log_paths_ = cast(
        Callable[..., Mapping[str, str | Path]], build_tsa_vdyp_log_paths_fn
    )
    append_jsonl_ = cast(Callable[[str | Path, Any], None], append_jsonl_fn)
    append_text_ = cast(Callable[[str | Path, str], None], append_text_fn)
    execute_vdyp_batch_ = cast(Callable[..., dict[Any, Any]], execute_vdyp_batch_fn)
    nsamples_from_curves_ = cast(
        Callable[..., tuple[int, Any]], nsamples_from_curves_fn
    )

    if which_fn("wine") is None:
        raise RuntimeError(
            "wine not found; VDYP7 requires wine to run on non-Windows systems"
        )
    vdyp_binpath_path = Path(vdyp_binpath)
    if not vdyp_binpath_path.exists():
        raise RuntimeError(f"VDYP executable not found: {vdyp_binpath_path.resolve()}")
    vdyp_params_path = Path(vdyp_params_infile)
    if not vdyp_params_path.exists():
        raise RuntimeError(f"VDYP params path not found: {vdyp_params_path.resolve()}")
    Path(vdyp_io_dirname).mkdir(parents=True, exist_ok=True)

    tsa_paths = build_tsa_vdyp_log_paths_(
        tsa_code=tsa,
        run_id=run_id,
        vdyp_io_dirname=vdyp_io_dirname,
    )
    if vdyp_log_path is None:
        vdyp_log_path = tsa_paths["run"]
    if vdyp_stdout_log_path is None:
        vdyp_stdout_log_path = tsa_paths["stdout"]
    if vdyp_stderr_log_path is None:
        vdyp_stderr_log_path = tsa_paths["stderr"]

    base_context = build_vdyp_run_context(
        base_context=log_context,
        tsa=tsa,
        run_id=run_id,
        vdyp_stdout_log_path=vdyp_stdout_log_path,
        vdyp_stderr_log_path=vdyp_stderr_log_path,
        vdyp_binpath=vdyp_binpath_path,
        vdyp_params=vdyp_params_path,
    )

    def _run_batch(
        feature_ids: Sequence[Any],
        *,
        timeout: int | float | None = None,
        cache_hits: int = 0,
        phase: str | None = None,
    ) -> dict[Any, Any]:
        feature_ids_list = list(feature_ids)
        feature_count = len(feature_ids_list)
        if feature_count == 0:
            append_jsonl_(
                vdyp_log_path,
                build_timestamped_event(
                    event="vdyp_run",
                    status="cache_only",
                    phase=phase,
                    feature_count=0,
                    cache_hits=int(cache_hits),
                    context=base_context,
                ),
            )
            return {}
        append_jsonl_(
            vdyp_log_path,
            build_timestamped_event(
                event="vdyp_run",
                status="start",
                phase=phase,
                feature_count=int(feature_count),
                cache_hits=int(cache_hits),
                context=base_context,
            ),
        )
        return execute_vdyp_batch_(
            feature_ids=feature_ids_list,
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
            timeout=int(timeout) if timeout is not None else 30,
            run_id=run_id,
            base_context=base_context,
            write_vdyp_infiles=write_vdyp_infiles_fn,
            import_vdyp_tables_fn=import_vdyp_tables_fn,
            append_jsonl_fn=append_jsonl_,
            append_text_fn=append_text_,
        )

    return run_vdyp_sampling(
        sample_table=sample_table,
        nsamples=nsamples,
        min_samples=min_samples,
        max_samples=max_samples,
        nsamples_c1=nsamples_c1,
        nsamples_c2=nsamples_c2,
        confidence=confidence,
        half_rel_ci=half_rel_ci,
        ipp_mode=ipp_mode,
        vdyp_timeout=vdyp_timeout,
        rc_len=rc_len,
        verbose=verbose,
        vdyp_out_cache=vdyp_out_cache,
        run_batch_fn=lambda feature_ids, **kwargs: _run_batch(feature_ids, **kwargs),
        nsamples_from_curves_fn=lambda vdyp_out, **kwargs: nsamples_from_curves_(
            vdyp_out,
            curve_fit_fn=curve_fit_fn,
            fit_func=fit_func,
            fit_func_bounds_func=fit_func_bounds_func,
            **kwargs,
        ),
        message_fn=message_fn,
    )


def build_run_vdyp_for_stratum_runner(
    *,
    tsa: str,
    run_id: str,
    vdyp_ply: Any,
    vdyp_lyr: Any,
    rc_len: int,
    curve_fit_fn: Callable[..., Any],
    fit_func: Callable[..., Any],
    fit_func_bounds_func: Callable[..., Any],
    append_jsonl_fn: Callable[[str | Path, Any], None] | None = None,
    vdyp_log_path: str | Path | None = None,
    vdyp_stdout_log_path: str | Path | None = None,
    vdyp_stderr_log_path: str | Path | None = None,
    run_vdyp_for_stratum_fn: Callable[..., dict[Any, Any]] = run_vdyp_for_stratum,
) -> Callable[..., dict[Any, Any]]:
    """Build a per-TSA VDYP runner callable for bootstrap dispatch helpers."""

    def _run_vdyp(sample_table: Any, **kwargs: Any) -> dict[Any, Any]:
        return run_vdyp_for_stratum_fn(
            sample_table=sample_table,
            tsa=tsa,
            run_id=run_id,
            vdyp_ply=vdyp_ply,
            vdyp_lyr=vdyp_lyr,
            rc_len=rc_len,
            curve_fit_fn=curve_fit_fn,
            fit_func=fit_func,
            fit_func_bounds_func=fit_func_bounds_func,
            append_jsonl_fn=append_jsonl_fn,
            vdyp_log_path=vdyp_log_path,
            vdyp_stdout_log_path=vdyp_stdout_log_path,
            vdyp_stderr_log_path=vdyp_stderr_log_path,
            **kwargs,
        )

    return _run_vdyp


def execute_bootstrap_vdyp_runs(
    *,
    tsa: str,
    run_id: str,
    results_for_tsa: Sequence[tuple[int, str, Any]],
    si_levels: Sequence[str],
    vdyp_run_events_path: str | Path,
    append_jsonl_fn: Callable[[str | Path, Any], None],
    run_vdyp_fn: Callable[..., dict[Any, Any]],
    vdyp_out_cache: dict[Any, Any] | None = None,
    verbose: bool = True,
    half_rel_ci: float = 0.01,
    ipp_mode: str | None = None,
    nsamples_c1: float = 0.05,
) -> dict[int, dict[str, dict[Any, Any]]]:
    """Execute bootstrap VDYP runs across stratum/SI combinations."""
    vdyp_results_tsa: dict[int, dict[str, dict[Any, Any]]] = {}
    for stratumi, sc, result in results_for_tsa:
        vdyp_results_tsa[stratumi] = {}
        for si_level in si_levels:
            if verbose:
                print(f"running VDYP in bootstrap sample mode ({sc}, {si_level})")
            run_context = {
                "run_id": run_id,
                "tsa": tsa,
                "stratum_index": int(stratumi),
                "stratum_code": sc,
                "si_level": si_level,
            }
            append_jsonl_fn(
                vdyp_run_events_path,
                build_timestamped_event(
                    event="vdyp_run",
                    status="dispatch",
                    phase="bootstrap",
                    context=run_context,
                ),
            )
            try:
                vdyp_out = run_vdyp_fn(
                    result[si_level]["ss"],
                    verbose=verbose,
                    half_rel_ci=half_rel_ci,
                    ipp_mode=ipp_mode,
                    nsamples_c1=nsamples_c1,
                    vdyp_out_cache=vdyp_out_cache,
                    log_context=run_context,
                )
            except _bootstrap_dispatch_exception_types() as exc:
                append_jsonl_fn(
                    vdyp_run_events_path,
                    build_timestamped_event(
                        event="vdyp_run",
                        status="dispatch_error",
                        phase="bootstrap",
                        error_type=type(exc).__name__,
                        error=str(exc),
                        error_repr=repr(exc),
                        traceback=traceback.format_exc(),
                        context=run_context,
                    ),
                )
                raise
            vdyp_results_tsa[stratumi][si_level] = vdyp_out
            if verbose:
                print()
    return vdyp_results_tsa


def build_bootstrap_vdyp_results_runner(
    *,
    tsa: str,
    run_id: str,
    results_for_tsa: Sequence[tuple[int, str, Any]],
    si_levels: Sequence[str],
    vdyp_run_events_path: str | Path,
    append_jsonl_fn: Callable[[str | Path, Any], None],
    run_vdyp_fn: Callable[..., dict[Any, Any]],
    vdyp_out_cache: dict[Any, Any] | None = None,
    execute_bootstrap_vdyp_runs_fn: Callable[
        ..., dict[int, dict[str, dict[Any, Any]]]
    ] = execute_bootstrap_vdyp_runs,
) -> Callable[[], dict[int, dict[str, dict[Any, Any]]]]:
    """Build a zero-arg bootstrap callback for `load_or_build_vdyp_results_tsa(...)`."""

    def _run_bootstrap() -> dict[int, dict[str, dict[Any, Any]]]:
        return execute_bootstrap_vdyp_runs_fn(
            tsa=tsa,
            run_id=run_id,
            results_for_tsa=results_for_tsa,
            si_levels=si_levels,
            vdyp_run_events_path=vdyp_run_events_path,
            append_jsonl_fn=append_jsonl_fn,
            run_vdyp_fn=run_vdyp_fn,
            vdyp_out_cache=vdyp_out_cache,
        )

    return _run_bootstrap


def execute_vdyp_batch(
    *,
    feature_ids: Sequence[int],
    vdyp_ply: Any,
    vdyp_lyr: Any,
    vdyp_binpath: str,
    vdyp_params_infile: str,
    vdyp_io_dirname: str,
    vdyp_log_path: str | Path,
    vdyp_stdout_log_path: str | Path,
    vdyp_stderr_log_path: str | Path,
    phase: str,
    cache_hits: int = 0,
    timeout: int = 30,
    run_id: str | None = None,
    base_context: Mapping[str, Any] | None = None,
    write_vdyp_infiles: Callable[..., None] | None = None,
    import_vdyp_tables_fn: Callable[[str], dict[Any, Any]] | None = None,
    append_jsonl_fn: Callable[[str | Path, Any], None] | None = None,
    append_text_fn: Callable[[str | Path, str], None] | None = None,
    build_stream_header_fn: Callable[..., str] | None = None,
    build_stream_log_block_fn: Callable[..., str] | None = None,
    subprocess_run: Callable[..., Any] | None = None,
) -> dict[Any, Any]:
    """Run one VDYP batch and return parsed per-feature output tables."""
    feature_ids_list = list(feature_ids)
    if not feature_ids_list:
        return {}
    if write_vdyp_infiles is None:
        from femic.pipeline.vdyp_io import (
            write_vdyp_infiles_plylyr as write_vdyp_infiles,
        )
    if import_vdyp_tables_fn is None:
        from femic.pipeline.vdyp_io import import_vdyp_tables as import_vdyp_tables_fn
    if append_jsonl_fn is None:
        from femic.pipeline.vdyp_logging import append_jsonl as append_jsonl_fn
    if append_text_fn is None:
        from femic.pipeline.vdyp_logging import append_text as append_text_fn
    if build_stream_header_fn is None:
        from femic.pipeline.vdyp_logging import (
            build_vdyp_stream_header as build_stream_header_fn,
        )
    if build_stream_log_block_fn is None:
        from femic.pipeline.vdyp_logging import (
            build_vdyp_stream_log_block as build_stream_log_block_fn,
        )
    if subprocess_run is None:
        subprocess_run = subprocess.run

    write_vdyp_infiles_ = cast(Callable[..., None], write_vdyp_infiles)
    import_vdyp_tables_ = cast(Callable[[str], dict[Any, Any]], import_vdyp_tables_fn)
    append_jsonl_ = cast(Callable[[str | Path, Any], None], append_jsonl_fn)
    append_text_ = cast(Callable[[str | Path, str], None], append_text_fn)
    build_stream_header_ = cast(Callable[..., str], build_stream_header_fn)
    build_stream_log_block_ = cast(Callable[..., str], build_stream_log_block_fn)
    subprocess_run_ = cast(Callable[..., Any], subprocess_run)

    feature_count = len(feature_ids_list)
    vdyp_ply_ = vdyp_ply[vdyp_ply.FEATURE_ID.isin(feature_ids_list)]
    vdyp_lyr_ = vdyp_lyr[vdyp_lyr.FEATURE_ID.isin(feature_ids_list)]
    ply_rows = vdyp_ply_.shape[0]
    lyr_rows = vdyp_lyr_.shape[0]
    context = build_vdyp_run_context(
        base_context=base_context,
        run_id=run_id,
    )

    vdyp_io_dir = Path(vdyp_io_dirname)
    vdyp_io_dir.mkdir(parents=True, exist_ok=True)

    with (
        tempfile.NamedTemporaryFile(
            dir=vdyp_io_dir,
            prefix="vdyp_ply_",
            suffix=".csv",
            delete=False,
        ) as vdyp_ply_csv_,
        tempfile.NamedTemporaryFile(
            dir=vdyp_io_dir,
            prefix="vdyp_lyr_",
            suffix=".csv",
            delete=False,
        ) as vdyp_lyr_csv_,
        tempfile.NamedTemporaryFile(
            dir=vdyp_io_dir,
            prefix="vdyp_out_",
            suffix=".out",
            delete=False,
        ) as vdyp_out_txt_,
        tempfile.NamedTemporaryFile(
            dir=vdyp_io_dir,
            prefix="vdyp_err_",
            suffix=".err",
            delete=False,
        ) as vdyp_err_txt_,
    ):
        vdyp_ply_csv = Path(vdyp_ply_csv_.name).name
        vdyp_lyr_csv = Path(vdyp_lyr_csv_.name).name
        vdyp_out_txt = Path(vdyp_out_txt_.name).name
        vdyp_err_txt = Path(vdyp_err_txt_.name).name
        out_path = Path(vdyp_out_txt_.name)
        err_path = Path(vdyp_err_txt_.name)

        write_vdyp_infiles_(vdyp_ply_, vdyp_lyr_, vdyp_ply_csv, vdyp_lyr_csv)

        run_started = time.time()
        args = build_vdyp_batch_command(
            vdyp_binpath=vdyp_binpath,
            vdyp_params_infile=vdyp_params_infile,
            vdyp_io_dir=vdyp_io_dir,
            vdyp_ply_csv=vdyp_ply_csv,
            vdyp_lyr_csv=vdyp_lyr_csv,
            vdyp_out_txt=vdyp_out_txt,
            vdyp_err_txt=vdyp_err_txt,
        )
        try:
            result = subprocess_run_(
                shlex.split(args),
                timeout=timeout,
                capture_output=True,
                text=True,
            )
        except subprocess.TimeoutExpired as exc:
            append_jsonl_(
                vdyp_log_path,
                build_timestamped_event(
                    event="vdyp_run",
                    status="timeout",
                    phase=phase,
                    feature_count=int(feature_count),
                    cache_hits=int(cache_hits),
                    ply_rows=int(ply_rows),
                    lyr_rows=int(lyr_rows),
                    cmd=args,
                    timeout_sec=timeout,
                    error=str(exc),
                    context=context,
                ),
            )
            return {}
        except _subprocess_run_exception_types() as exc:
            append_jsonl_(
                vdyp_log_path,
                build_timestamped_event(
                    event="vdyp_run",
                    status="error",
                    phase=phase,
                    feature_count=int(feature_count),
                    cache_hits=int(cache_hits),
                    ply_rows=int(ply_rows),
                    lyr_rows=int(lyr_rows),
                    cmd=args,
                    error=str(exc),
                    traceback=traceback.format_exc(),
                    context=context,
                ),
            )
            return {}

        stream_header = build_stream_header_(
            phase=phase,
            feature_count=feature_count,
            cache_hits=int(cache_hits),
            cmd=args,
        )
        if result.stdout:
            append_text_(
                vdyp_stdout_log_path,
                build_stream_log_block_(
                    stream_header=stream_header,
                    stream_text=result.stdout,
                ),
            )
        if result.stderr:
            append_text_(
                vdyp_stderr_log_path,
                build_stream_log_block_(
                    stream_header=stream_header,
                    stream_text=result.stderr,
                ),
            )

        run_metadata = collect_vdyp_batch_run_metadata(
            result=result,
            out_path=out_path,
            err_path=err_path,
            run_started=run_started,
        )
        try:
            vdyp_out = import_vdyp_tables_(str(vdyp_io_dir / vdyp_out_txt))
        except _vdyp_parse_exception_types() as exc:
            append_jsonl_(
                vdyp_log_path,
                build_timestamped_event(
                    event="vdyp_run",
                    status="parse_error",
                    phase=phase,
                    feature_count=int(feature_count),
                    cache_hits=int(cache_hits),
                    ply_rows=int(ply_rows),
                    lyr_rows=int(lyr_rows),
                    cmd=args,
                    **run_metadata,
                    error=str(exc),
                    traceback=traceback.format_exc(),
                    context=context,
                ),
            )
            return {}

        append_jsonl_(
            vdyp_log_path,
            build_timestamped_event(
                event="vdyp_run",
                status="ok" if vdyp_out else "empty_output",
                phase=phase,
                feature_count=int(feature_count),
                cache_hits=int(cache_hits),
                ply_rows=int(ply_rows),
                lyr_rows=int(lyr_rows),
                cmd=args,
                **run_metadata,
                vdyp_out_tables=int(len(vdyp_out)),
                context=context,
            ),
        )
        return vdyp_out


def execute_curve_smoothing_runs(
    *,
    tsa: str,
    run_id: str,
    results_for_tsa: Sequence[tuple[int, str, Any]],
    si_levels: Sequence[str],
    vdyp_results_for_tsa: Mapping[int, Mapping[str, dict[Any, Any]]],
    kwarg_overrides_for_tsa: Mapping[tuple[str, str], Mapping[str, Any]],
    process_vdyp_out_fn: Callable[..., tuple[Sequence[float], Sequence[float]]],
    append_jsonl_fn: Callable[[str | Path, Any], None],
    vdyp_curve_events_path: str | Path,
    curve_fit_fn: Callable[..., Any],
    body_fit_func: Callable[..., Any],
    body_fit_func_bounds_func: Callable[..., Any],
    toe_fit_func: Callable[..., Any],
    toe_fit_func_bounds_func: Callable[..., Any],
    message_fn: Callable[..., Any] = print,
) -> list[SmoothedCurveResult]:
    """Build smoothed VDYP curves for each stratum/SI combination."""
    smoothed_runs: list[SmoothedCurveResult] = []
    for stratumi, sc, _result in results_for_tsa:
        for si_level in si_levels:
            kwargs = dict(kwarg_overrides_for_tsa.get((sc, si_level), {}))
            curve_context = {
                "run_id": run_id,
                "tsa": tsa,
                "stratum_index": int(stratumi),
                "stratum_code": sc,
                "si_level": si_level,
            }
            vdyp_out = vdyp_results_for_tsa.get(stratumi, {}).get(si_level)
            if not isinstance(vdyp_out, dict) or len(vdyp_out) == 0:
                message_fn("  missing vdyp results for", sc, si_level)
                append_jsonl_fn(
                    vdyp_curve_events_path,
                    build_timestamped_event(
                        event="vdyp_curve_fit",
                        status="warning",
                        stage="curve_input",
                        reason="missing_vdyp_output",
                        context=curve_context,
                    ),
                )
                continue
            x, y = process_vdyp_out_fn(
                vdyp_out,
                curve_fit_fn=curve_fit_fn,
                body_fit_func=body_fit_func,
                body_fit_func_bounds_func=body_fit_func_bounds_func,
                toe_fit_func=toe_fit_func,
                toe_fit_func_bounds_func=toe_fit_func_bounds_func,
                log_event=lambda payload: append_jsonl_fn(
                    vdyp_curve_events_path, payload
                ),
                message=message_fn,
                curve_context=curve_context,
                **kwargs,
            )
            smoothed_runs.append(
                SmoothedCurveResult(
                    stratumi=int(stratumi),
                    stratum_code=sc,
                    si_level=si_level,
                    x=x,
                    y=y,
                    vdyp_out=vdyp_out,
                )
            )
    return smoothed_runs
