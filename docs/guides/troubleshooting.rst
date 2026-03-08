Troubleshooting and Recovery Cookbook
=====================================

Common Issues
-------------

BatchTIPSY input parsing errors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Likely causes:

- Fixed-width DAT misalignment
- Column-wizard mismatch versus previously validated settings
- Unsupported species/FIZ pairings

Recovery:

1. Keep wizard column mapping constant across runs.
2. Regenerate DAT from FEMIC with unchanged schema.
3. Apply species-code overrides in TSA YAML config where needed.

Sparse/unstable VDYP fits
^^^^^^^^^^^^^^^^^^^^^^^^^

Likely causes:

- Over-fragmented strata/SI bins
- Too-few stands in fit bins
- Outlier points driving NLLS behavior

Recovery:

1. Reduce stratification complexity for small areas.
2. Increase SI-bin collapse aggressiveness or merge bins.
3. Apply targeted fit overrides and compare diagnostics.

Unexpected cache/resume behavior
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Likely causes:

- Resume with stale checkpoints under changed run profile
- Debug-row mode interacting with cached artifacts

Recovery:

1. Use explicit run IDs per experiment.
2. Disable/clear relevant caches when run semantics changed.
3. Confirm manifest provenance and runtime parameters.

Docs/Pages visibility confusion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Likely causes:

- GitHub Pages source set to branch/Jekyll instead of Actions artifact
- Deploy job skipped by workflow ``if`` guard

Recovery:

1. Set Pages source to **GitHub Actions**.
2. Ensure deploy guard matches intended trigger (push/manual).
3. Re-run workflow and validate guide URLs directly.
