from __future__ import annotations

import pandas as pd

from femic.pipeline.managed_curves import synthesize_managed_curve_from_vdyp


def test_synthesize_managed_curve_from_vdyp_applies_scale_and_truncate() -> None:
    vdyp_curve = pd.DataFrame(
        {
            "age": [1, 50, 100, 150, 200, 250, 300],
            "volume": [1.0, 120.0, 220.0, 260.0, 240.0, 220.0, 200.0],
        }
    )
    out = synthesize_managed_curve_from_vdyp(
        vdyp_curve=vdyp_curve,
        x_scale=0.8,
        y_scale=1.2,
        max_age=300,
        truncate_after_culmination=True,
    )
    assert not out.empty
    assert int(out["Age"].min()) == 1
    assert int(out["Age"].max()) == 300
    # x_scale=0.8 should shift culmination left; y_scale=1.2 should increase magnitudes.
    peak_age = int(out.loc[out["Yield"].idxmax(), "Age"])
    assert peak_age < 150
    assert float(out["Yield"].max()) > 260.0
    # Truncation should prevent decline after culmination.
    tail = out[out["Age"] >= peak_age]["Yield"]
    assert float(tail.min()) == float(tail.max())
