"""Reusable VDYP curve smoothing/fitting helpers."""

from __future__ import annotations

import importlib
from typing import Any, Callable
import traceback

import numpy as np

from femic.pipeline.diagnostics import build_timestamped_event

CurveFitFn = Callable[..., tuple[np.ndarray, Any]]
BoundsFn = Callable[[np.ndarray], tuple[Any, Any]]
EventLoggerFn = Callable[[dict[str, Any]], None]
MessageFn = Callable[[str], None]


def _curve_fit_fallback_exception_types() -> tuple[type[Exception], ...]:
    """Operational curve-fit/toe-fit failures that should trigger legacy fallback curves."""
    return (
        RuntimeError,
        ValueError,
        TypeError,
        OverflowError,
        FloatingPointError,
        np.linalg.LinAlgError,
    )


def legacy_fit_func1(
    x: np.ndarray, a: float, b: float, c: float, s: float
) -> np.ndarray:
    """Legacy body/toe fit function used in notebook-era curve smoothing."""
    return s * (a * ((x - c) ** b)) * np.exp(-a * (x - c))


def legacy_fit_func1_bounds_func(x: np.ndarray) -> tuple[list[float], list[float]]:
    """Bounds function for legacy_fit_func1 with c capped by min(x) and 100."""
    return ([0.000, 0, 0, 0], [1.00, 50, max(1, min(np.min(x), 100)), 10])


def legacy_fit_func2(x: np.ndarray, a: float, b: float) -> np.ndarray:
    """Legacy splice-fit function used for left-tail blending diagnostics."""
    return a * np.power(x, b) * np.power(x, -a)


def legacy_fit_func2_bounds_func(
    _x: np.ndarray,
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Bounds function for legacy_fit_func2."""
    return (0, 0), (10, 10)


def prepend_quasi_origin_point(
    x: np.ndarray | list[float],
    y: np.ndarray | list[float],
    *,
    age: float = 1.0,
    epsilon: float = 1e-6,
) -> tuple[np.ndarray, np.ndarray]:
    """Ensure curves are anchored at quasi-origin `(age, epsilon)`."""
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    if x_arr.size == 0:
        return np.array([age], dtype=float), np.array([epsilon], dtype=float)
    if x_arr[0] == age:
        y_out = y_arr.copy()
        y_out[0] = epsilon
        return x_arr, y_out
    return np.insert(x_arr, 0, age), np.insert(y_arr, 0, epsilon)


def fill_curve_left(
    x: np.ndarray,
    y: np.ndarray,
    *,
    curve_fit_fn: CurveFitFn,
    toe_fit_func: Callable[..., np.ndarray],
    toe_fit_func_bounds_func: BoundsFn,
    maxfev: int = 10000,
    skip: int = 10,
    dx: float = 0.0,
    di: int = 20,
    cy: float = 0.1,
) -> tuple[np.ndarray, np.ndarray, tuple[int, np.ndarray]]:
    """Fill left tail with a toe-fit curve and return fitted arrays plus toe metadata."""
    x_ = np.asarray(x, dtype=float).copy()
    y_ = np.asarray(y, dtype=float).copy()
    i1 = int(np.argmax(y_ > 0.0))
    x_fit = np.concatenate(([1 + dx, 2 + dx, 3 + dx], x_[i1 + skip : i1 + skip + di]))
    y_fit = np.concatenate(([1 * cy, 2 * cy, 3 * cy], y_[i1 + skip : i1 + skip + di]))
    bounds = toe_fit_func_bounds_func(x_fit)
    popt, _ = curve_fit_fn(toe_fit_func, x_fit, y_fit, maxfev=maxfev, bounds=bounds)
    y_[: i1 + skip] = toe_fit_func(x_[: i1 + skip], *popt)
    return x_, y_, (i1 + skip, np.asarray(popt, dtype=float))


def process_vdyp_out(
    vdyp_out: dict[Any, Any],
    *,
    curve_fit_fn: CurveFitFn,
    body_fit_func: Callable[..., np.ndarray],
    body_fit_func_bounds_func: BoundsFn,
    toe_fit_func: Callable[..., np.ndarray],
    toe_fit_func_bounds_func: BoundsFn,
    log_event: EventLoggerFn,
    message: MessageFn | None = None,
    curve_context: dict[str, Any] | None = None,
    volume_flavour: str = "Vdwb",
    min_age: int = 30,
    max_age: int = 300,
    sigma_c1: float = 10,
    sigma_c2: float = 0.4,
    dx_c1: float = 0.5,
    dx_c2: float = 10,
    window: int = 10,
    skip1: int = 0,
    skip2: int = 30,
    maxfev: int = 100000,
    max_skip_increase: int = 30,
    skip_step: int = 1,
) -> tuple[np.ndarray, np.ndarray]:
    """Build smoothed VDYP curve with toe splice and quasi-origin fallback behavior."""
    base_event = build_timestamped_event(
        event="vdyp_curve",
        context=dict(curve_context) if curve_context else {},
    )

    def emit(msg: str) -> None:
        if message is not None:
            message(msg)

    def fallback_curve(
        *,
        stage: str,
        reason: str,
        x_raw: np.ndarray | None = None,
        y_raw: np.ndarray | None = None,
        exc: Exception | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
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
        x_arr, y_arr = prepend_quasi_origin_point(x_arr, y_arr)
        payload: dict[str, Any] = {
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
        log_event(payload)
        return x_arr, y_arr

    pd_mod = importlib.import_module("pandas")
    vdyp_tables = [v for v in vdyp_out.values() if isinstance(v, pd_mod.DataFrame)]
    if not vdyp_tables:
        return fallback_curve(stage="preflight", reason="empty_vdyp_out")

    vdyp_out_concat = pd_mod.concat(vdyp_tables)
    c_all = vdyp_out_concat.groupby(level="Age")[volume_flavour].median()
    c_all = c_all[c_all > 0]
    c = c_all[c_all.index >= min_age]
    if c.empty:
        return fallback_curve(
            stage="body_input",
            reason="no_points_after_min_age_filter",
            x_raw=c_all.index.values,
            y_raw=c_all.values,
        )

    x = c.index.values
    y = c.rolling(window=window, center=True).median().values
    x, y = x[y > 0], y[y > 0]
    x, y = x[skip1:], y[skip1:]
    if len(x) < 4 or len(y) < 4:
        return fallback_curve(
            stage="body_input",
            reason="insufficient_points_after_smoothing",
            x_raw=c.index.values,
            y_raw=c.values,
        )

    y_mai = pd_mod.Series(y / x, x)
    if y_mai.empty:
        return fallback_curve(
            stage="body_input",
            reason="empty_mai_series",
            x_raw=c.index.values,
            y_raw=c.values,
        )

    y_mai_max_age = y_mai.idxmax()
    sigma = (np.abs(x - y_mai_max_age) + sigma_c1) ** sigma_c2
    try:
        popt, _ = curve_fit_fn(
            body_fit_func,
            x,
            y,
            bounds=body_fit_func_bounds_func(x),
            maxfev=maxfev,
            sigma=sigma,
        )
    except _curve_fit_fallback_exception_types() as exc:
        log_event(
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
            }
        )
        return fallback_curve(
            stage="body_fit_fallback",
            reason="body_fit_exception",
            x_raw=x,
            y_raw=y,
            exc=exc,
        )

    x = np.array(range(1, max_age), dtype=float)
    y = body_fit_func(x, *popt)
    dx = max(0, dx_c1 * float(popt[2]) - dx_c2)
    emit(str(dx))
    used_skip: int | None = None
    last_exc: Exception | None = None
    for extra in range(0, max_skip_increase + 1, skip_step):
        try:
            x_, y_, (_, popt_toe) = fill_curve_left(
                x.copy(),
                y.copy(),
                curve_fit_fn=curve_fit_fn,
                toe_fit_func=toe_fit_func,
                toe_fit_func_bounds_func=toe_fit_func_bounds_func,
                skip=skip2 + extra,
                dx=dx,
                maxfev=maxfev,
            )
            used_skip = skip2 + extra
            if used_skip != skip2:
                emit(f"vdyp toe fit: increased skip to {used_skip}")
            emit(str(popt_toe))
            x_, y_ = prepend_quasi_origin_point(x_, y_)
            log_event(
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
                }
            )
            return x_, y_
        except _curve_fit_fallback_exception_types() as exc:
            last_exc = exc
            continue

    log_event(
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
        }
    )
    emit(
        "vdyp toe fit failed; returning body fit curve with quasi-origin "
        "(1, epsilon) anchor"
    )
    x, y = prepend_quasi_origin_point(x, y)
    log_event(
        {
            **base_event,
            "event": "vdyp_curve_anchor",
            "status": "warning",
            "stage": "quasi_origin_anchor",
            "first_age": float(x[0]),
            "first_volume": float(y[0]),
        }
    )
    return x, y
