from __future__ import annotations

from typing import Any, Callable

import numpy as np
import pandas as pd
import pytest

from femic.pipeline.vdyp_curves import (
    legacy_fit_func1,
    legacy_fit_func1_bounds_func,
    legacy_fit_func2,
    legacy_fit_func2_bounds_func,
    prepend_quasi_origin_point,
    process_vdyp_out,
)


def _fit_func1(x: np.ndarray, a: float, b: float, c: float, s: float) -> np.ndarray:
    return s * (a * ((x - c) ** b)) * np.exp(-a * (x - c))


def _fit_bounds(_x: np.ndarray) -> tuple[list[float], list[float]]:
    return ([0.0, 0.0, 0.0, 0.0], [1.0, 50.0, 100.0, 10.0])


def test_prepend_quasi_origin_point_inserts_first_point() -> None:
    x, y = prepend_quasi_origin_point(np.array([10.0, 20.0]), np.array([5.0, 8.0]))
    assert x[0] == 1.0
    assert y[0] == 1e-6


def test_legacy_fit_func1_bounds_caps_c_parameter() -> None:
    values = legacy_fit_func1(np.array([5.0]), 0.5, 2.0, 1.0, 3.0)
    assert values.shape == (1,)
    lower, upper = legacy_fit_func1_bounds_func(np.array([25.0, 40.0]))
    assert lower == [0.0, 0, 0, 0]
    assert upper == [1.0, 50, 25.0, 10]


def test_legacy_fit_func2_and_bounds_behavior() -> None:
    out = legacy_fit_func2(np.array([2.0, 4.0]), 2.0, 3.0)
    assert out.tolist() == [4.0, 8.0]
    assert legacy_fit_func2_bounds_func(np.array([1.0])) == ((0, 0), (10, 10))


def test_process_vdyp_out_empty_input_returns_quasi_anchor() -> None:
    events: list[dict[str, Any]] = []
    x, y = process_vdyp_out(
        {},
        curve_fit_fn=lambda *args, **kwargs: (np.array([0.1, 1.0, 1.0, 1.0]), None),
        body_fit_func=_fit_func1,
        body_fit_func_bounds_func=_fit_bounds,
        toe_fit_func=_fit_func1,
        toe_fit_func_bounds_func=_fit_bounds,
        log_event=events.append,
    )
    assert x.tolist() == [1.0]
    assert y.tolist() == [1e-6]
    assert events[-1]["stage"] == "preflight"
    assert events[-1]["reason"] == "empty_vdyp_out"


def test_process_vdyp_out_toe_failure_falls_back_to_quasi_origin() -> None:
    ages = np.array([30, 40, 50, 60, 70, 80], dtype=float)
    vols = np.array([30, 80, 140, 190, 220, 240], dtype=float)
    vdyp_df = pd.DataFrame({"Age": ages, "Vdwb": vols}).set_index("Age")
    events: list[dict[str, Any]] = []

    def curve_fit_stub(
        func: Callable[..., np.ndarray], x: np.ndarray, y: np.ndarray, **kwargs: Any
    ) -> tuple[np.ndarray, Any]:
        _ = (x, y, kwargs)
        if func is _fit_func1:
            # Body fit succeeds.
            return np.array([0.04, 2.0, 12.0, 7.0]), None
        raise RuntimeError("unexpected function")

    def toe_fail(*args: Any, **kwargs: Any) -> np.ndarray:
        _ = (args, kwargs)
        raise RuntimeError("toe failed")

    x, y = process_vdyp_out(
        {1: vdyp_df},
        curve_fit_fn=curve_fit_stub,
        body_fit_func=_fit_func1,
        body_fit_func_bounds_func=_fit_bounds,
        toe_fit_func=toe_fail,
        toe_fit_func_bounds_func=lambda _: ([0.0], [1.0]),
        log_event=events.append,
        min_age=30,
        max_age=90,
        window=2,
        max_skip_increase=2,
    )
    assert x[0] == 1.0
    assert y[0] == 1e-6
    stages = {event["stage"] for event in events}
    assert "toe_fit" in stages
    assert "quasi_origin_anchor" in stages


def test_process_vdyp_out_body_fit_runtime_error_falls_back() -> None:
    ages = np.array([30, 40, 50, 60, 70, 80], dtype=float)
    vols = np.array([30, 80, 140, 190, 220, 240], dtype=float)
    vdyp_df = pd.DataFrame({"Age": ages, "Vdwb": vols}).set_index("Age")
    events: list[dict[str, Any]] = []

    def _body_fit_raises(*args: Any, **kwargs: Any) -> tuple[np.ndarray, Any]:
        _ = (args, kwargs)
        raise RuntimeError("curve fit failed")

    x, y = process_vdyp_out(
        {1: vdyp_df},
        curve_fit_fn=_body_fit_raises,
        body_fit_func=_fit_func1,
        body_fit_func_bounds_func=_fit_bounds,
        toe_fit_func=_fit_func1,
        toe_fit_func_bounds_func=_fit_bounds,
        log_event=events.append,
        min_age=30,
        max_age=90,
        window=2,
    )

    assert x[0] == 1.0
    assert y[0] == 1e-6
    stages = {event["stage"] for event in events}
    assert "body_fit" in stages
    assert "body_fit_fallback" in stages


def test_process_vdyp_out_unexpected_body_fit_error_propagates() -> None:
    ages = np.array([30, 40, 50, 60, 70, 80], dtype=float)
    vols = np.array([30, 80, 140, 190, 220, 240], dtype=float)
    vdyp_df = pd.DataFrame({"Age": ages, "Vdwb": vols}).set_index("Age")

    def _body_fit_unexpected(*args: Any, **kwargs: Any) -> tuple[np.ndarray, Any]:
        _ = (args, kwargs)
        raise ZeroDivisionError("unexpected")

    with pytest.raises(ZeroDivisionError):
        process_vdyp_out(
            {1: vdyp_df},
            curve_fit_fn=_body_fit_unexpected,
            body_fit_func=_fit_func1,
            body_fit_func_bounds_func=_fit_bounds,
            toe_fit_func=_fit_func1,
            toe_fit_func_bounds_func=_fit_bounds,
            log_event=lambda _event: None,
            min_age=30,
            max_age=90,
            window=2,
        )


def test_process_vdyp_out_unexpected_toe_fit_error_propagates() -> None:
    ages = np.array([30, 40, 50, 60, 70, 80], dtype=float)
    vols = np.array([30, 80, 140, 190, 220, 240], dtype=float)
    vdyp_df = pd.DataFrame({"Age": ages, "Vdwb": vols}).set_index("Age")

    def _curve_fit_stub(
        func: Callable[..., np.ndarray], x: np.ndarray, y: np.ndarray, **kwargs: Any
    ) -> tuple[np.ndarray, Any]:
        _ = (func, x, y, kwargs)
        return np.array([0.04, 2.0, 12.0, 7.0]), None

    def _toe_unexpected(*args: Any, **kwargs: Any) -> np.ndarray:
        _ = (args, kwargs)
        raise ZeroDivisionError("unexpected toe")

    with pytest.raises(ZeroDivisionError):
        process_vdyp_out(
            {1: vdyp_df},
            curve_fit_fn=_curve_fit_stub,
            body_fit_func=_fit_func1,
            body_fit_func_bounds_func=_fit_bounds,
            toe_fit_func=_toe_unexpected,
            toe_fit_func_bounds_func=lambda _: ([0.0], [1.0]),
            log_event=lambda _event: None,
            min_age=30,
            max_age=90,
            window=2,
            max_skip_increase=2,
        )
