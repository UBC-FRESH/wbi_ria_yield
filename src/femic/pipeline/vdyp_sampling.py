"""VDYP sample-size estimation helpers extracted from legacy runner."""

from __future__ import annotations

import importlib
from typing import Any, Callable

import numpy as np


def nsamples_from_curves(
    vdyp_out: dict[Any, Any],
    *,
    curve_fit_fn: Callable[..., tuple[np.ndarray, np.ndarray]],
    fit_func: Callable[..., np.ndarray],
    fit_func_bounds_func: Callable[[np.ndarray], Any],
    col: str = "Vdwb",
    maxfev: int = 10_000,
    confidence: int = 95,
    half_rel_ci: float = 0.01,
    window: int = 30,
    min_samples: int = 10,
    max_samples: int = 1000,
) -> tuple[float, tuple[float, float, float, float] | None]:
    """Estimate target sample size from current VDYP output curves."""
    if len(vdyp_out) < min_samples:
        return np.inf, None

    pd = importlib.import_module("pandas")
    z = {95: 1.96}[confidence]
    dataframe_type = pd.core.frame.DataFrame
    frames = [
        v for v in vdyp_out.values() if isinstance(v, dataframe_type) and not v.empty
    ]
    if not frames:
        return np.inf, None

    vdyp_out_concat = pd.concat(frames)
    c = vdyp_out_concat.groupby(level="Age")[col].median()
    c = c[c > 0]
    c = c[c.index >= 30]
    x = c.index.values
    y = c.rolling(window=window).median().values
    x, y = x[y > 0], y[y > 0]
    if len(x) == 0 or len(y) == 0:
        return np.inf, None

    popt, _ = curve_fit_fn(
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
