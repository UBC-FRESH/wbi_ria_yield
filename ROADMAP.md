# Refactor Roadmap

## Phase 1: Stabilize Runtime + Inputs
- [ ] P1.1 Stand up Typer CLI entrypoint (FHOPS-style, nemora-compatible)
- [ ] P1.1a Expose the `femic` console script (Forest Estate Model Input Compiler)
- [ ] P1.1b Create `src/femic/cli/main.py` with `Typer(add_completion=False, no_args_is_help=True)`
- [ ] P1.1c Organize subcommands (prep, vdyp, tsa, run) via `app.add_typer(...)`
- [ ] P1.1d Use module-level constants for defaults + typed `Path` args (avoid B008)
- [ ] P1.2 Define a single entrypoint script with explicit CLI args
- [ ] P1.2a Add a `--tsa` filter and `--resume` flag
- [ ] P1.2b Centralize environment checks (VDYP, wine, data paths)
- [ ] P1.3 Normalize I/O paths and required files
- [ ] P1.3a Document expected data layout under `data/` and `vdyp_io/`
- [ ] P1.3b Add validation for missing files before processing
- [ ] P1.4 Improve logging and error visibility
- [ ] P1.4a Add structured logging with per-TSA context
- [ ] P1.4b Capture external tool stderr/stdout to files
- [ ] P1.5 VDYP diagnostics + metadata hardening
- [ ] P1.5a Add VDYP Wine wrapper health checks (config, inputs, tmp outputs,
  exit codes)
- [ ] P1.5b Record VDYP run metadata + failure reasons per TSA and AU
- [ ] P1.5c Add curve-build diagnostics (binning stats, NLLS convergence,
  residuals)
- [ ] P1.5d Add ramp-splice diagnostics and iterative left-point trimming with warnings

## Phase 2: Modularize Pipeline Steps
- [ ] P2.1 Extract reusable modules from `00_data-prep.py`
- [ ] P2.1a Split into `io.py`, `vdyp.py`, `tsa.py`, `plots.py`
- [ ] P2.1b Remove global state and pass explicit parameters
- [ ] P2.2 Convert notebook logic into functions
- [ ] P2.2a Wrap major steps with clear inputs/outputs
- [ ] P2.2b Add a small orchestration layer for sequencing
- [ ] P2.3 Add minimal tests for core helpers
- [ ] P2.3a Smoke tests for file validation and key transforms
- [ ] P2.3b Deterministic checks for small sample data

## Phase 3: Workflow Hardening
- [ ] P3.1 Sphinx docs + GitHub Pages (FHOPS-style)
- [ ] P3.1a Add `docs/conf.py` with `sphinx_rtd_theme`, `nbsphinx`, `autosummary`
- [ ] P3.1b Add `docs/index.rst` + `docs/reference/cli.rst` mirroring CLI help
- [ ] P3.1c Add GitHub Pages workflow to build + publish `docs/_build/html`
- [ ] P3.2 Nemora alignment prep
- [ ] P3.2a Map femic CLI commands to nemora task taxonomy
- [ ] P3.2b Identify shared utilities to upstream into nemora later
- [ ] P3.3 Add config-driven runs
- [ ] P3.3a YAML/JSON config to select TSA, strata, and modes
- [ ] P3.3b Store run metadata and versioned outputs
- [ ] P3.4 Make outputs reproducible
- [ ] P3.4a Seed randomness in bootstrap/sample paths
- [ ] P3.4b Record tool versions and runtime parameters
- [ ] P3.5 Documentation + handoff
- [ ] P3.5a Update README with new workflow
- [ ] P3.5b Add a quickstart for running end-to-end

## Next Focus
- [x] NF1 Make the `femic` CLI runnable in the current venv
- [x] NF1a Ensure `typer` and `rich` are installed (`pip install -r requirements.txt`)
- [x] NF1b Add a console script entrypoint in packaging (so `femic --help` works)
- [x] NF2 Wire `femic run` to the existing pipeline
- [x] NF2a Execute `00_data-prep.py` through a controlled wrapper subprocess
- [x] NF2b Plumb `--tsa` and `--resume` into the current control flow
- [x] NF3 Add preflight checks for external dependencies
- [x] NF3a Verify `wine` availability and `VDYP7/VDYP7/VDYP7Console.exe` path
- [x] NF3b Verify `vdyp_io/VDYP_CFG` and required input files under `data/`
- [x] NF4 Add minimal run metadata + logging
- [ ] NF4a Emit per-TSA log files and capture full VDYP stdout/stderr artifacts
- [ ] NF4b Write a run manifest (timestamp, TSA list, paths, versions)
- [x] NF5 Quick README update for femic usage
- [x] NF5a Add a 5-minute “run the pipeline” quickstart
- [x] NF6 VDYP debug + metadata dive to reduce late-stage failures
- [x] NF6a Add VDYP wrapper sanity checks and per-run diagnostics
- [x] NF6b Add curve-binning and NLLS convergence metadata outputs
- [x] NF6c Add ramp-splice auto-trimming and warning thresholds
- [x] NF7 Promote debug metadata into operator-facing run artifacts
- [x] NF7a Persist per-run manifest JSON (env flags, debug_rows, checkpoints used)
- [x] NF7b Split `vdyp_*` JSONL logs by TSA/run-id and retain rolling history
- [x] NF7c Add `femic run --log-dir` and `femic run --run-id` overrides
- [ ] NF8 Add deterministic regression harness for TSA08 debug profile
- [ ] NF8a Add smoke assertion over `femic vdyp report` summary counts
- [ ] NF8b Add guardrails for warning-budget thresholds (fail on unexpected growth)

## Detailed Next Steps Notes
- `PYTHONPATH=src python -m femic --help` now works in the venv.
- `pyproject.toml` defines the `femic` console script; install with `pip install -e .` when ready.
- Added a legacy workflow wrapper that runs `00_data-prep.py` and honors `--tsa`/`--resume`.
- `femic run` now performs preflight checks (use `--skip-checks` to bypass).
- Legacy bundle handling now targets `data/model_input_bundle` only (no legacy auto-copy).
- Removed legacy `data/spadescbm_bundle` directory.
- Normalized `tsa_code`/`tsa` to zero-padded strings to prevent resume-time index mismatches.
- Added a guard that fails fast with a summary when AU assignment yields zero rows.
- Rebuilds `scsi_au` from `au_table` when resuming so curve assignment can proceed.
- Added a `--debug-rows` CLI option to downsample VRI rows for faster iteration.
- Debug row limiting now re-applies after checkpoint reloads to avoid full-size fallbacks.
- Fixed debug row helper ordering so checkpoint loads can call it safely.
- Skips strata lacking VDYP curves to avoid debug-run crashes.
- Debug runs now disable cached checkpoint and output reuse.
- External dataset paths now resolve relative to repo root (`../data`).
- Added external data root override via `FEMIC_EXTERNAL_DATA_ROOT`.
- Fixed raster masking calls to wrap geometries in lists (rasterio expects iterables).
- AU/curve assignment now tolerates missing stratum+SI mappings and logs a warning summary before
  dropping unmapped rows.
- Added `planning/VDYP_debug_notes.md` and queued a VDYP diagnostics + metadata
  hardening focus.
- Added VDYP run and curve-fit diagnostics logs plus toe-fit auto-trimming with warnings to keep
  the pipeline moving while recording failures.
- Updated curve anchoring to quasi-origin `(1, 1e-6)` so zero-value filtering can stay strict.
- Added pre-VDYP TSA checkpointing (`data/vdyp_prep-tsa{tsa}.pkl`) for faster warm-starts.
- Pre-VDYP checkpoint payloads now strip non-picklable fit callables for reliable resume loads.
- Added minimal validation scaffolding: `tests/`, `docs/`, and `.pre-commit-config.yaml`.
- Verified TSA 08 rerun writes `vdyp_io/logs/vdyp_curve_events.jsonl` entries with
  `first_age=1.0` and `first_volume=1e-06`.
- Added `femic vdyp report` to summarize `vdyp_runs.jsonl` + `vdyp_curve_events.jsonl`
  (status/stage/phase counts, parse errors, first-point conformance, mismatch samples).
- Added fallback handling for `nsamples="auto"` with small strata so VDYP runs all available
  records instead of raising `AssertionError`.
- Added explicit warnings + JSONL metadata when curve build/tipsy-input stages encounter
  missing VDYP outputs for specific stratum+SI combinations.
- Forced a fresh TSA 08 debug rerun (`--debug-rows 500`) and confirmed non-empty logs:
  `vdyp_runs.jsonl` (77 events) and `vdyp_curve_events.jsonl` (26 events).
- Hardened sparse-curve handling in `process_vdyp_out`: if smoothed body-fit inputs are empty or
  too short, emit a warning event and return a quasi-origin-anchored fallback curve instead of
  crashing on `idxmax()`.
- Moved `scsi_au`/`au_scsi` registration to only occur for stratum+SI combos that pass all
  operability/species filters and have usable VDYP output.
- Hardened AU-table build in `00_data-prep.py` to skip VDYP curve combos that have no AU mapping,
  with a top-10 warning summary instead of raising `KeyError`.
- Re-ran forced TSA 08 debug (`--debug-rows 500`) from fresh VDYP and reached end-to-end completion
  (process exit code `0`) with populated logs:
  `vdyp_runs.jsonl` (77 events) and `vdyp_curve_events.jsonl` (27 events, including 1
  `body_input` sparse-data warning fallback).
- Defaulted row-wise apply paths back to pandas `.apply(...)` (with optional
  `FEMIC_USE_SWIFTER=1` opt-in) to reduce swifter-related instability/noise during debug runs.
- Added `FEMIC_DISABLE_IPP` handling (default `1`) so debug runs use serial execution without
  ipyparallel controller dependencies.
- Added `FEMIC_SKIP_STANDS_SHP` handling (defaults to skip in debug mode) to bypass final
  shapefile export when iterating rapidly.
- The non-fatal shutdown message (`Error in sys.excepthook` / `Original exception was`) still
  appears even on exit code `0`; root cause remains unresolved, but pipeline outputs and VDYP
  diagnostics are now completing reliably in forced TSA08 debug reruns.
- Updated citation metadata repository URL to match the active remote:
  `https://github.com/UBC-FRESH/wbi_ria_yield`.
- Fixed singleton-stratum handling in `fit_stratum` by forcing `f_.loc[[sc]]` DataFrame access
  (avoids accidental Series coercion and `KeyError: np.False_` during boolean filtering).
- Added guards for empty species mixes in TIPSY-input assembly: if a stratum+SI has no species
  candidates after filtering, emit `no_species_candidates` warning metadata and skip that combo
  instead of raising `IndexError`.
- Stopped importing `swifter` unless `FEMIC_USE_SWIFTER=1` is explicitly enabled, removing
  default monkeypatch side effects during normal debug runs.
- Reworked `run_data_prep` to execute `00_data-prep.py` in a subprocess and stream filtered
  output; this removes persistent non-fatal legacy shutdown noise
  (`Error in sys.excepthook` / `Original exception was`) from `femic run` logs.
- Roadmap review checkpoint (2026-03-01): next implementation sequence should prioritize
  NF7 (operator-facing run artifacts) before NF8 (regression harness), then return to
  Phase 1 items NF4a/NF4b that are still open.
- `femic run` now accepts `--run-id` and `--log-dir`; these are passed to the legacy runner and
  exported as `FEMIC_RUN_ID` / `FEMIC_LOG_DIR`.
- Added per-run manifest output (`run_manifest-<run_id>.json`) with command/options, env flags,
  TSA list, checkpoint presence, and resolved run-scoped log paths.
- VDYP logs are now emitted per TSA + run id
  (`vdyp_runs-tsa{tsa}-{run_id}.jsonl`, `vdyp_curve_events-tsa{tsa}-{run_id}.jsonl`).
