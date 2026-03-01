# wbi_ria_yield

[![DOI](https://zenodo.org/badge/430531073.svg)](https://zenodo.org/badge/latestdoi/430531073)

## CLI

Run the legacy pipeline through the FEMIC CLI:

```bash
femic run --tsa 08 --resume
```

`femic run` executes the legacy script in an isolated subprocess and filters known
non-fatal shutdown noise lines from legacy stderr output.
Each run writes a manifest at `vdyp_io/logs/run_manifest-<run_id>.json` and uses
run-scoped VDYP log files (per TSA + run id).
For each TSA, raw VDYP process streams are also captured to:
`vdyp_io/logs/vdyp_stdout-tsa<tsa>-<run_id>.log` and
`vdyp_io/logs/vdyp_stderr-tsa<tsa>-<run_id>.log`.

For faster debugging, limit the number of VRI rows processed (this disables cached checkpoints
and output reuse):

```bash
femic run --tsa 08 --resume --debug-rows 1000
```

You can override run metadata/log routing:

```bash
femic run --tsa 08 --resume --run-id mytest01 --log-dir vdyp_io/logs
```

If `--tsa` is omitted, defaults are loaded from `config/dev.toml` (`[run].default_tsa_list`).

Note: In debug mode, some strata may lack VDYP curves. These are skipped with a warning.
Rows whose strata do not map to an AU/curve (missing VDYP curves) are dropped with a warning
summary.
Debug mode also skips final TSA stand shapefile export by default; set
`FEMIC_SKIP_STANDS_SHP=0` to force shapefile output while debugging.
`ipyparallel` is disabled by default (`FEMIC_DISABLE_IPP=1`) for stability;
set `FEMIC_DISABLE_IPP=0` to re-enable controller-backed execution.
Row-wise operations default to pandas `.apply(...)`; set `FEMIC_USE_SWIFTER=1`
to opt back into swifter acceleration.

VDYP diagnostics are written to `vdyp_io/logs/` as JSONL files (e.g.,
`vdyp_runs.jsonl`, `vdyp_curve_events.jsonl`) to capture run status and curve-fit
warnings.
Summarize these logs with:

```bash
femic vdyp report
```

For regression checks in CI, apply warning-budget thresholds (command exits non-zero on breach):

```bash
femic vdyp report --max-curve-warnings 2 --max-first-point-mismatches 0 --min-curve-events 5 --min-run-events 6
```

Yield curves are anchored to a quasi-origin point `(1, 1e-6)` so downstream positive-value
filters can remain unchanged while avoiding zero-age intercept issues.

Raw BC datasets are expected under `../data` relative to the repo root (e.g.,
`../data/bc/vri/2019/VEG_COMP_LYR_R1_POLY.gdb`). You can override this by setting
`FEMIC_EXTERNAL_DATA_ROOT` to a different base path.
