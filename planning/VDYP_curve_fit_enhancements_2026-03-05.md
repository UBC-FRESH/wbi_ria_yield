# VDYP Curve-Fit Enhancement Summary (TSA29/K3Z) - 2026-03-05

## Why this work was done
- Baseline VDYP smoothing occasionally produced pathological curves (for example AU 21005 spike).
- Even after targeted `skip1` overrides, many fitted curves failed to represent late-age behavior:
  observed binned medians often flatten near age 200-300, while fitted curves remained too curved.
- Goal: preserve robust baseline fitting while adding a defensible tail-treatment workflow that can
  better represent late-age near-linear decline/plateau patterns.

## High-level changes implemented

### 1) Baseline hardening
- Added TSA29 override in [`src/femic/pipeline/vdyp_overrides.py`](../src/femic/pipeline/vdyp_overrides.py):
  - `("SBPS_PL", "L") -> {"skip1": 50}`.
- Result: removed AU 21005 early-age pathological spike and restored coherent trajectory.

### 2) Fit diagnostics as first-class output
- Added per-stratum/SI diagnostic plots in
  [`src/femic/pipeline/vdyp_stage.py`](../src/femic/pipeline/vdyp_stage.py):
  - output pattern: `plots/vdyp_fitdiag_tsaXX-<stratumi>-<stratum>-<si>.png`.
  - includes observed binned median/P25/P75, fitted curve(s), and metric text overlays.
- Added candidate comparison workflow in diagnostics:
  - current fit
  - tail-blend candidate
  - auto-skip candidate (accepted only if quality gates improve baseline).

### 3) Tail blend algorithm evolution
- Introduced right-tail blend path in
  [`src/femic/pipeline/vdyp_curves.py`](../src/femic/pipeline/vdyp_curves.py).
- Iteration sequence:
  1. Quantile-anchored tail blending (too permissive in some non-linear tails).
  2. Linear-tail detection with quality gates (`R^2`, normalized RMSE).
  3. Removed early-anchor failure mode by requiring late-age candidates.
  4. Relaxed linearity thresholds to capture additional "obvious" near-linear tails.

## Current tail-blend logic (as of this note)
- For each curve, detect rightmost linear candidate tail from binned data using:
  - minimum points: `tail_linear_min_points`
  - linearity gate: `tail_linear_min_r2`
  - fit-error gate: `tail_linear_max_nrmse`
  - late-age preference gate: `tail_linear_prefer_min_age`
- If no acceptable late-age candidate is found:
  - no tail override is applied (fall back to current fit).
- If a candidate is found:
  - fit current NLLS body as usual
  - construct linear tail from detected segment
  - blend body -> tail over `tail_blend_years`.

## Stage-level hyperparameters currently used for diagnostic candidate runs
- In [`src/femic/pipeline/vdyp_stage.py`](../src/femic/pipeline/vdyp_stage.py):
  - `tail_linear_min_points = 4`
  - `tail_linear_min_r2 = 0.82`
  - `tail_linear_max_nrmse = 0.12`
  - `tail_linear_prefer_min_age = 190.0`
  - `tail_linear_allow_quantile_fallback = False`
  - `tail_blend_years = 30.0`

## Auto-skip enhancement status
- Added heuristic detection for early-age "wacky" overshoot:
  - infer suggested `skip1` from early quantile overshoot ratio.
- Candidate auto-skip is accepted only if all gates pass:
  - RMSE improvement
  - tail-RMSE non-worsening
  - early-overshoot non-worsening.
- On TSA29 this remains conservative; many suggestions are rejected by gates.

## Metrics snapshots observed during this iteration
- Initial candidate-comparison run (current/tail/sigma):
  - showed directionally useful information but exposed bad tail selection cases.
- After strict late-age gating:
  - catastrophic tail-blend failures removed.
- After relaxed late-tail detection:
  - more tails captured (blended tails increased from 22/30 to 26/30 on TSA29),
  - but with moderate tradeoff in a few curves.
- Most recent tail-only summary artifact:
  - `plots/vdyp_fitdiag_tsa29_metrics_tail_only.csv`.

## New plotting enhancement for lecture/demo use
- Fit diagnostics now include raw VDYP sample curves as fine low-alpha grey lines:
  - plotted from per-sample VDYP outputs (`Age` vs `Vdwb`) before aggregation/smoothing.
  - intent: visibly show lifecycle from raw model outputs -> binned summaries -> final fitted curve.

## Files touched in this enhancement stream
- `src/femic/pipeline/vdyp_curves.py`
- `src/femic/pipeline/vdyp_stage.py`
- `src/femic/pipeline/vdyp_overrides.py`
- `tests/test_vdyp_curves.py`
- `tests/test_vdyp_stage.py`
- `tests/test_vdyp_overrides.py`
- `plots/vdyp_fitdiag_tsa29-*.png`
- `plots/vdyp_fitdiag_tsa29_metrics_tail_only.csv`

## Remaining tuning work (explicit TODO)
- Continue tuning tail-fit hyperparameters (especially linearity thresholds and late-age preference)
  to better capture "obvious" long near-linear tails without introducing regressions:
  - tune `tail_linear_min_r2`
  - tune `tail_linear_max_nrmse`
  - tune `tail_linear_prefer_min_age`
  - possibly add a minimum accepted tail duration (years) and/or per-curve acceptance gate
    (accept blend only if tail-RMSE does not degrade beyond tolerance).
