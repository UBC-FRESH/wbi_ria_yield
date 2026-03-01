# VDYP Debug Notes

## Why a stratum+SI can be "missing" even when VRI says it exists
A stratum+SI can be valid in VRI-derived rows but still absent from VDYP curve outputs. In this
pipeline, "missing" means the stratum+SI never appears in `vdyp_curves_smooth` (so no AU mapping
is created), not that the VRI record is invalid.

Key points from the prior explanation:
- VDYP curves are built from VDYP outputs and then filtered; `scsi_au` only contains strata found
  in `vdyp_curves_smooth`.
- A stratum can be skipped entirely if it is not present in the VDYP curve outputs for that TSA.
- A stratum can exist but be missing specific SI-level curves; the lookup for `sc, si_level` can
  fail and get skipped.
- Curves can be dropped after VDYP runs due to post-processing filters (operability window,
  minimum volume thresholds, etc.), leaving no curve to map.
- Resume/caching can lock in prior gaps: if cached VDYP outputs lacked a stratum+SI, the pipeline
  continues to treat it as missing.
- Upstream filtering can empty a bin even at 100% sampling because of null site index, invalid
  species codes, or other filters.

Recommended diagnostic: produce a per-TSA diff of
- VRI `stratum_matched` + `si_level` combos
- VDYP curve combos
- the set difference with counts and any detected reasons

## Fragility hot spots (user-provided)
- VDYP execution under Wine is fragile; it depends on correct parameter sets, install files, and
  tmp-file creation. We need sanity checks that pinpoint failures rather than silent exits.
- Curve compression + NLLS fit can fail if binning or convergence fails; when it does, there is
  no curve for that AU and we currently lack detailed diagnostics.
- The exponential ramp splice can fail if the left edge of the NLLS curve has a shape that cannot
  match slopes; this likely needs automated detection and iterative left-point trimming with a
  warning if a tolerance is exceeded.
