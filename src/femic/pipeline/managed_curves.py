"""Managed-curve synthesis helpers."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd


def synthesize_managed_curve_from_vdyp(
    *,
    vdyp_curve: Any,
    x_scale: float = 0.8,
    y_scale: float = 1.2,
    max_age: int = 300,
    truncate_after_culmination: bool = True,
    pd_module: Any = pd,
    np_module: Any = np,
) -> Any:
    """Build a synthetic managed curve by transforming a VDYP unmanaged curve."""
    frame = vdyp_curve.copy()
    if frame.empty:
        return pd_module.DataFrame(columns=["Age", "Yield"])

    work = frame[["age", "volume"]].copy()
    work["age"] = pd_module.to_numeric(work["age"], errors="coerce")
    work["volume"] = pd_module.to_numeric(work["volume"], errors="coerce")
    work = work.dropna(subset=["age", "volume"]).sort_values("age")
    work = work[work["age"] > 0]
    if work.empty:
        return pd_module.DataFrame(columns=["Age", "Yield"])

    scaled_age = (work["age"].astype(float) * float(x_scale)).round().astype(int)
    scaled_age = scaled_age.clip(lower=1, upper=int(max_age))
    scaled_yield = work["volume"].astype(float) * float(y_scale)
    scaled = pd_module.DataFrame({"Age": scaled_age, "Yield": scaled_yield})
    scaled = scaled.groupby("Age", as_index=False)["Yield"].max().sort_values("Age")
    if scaled.empty:
        return pd_module.DataFrame(columns=["Age", "Yield"])

    all_ages = np_module.arange(1, int(max_age) + 1, dtype=int)
    x = scaled["Age"].to_numpy(dtype=float)
    y = scaled["Yield"].to_numpy(dtype=float)
    y_interp = np_module.interp(all_ages.astype(float), x, y, left=y[0], right=y[-1])
    y_interp = np_module.maximum(y_interp, 0.0)
    if truncate_after_culmination and y_interp.size > 0:
        culm_idx = int(np_module.argmax(y_interp))
        y_interp[culm_idx:] = y_interp[culm_idx]
    return pd_module.DataFrame({"Age": all_ages, "Yield": y_interp})


def build_transformed_managed_curves_for_tsa(
    *,
    tsa: str,
    au_values: list[int],
    au_scsi: Mapping[str, Mapping[int, tuple[str, str]]],
    vdyp_curves_by_scsi: Any,
    x_scale: float,
    y_scale: float,
    max_age: int,
    truncate_after_culmination: bool,
    pd_module: Any = pd,
) -> Any:
    """Generate transformed managed curves for all AUs in one TSA."""
    rows: list[dict[str, Any]] = []
    au_map = au_scsi.get(tsa, {})
    for au in sorted({int(v) for v in au_values}):
        au_base = int(str(au)[-4:])
        scsi = au_map.get(au_base)
        if scsi is None:
            continue
        stratum_code, si_level = scsi
        try:
            vdyp_curve = vdyp_curves_by_scsi.loc[stratum_code, si_level]
        except KeyError:
            continue
        if not hasattr(vdyp_curve, "columns") and hasattr(vdyp_curve, "to_frame"):
            vdyp_curve = vdyp_curve.to_frame().T
        managed_curve = synthesize_managed_curve_from_vdyp(
            vdyp_curve=vdyp_curve,
            x_scale=x_scale,
            y_scale=y_scale,
            max_age=max_age,
            truncate_after_culmination=truncate_after_culmination,
            pd_module=pd_module,
        )
        for age, yield_ in zip(managed_curve["Age"], managed_curve["Yield"]):
            rows.append(
                {
                    "AU": int(au),
                    "Age": int(age),
                    "Yield": float(yield_),
                    "Height": np.nan,
                    "DBHq": np.nan,
                    "TPH": np.nan,
                }
            )
    out = pd_module.DataFrame(rows)
    if out.empty:
        return pd_module.DataFrame(
            columns=["AU", "Age", "Yield", "Height", "DBHq", "TPH"]
        )
    return out.sort_values(["AU", "Age"]).reset_index(drop=True)
