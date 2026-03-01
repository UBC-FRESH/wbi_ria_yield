from __future__ import annotations

import numpy as np
import pandas as pd

from femic.pipeline.vdyp_sampling import nsamples_from_curves


def _fit_func(x: np.ndarray, a: float, b: float) -> np.ndarray:
    return a * x + b


def _fit_bounds(x: np.ndarray) -> tuple[list[float], list[float]]:
    _ = x
    return ([0.0, 0.0], [10.0, 10.0])


def _curve_fit_stub(func, x, y, bounds=None, maxfev=None):
    _ = (func, x, y, bounds, maxfev)
    return np.array([1.0, 0.0]), np.eye(2)


def test_nsamples_from_curves_empty_frames_returns_inf() -> None:
    nsamples, details = nsamples_from_curves(
        {1: pd.DataFrame()},
        curve_fit_fn=_curve_fit_stub,
        fit_func=_fit_func,
        fit_func_bounds_func=_fit_bounds,
        min_samples=1,
    )

    assert nsamples == np.inf
    assert details is None


def test_nsamples_from_curves_returns_finite_result() -> None:
    df = pd.DataFrame(
        {
            "Age": [30, 40, 50, 60, 70],
            "Vdwb": [50.0, 80.0, 100.0, 110.0, 115.0],
        }
    ).set_index("Age")

    nsamples, details = nsamples_from_curves(
        {1: df, 2: df * 1.05},
        curve_fit_fn=_curve_fit_stub,
        fit_func=_fit_func,
        fit_func_bounds_func=_fit_bounds,
        min_samples=1,
        window=2,
    )

    assert np.isfinite(nsamples)
    assert details is not None
