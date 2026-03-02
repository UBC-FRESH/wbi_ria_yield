# Refactor Roadmap

## Phase 1: Stabilize Runtime + Inputs
- [x] P1.1 Stand up Typer CLI entrypoint (FHOPS-style, nemora-compatible)
  - [x] P1.1a Expose the `femic` console script (Forest Estate Model Input Compiler)
  - [x] P1.1b Create `src/femic/cli/main.py` with `Typer(add_completion=False, no_args_is_help=True)`
  - [x] P1.1c Organize subcommands (prep, vdyp, tsa, run) via `app.add_typer(...)`
  - [x] P1.1d Use module-level constants for defaults + typed `Path` args (avoid B008)
- [x] P1.2 Define a single entrypoint script with explicit CLI args
  - [x] P1.2a Add a `--tsa` filter and `--resume` flag
  - [x] P1.2b Centralize environment checks (VDYP, wine, data paths)
- [x] P1.3 Normalize I/O paths and required files
  - [x] P1.3a Document expected data layout under `data/` and `vdyp_io/`
  - [x] P1.3b Add validation for missing files before processing
- [x] P1.4 Improve logging and error visibility
  - [x] P1.4a Add structured logging with per-TSA context
  - [x] P1.4b Capture external tool stderr/stdout to files
- [x] P1.5 VDYP diagnostics + metadata hardening
  - [x] P1.5a Add VDYP Wine wrapper health checks (config, inputs, tmp outputs,
  exit codes)
  - [x] P1.5b Record VDYP run metadata + failure reasons per TSA and AU
  - [x] P1.5c Add curve-build diagnostics (binning stats, NLLS convergence,
  residuals)
  - [x] P1.5d Add ramp-splice diagnostics and iterative left-point trimming with warnings

## Phase 2: Modularize Pipeline Steps
- [ ] P2.1 Extract reusable modules from `00_data-prep.py`
  - [x] P2.1a Split into `io.py`, `vdyp.py`, `tsa.py`, `plots.py`
  - [ ] P2.1b Remove global state and pass explicit parameters
    - [x] P2.1b.1 Centralize 01a per-TSA VDYP cache-path templates in shared helper
    - [x] P2.1b.2 Replace residual 01a `os.path` cache checks with `Path(...).is_file()`
    - [x] P2.1b.3 Collapse 00->01a cache-path handoff to one resolved payload
    - [x] P2.1b.4 Reduce 01a `run_tsa(...)` signature by bundling remaining path/runtime args
- [ ] P2.2 Convert notebook logic into functions
  - [ ] P2.2a Wrap major steps with clear inputs/outputs
  - [ ] P2.2b Add a small orchestration layer for sequencing
  - [ ] P2.2c Move 00_data-prep 01a/01b module-load + call loops behind shared stage helpers
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
- Roadmap review checkpoint (2026-03-01): completed the runtime hardening/diagnostics tranche that
  started this refactor; roadmap focus is now Phase 2 extraction and global-state reduction.
- `femic run` now accepts `--run-id` and `--log-dir`; these are passed to the legacy runner and
  exported as `FEMIC_RUN_ID` / `FEMIC_LOG_DIR`.
- Added per-run manifest output (`run_manifest-<run_id>.json`) with command/options, env flags,
  TSA list, checkpoint presence, and resolved run-scoped log paths.
- VDYP logs are now emitted per TSA + run id
  (`vdyp_runs-tsa{tsa}-{run_id}.jsonl`, `vdyp_curve_events-tsa{tsa}-{run_id}.jsonl`).
- Added deterministic TSA08 regression fixtures under `tests/fixtures/vdyp/tsa08_debug/` and
  tests that assert stable `summarize_vdyp_logs` counts.
- Added warning-budget evaluation (`evaluate_warning_budget`) and CLI threshold flags on
  `femic vdyp report` so CI can fail when warnings/parse-errors grow beyond expected bounds.
- Added per-TSA raw VDYP stream artifacts:
  `vdyp_stdout-tsa{tsa}-{run_id}.log` and `vdyp_stderr-tsa{tsa}-{run_id}.log`.
- Expanded run manifest payloads with runtime/package versions, resolved key paths, and per-TSA
  artifact existence inventory for `vdyp_runs`, `vdyp_curve_events`, `vdyp_stdout`, and
  `vdyp_stderr`.
- Phase 1 checklist reconciled with completed runtime hardening deliverables; remaining work now starts at
  Phase 2 modularization tasks (P2.1+).
- Started Phase 2 module extraction with new reusable helpers under `src/femic/pipeline/`:
  `io.py`, `vdyp.py`, `tsa.py`, and `plots.py`.
- Legacy workflow manifest/log path logic now consumes `femic.pipeline` helpers, reducing
  duplicated logic and defining a stable seam for future migration out of notebook-generated code.
- Removed hardcoded multi-TSA defaults from new pipeline helpers; default TSA selection now reads
  from dev config (`config/dev.toml`, `[run].default_tsa_list`) with `["08"]` fallback for local
  testing.
- Introduced explicit `PipelineRunConfig` handoff from CLI to workflow wrapper so run settings
  (`tsa_list`, `resume`, `debug_rows`, `run_id`, `log_dir`) are passed as typed config instead of
  loose parameters; this is the first concrete step toward `P2.1b` global-state reduction.
- Added `LegacyExecutionPlan` builder in pipeline I/O helpers; legacy runner now consumes a fully
  resolved execution plan (command, env, run IDs, paths, checkpoints) instead of constructing this
  state inline.
- `P2.1b` is now partially complete at the CLI/workflow boundary (typed run config + execution
  plan); remaining `P2.1b` work is to eliminate notebook-script globals inside `00_data-prep.py`
  and `01a_run-tsa.py`.
- Extracted subprocess execution into `femic.pipeline.stages.run_legacy_subprocess(...)`, giving a
  reusable stage executor and reducing orchestration logic inside the legacy workflow wrapper.
- Extracted run-manifest assembly into `femic.pipeline.manifest` (`build_run_manifest_payload`,
  `collect_runtime_versions`, `write_manifest`) so workflow wrapper orchestration now calls reusable
  stage + manifest builders instead of maintaining these internals inline.
- Extracted pre-VDYP checkpoint serialization/load/save into `femic.pipeline.pre_vdyp` and wired
  `01a_run-tsa.py` to use these helpers (`load_vdyp_prep_checkpoint`,
  `save_vdyp_prep_checkpoint`), creating the first notebook-derived data-stage seam for `P2.2a`.
- Removed the old `Next Focus` section after merging non-redundant items into phase checklists to
  keep a single source of planning truth.
- Extracted VDYP input/output table I/O helpers into `femic.pipeline.vdyp_io` and refactored
  `01a_run-tsa.py` to call these shared functions (`write_vdyp_infiles_plylyr`,
  `import_vdyp_tables`), extending `P2.2a` modularization with explicit helper seams.
- Extracted VDYP sample-size estimator into `femic.pipeline.vdyp_sampling.nsamples_from_curves`
  and refactored the auto-sampling loop in `01a_run-tsa.py` to consume this helper.
- Extracted run-id/log-path resolution and append helpers into
  `femic.pipeline.vdyp_logging` (`resolve_run_id`, `build_tsa_vdyp_log_paths`,
  `append_jsonl`, `append_text`) and refactored `01a_run-tsa.py` to consume them.
- Rewired manifest-facing VDYP artifact path builder (`femic.pipeline.vdyp.build_vdyp_log_paths`)
  to reuse `build_tsa_vdyp_log_paths`, removing duplicated filename logic between modules.
- Extracted VDYP curve-building helpers into `femic.pipeline.vdyp_curves` and refactored
  `01a_run-tsa.py` to call shared `process_vdyp_out(...)` logic (including toe-fit retry/fallback
  and quasi-origin anchor behavior) through a reusable module seam.
- Extracted shared VDYP-to-TIPSY scalar derivations into `femic.pipeline.tipsy`
  (`compute_vdyp_site_index`, `compute_vdyp_oaf1`) and refactored all TSA-specific TIPSY parameter
  builders in `01a_run-tsa.py` to consume these helpers instead of duplicating inline parsing logic.
- Added reusable TIPSY candidate evaluation + warning payload helpers in `femic.pipeline.tipsy`
  (`evaluate_tipsy_candidate`, `build_tipsy_warning_event`) and rewired the AU-selection loop in
  `01a_run-tsa.py` to use centralized eligibility reasoning + standardized warning metadata.
- Added initial manual-handoff TIPSY config scaffolding under `config/tipsy/` with a draft template
  (`template.tsa.yaml`) and notes capturing cross-TSA variability from the five legacy TSA rule
  dicts (08/16/24/40/41), to guide migration from hard-coded logic to expert-authored config.
- Added `femic.pipeline.tipsy_config` with TSA YAML loader/validator and config-rule evaluation
  (`load_tipsy_tsa_config`, `validate_tipsy_tsa_config`, `build_tipsy_params_from_config`), and
  wired `01a_run-tsa.py` to prefer `config/tipsy/tsa{tsa}.yaml` (or `.yml`) when present, with
  legacy dict-based dispatch as fallback.
- Added first concrete migrated TSA config `config/tipsy/tsa08.yaml` plus tokenized assignment
  support (e.g., `$leading_species_tipsy`) so config rules can preserve legacy species normalization
  behavior (notably `SX -> SW`) while keeping per-TSA rule logic out of Python code.
- Added second migrated TSA config `config/tipsy/tsa16.yaml` (high-variability case with full
  species-mix/GW field coverage), plus tests that load the repo config and verify expected
  config-driven rule selection output.
- Added third migrated TSA config `config/tipsy/tsa24.yaml` capturing BEC-dependent branching
  (`SBS` vs `ESSF`) and species-group-specific assignment blocks; expanded config tests to verify
  both SBS and ESSF rule-path selection from repo-backed YAML.
- Added `config/tipsy/tsa40.yaml` and `config/tipsy/tsa41.yaml`, completing migration of all five
  legacy TSA rule dict examples into YAML. Extended token support for ranked species placeholders
  (`$species_rank_<n>_tipsy`, `$species_pct_<n>`) and added tests covering dynamic species token
  expansion and forest-type-conditioned rule selection.
- Switched legacy runner default to require config-driven TIPSY rules for TSA processing; missing
  config now fails fast with explicit guidance, while `FEMIC_TIPSY_USE_LEGACY=1` preserves an
  opt-in escape hatch to legacy in-code rule dispatch during transition.
- Added `femic tipsy validate` CLI command for preflight validation of TSA YAML handoff files
  (all discovered configs, or explicit `--tsa` subset), including missing-file detection and schema
  checks via shared `tipsy_config` loader/validator helpers.
- Reduced notebook-script global coupling at the 00/01a/01b stage boundary:
  `01a_run-tsa.run_tsa(...)` and `01b_run-tsa.run_tsa(...)` now take explicit runtime arguments
  (`tsa`, and for 01a also `stratum_col`, `f`, `si_levels`, `vdyp_out_cache`, fit/wrap hooks),
  and `00_data-prep.py` now passes these values directly instead of setting module globals.
- Replaced broad `module.__dict__.update(globals())` handoff with explicit, validated context
  binding via `femic.pipeline.legacy_context.bind_legacy_module_context(...)` and scoped symbol
  lists (`RUN_01A_CONTEXT_SYMBOLS`, `RUN_01B_CONTEXT_SYMBOLS`) so 01a/01b receive only required
  shared notebook-state dependencies.
- Extracted VDYP batch prep/run/import orchestration into
  `femic.pipeline.vdyp_stage.execute_vdyp_batch(...)` (input CSV staging, subprocess execution,
  stdout/stderr artifact appends, parse/error/status event logging), and rewired `01a_run-tsa.py`
  `run_vdyp` internals to call this shared stage helper.
- Added focused unit tests for the VDYP stage helper (`tests/test_vdyp_stage.py`) covering success,
  parse-error, and timeout paths with deterministic fake runner/importer hooks.
- Extracted bootstrap-dispatch orchestration from `01a_run-tsa.py` into
  `femic.pipeline.vdyp_stage.execute_bootstrap_vdyp_runs(...)` (per stratum+SI context assembly,
  dispatch/dispatch_error logging, and nested result-table accumulation), and rewired the
  `force_run_vdyp` branch to consume this helper.
- Expanded `tests/test_vdyp_stage.py` with bootstrap orchestration coverage for success and
  dispatch-error logging behavior.
- Extracted curve-smoothing dispatch orchestration from `01a_run-tsa.py` into
  `femic.pipeline.vdyp_stage.execute_curve_smoothing_runs(...)`, centralizing per stratum+SI
  missing-output warnings, `process_vdyp_out(...)` invocation, and curve-context event emission.
- Rewired `01a_run-tsa.py` to consume `execute_curve_smoothing_runs(...)` and build
  `vdyp_smoothxy` tables from returned smoothed-curve records before writing
  `vdyp_curves_smooth-tsa{tsa}.feather`.
- Expanded `tests/test_vdyp_stage.py` with curve-smoothing orchestration coverage, including
  missing-VDYP warning logging and kwarg-override forwarding into `process_vdyp_out(...)`.
- Extracted legacy VDYP overlay plotting into
  `femic.pipeline.vdyp_stage.plot_curve_overlays(...)`, so `01a_run-tsa.py` now delegates the
  per-stratum plotting loop to a shared stage helper while preserving existing plot output shape.
- Reduced required 01a legacy context symbols by removing no-longer-used globals
  (`Path`, `curve_fit`, `shlex`, `subprocess`) from `RUN_01A_CONTEXT_SYMBOLS`.
- Added `tests/test_vdyp_stage.py` coverage for overlay plotting orchestration
  (`plot_curve_overlays`) to assert expected plotting calls and axis/legend handling.
- Extracted the remaining smooth-curve table assembly/write path into
  `femic.pipeline.vdyp_stage.build_smoothed_curve_table(...)`, so `01a_run-tsa.py` now delegates
  smoothed-curve DataFrame construction + optional feather persistence through a shared stage helper.
- Removed additional stale 01a legacy context symbols after extraction (`_curve_fit`, `wraps`)
  from `RUN_01A_CONTEXT_SYMBOLS`.
- Expanded `tests/test_vdyp_stage.py` with `build_smoothed_curve_table(...)` coverage to verify
  row assembly and output-path write invocation behavior.
- Extracted VDYP result-resolution branching (`force_run`, per-TSA cache load, combined-cache
  fallback, bootstrap-and-persist) into
  `femic.pipeline.vdyp_stage.load_or_build_vdyp_results_tsa(...)`, and rewired `01a_run-tsa.py`
  to delegate this cache/bootstrap decision path through the shared stage helper.
- Reduced required 01a legacy context symbols again by removing stale `pickle` dependency from
  `RUN_01A_CONTEXT_SYMBOLS`.
- Expanded `tests/test_vdyp_stage.py` with coverage for `load_or_build_vdyp_results_tsa(...)`
  across force-run, TSA-cache, combined-cache, and compat-loader fallback branches.
- Extracted VDYP polygon/layer table loading into
  `femic.pipeline.vdyp_stage.load_vdyp_input_tables(...)` and rewired `01a_run-tsa.py` to use this
  helper instead of inline source/feather branch code.
- Reduced required 01a legacy context symbols again by removing stale `gpd` dependency from
  `RUN_01A_CONTEXT_SYMBOLS`.
- Expanded `tests/test_vdyp_stage.py` with `load_vdyp_input_tables(...)` coverage for both feather
  cache loads and source-geodatabase load+persist behavior.
- Added `femic.pipeline.vdyp_stage.build_curve_fit_adapter(...)` and rewired `01a_run-tsa.py` to
  construct a local `curve_fit` wrapper from `curve_fit_impl` so legacy `maxfev` kwargs map to
  modern SciPy `max_nfev` without per-call inline wrapper logic.
- Removed obsolete `wraps_impl` plumbing from `01a_run-tsa.run_tsa(...)` and the
  `00_data-prep.py` caller now that curve-fit adaptation is centralized in the stage helper.
- Expanded `tests/test_vdyp_stage.py` with `build_curve_fit_adapter(...)` coverage for both
  `maxfev -> max_nfev` conversion and passthrough when `max_nfev` is already supplied.
- Reduced additional 01a global-state coupling by extending `01a_run-tsa.run_tsa(...)` with
  explicit path/export inputs (`vdyp_results_*`, `vdyp_input_pandl_path`,
  `vdyp_{ply,lyr}_feather_path`, `tipsy_params_columns`, `tipsy_params_path_prefix`) and wiring
  `00_data-prep.py` to pass them directly.
- Trimmed `RUN_01A_CONTEXT_SYMBOLS` after this signature change by removing no-longer-needed path
  and TIPSY-export globals (`vdyp_input_pandl_path`, `vdyp_{ply,lyr}_feather_path`,
  `vdyp_results_*`, `tipsy_params_columns`, `tipsy_params_path_prefix`).
- Extended `01a_run-tsa.run_tsa(...)` again to take the mutable per-run data structures
  (`results`, `vdyp_results`, `vdyp_curves_smooth`, `scsi_au`, `au_scsi`, `tipsy_params`) and
  lookup inputs (`si_levelquants`, `species_list`,
  `vdyp_curves_smooth_tsa_feather_path_prefix`) explicitly from `00_data-prep.py`.
- Trimmed `RUN_01A_CONTEXT_SYMBOLS` further after this handoff update, leaving only baseline
  runtime/module helpers (`np`, `pd`, `plt`, `sns`, `os`, `operator`, `itertools`, `distance`,
  `kwarg_overrides`, `_femic_resume_effective`) instead of dataset/state payload globals.
- Converted `01b_run-tsa.run_tsa(...)` to explicit runtime inputs
  (`results`, `au_scsi`, `tipsy_curves`, `vdyp_curves_smooth`) and updated `00_data-prep.py` to
  pass these directly instead of relying on injected module globals.
- Removed all remaining 01b context injection requirements by setting
  `RUN_01B_CONTEXT_SYMBOLS` to an empty tuple and localizing 01b plotting imports
  (`matplotlib.pyplot`, `seaborn`) inside the function.
- Extracted TIPSY export assembly/writes from `01a_run-tsa.py` into reusable
  `femic.pipeline.tipsy` helpers (`build_tipsy_input_table`, `write_tipsy_input_exports`) and
  rewired the legacy script to delegate xlsx/dat output generation through these helpers.
- Expanded `tests/test_tipsy.py` with coverage for new TIPSY export helpers: row/column assembly,
  empty-input failure behavior, and xlsx/dat artifact writes.
- Extracted config-vs-legacy TIPSY rule-selection into
  `femic.pipeline.tipsy_config.resolve_tipsy_param_builder(...)` and rewired `01a_run-tsa.py` to
  call this helper for builder/message resolution.
- Expanded `tests/test_tipsy_config.py` with resolver coverage for config-preferred, forced-legacy,
  and missing-config error paths.
- Localized remaining non-numeric helper imports used by `01a_run-tsa.py` (`distance`,
  `itertools`, `operator`, `os`) inside `run_tsa(...)`, removing these dependencies on injected
  legacy module globals.
- Trimmed `RUN_01A_CONTEXT_SYMBOLS` again after import localization; 01a context binding now
  requires only `_femic_resume_effective`, `kwarg_overrides`, and plotting/dataframe modules
  (`np`, `pd`, `plt`, `sns`).
- Extracted the TIPSY candidate-selection and AU-assignment loop from `01a_run-tsa.py` into
  `femic.pipeline.tipsy.build_tipsy_params_for_tsa(...)`, including eligibility filtering, warning
  event emission, and final `scsi_au`/`au_scsi`/`tipsy_params` map construction.
- Rewired `01a_run-tsa.run_tsa(...)` to consume `build_tipsy_params_for_tsa(...)` and pass
  explicit runtime flags (`resume_effective`, `force_run_vdyp`, `kwarg_overrides_for_tsa`) from
  `00_data-prep.py` instead of reading injected globals.
- Localized `numpy`/`pandas`/`matplotlib`/`seaborn` imports inside `01a_run-tsa.run_tsa(...)` and
  trimmed `RUN_01A_CONTEXT_SYMBOLS` to an empty tuple; both 01a and 01b now run without required
  legacy context payload injection.
- Expanded `tests/test_tipsy.py` with orchestration coverage for
  `build_tipsy_params_for_tsa(...)` (success mapping, missing-VDYP warning, no-species warning).
- Extracted inline legacy TSA rule builders/exclusion setup from `01a_run-tsa.py` into new
  `femic.pipeline.tipsy_legacy` module (`build_tipsy_exclusion`,
  `get_legacy_tipsy_builders`, `tipsy_params_tsa08/16/24/40/41`) and rewired 01a to consume this
  shared seam.
- Added `tests/test_tipsy_legacy.py` coverage for legacy builder-dispatch keys, exclusion-map keys,
  and baseline TSA08 output fields.
- Added runtime-wiring regression tests in `tests/test_legacy_context.py` asserting
  `RUN_01A_CONTEXT_SYMBOLS == ()` and `RUN_01B_CONTEXT_SYMBOLS == ()`, plus empty-required-symbol
  binding behavior.
- Removed no-op legacy context binding calls from `00_data-prep.py` now that both
  `RUN_01A_CONTEXT_SYMBOLS` and `RUN_01B_CONTEXT_SYMBOLS` are empty; 01a/01b module loading now
  proceeds directly to explicit `run_tsa(...)` invocation.
- Removed the inactive `if 0:` legacy TIPSY export branch from `01a_run-tsa.py` (unused duplicate
  xlsx assembly path) to keep only the active helper-driven export flow.
- Pruned deprecated legacy-context re-exports from `femic.pipeline.__init__` now that context
  injection is no longer part of the runtime orchestration surface.
- Removed additional low-risk inactive `if 0:` debug/reload blocks from `00_data-prep.py`
  (checkpoint rollbacks/manual cache toggles/legacy shp export snippets) to reduce notebook-era
  dead-code noise without altering active runtime branches.
- Added `tests/test_legacy_orchestration_wiring.py` AST regression checks to lock explicit
  `_run01a_module.run_tsa(...)` and `_run01b_module.run_tsa(...)` keyword handoff surfaces and
  assert no `bind_legacy_module_context(...)` call remains in `00_data-prep.py`.
- Removed the final inactive `if 0:` notebook-era debug blocks from `00_data-prep.py` (dormant
  legacy `process_vdyp_out(...)` sandbox and manual TSA smoothing loop), leaving only active
  orchestration code paths.
- Expanded `tests/test_tipsy_legacy.py` with a TSA24 regression case that verifies BEC-dependent
  legacy rule branching (`SBS` vs `ESSF`) for a fir-leading stand.
- Extracted default VDYP curve-smoothing kwarg overrides into
  `femic.pipeline.vdyp_overrides` (`DEFAULT_VDYP_KWARG_OVERRIDES`,
  `vdyp_kwarg_overrides_for_tsa(...)`) to remove hardcoded override dicts from
  `00_data-prep.py` and centralize override defaults in a reusable pipeline seam.
- Updated `01a_run-tsa.run_tsa(...)` to resolve override defaults internally when
  `kwarg_overrides_for_tsa` is not provided; `00_data-prep.py` now passes `None` explicitly.
- Added regression coverage for the new override helper (`tests/test_vdyp_overrides.py`) plus AST
  wiring coverage asserting the 00->01a handoff uses internal defaults
  (`kwarg_overrides_for_tsa=None`).
- Rewired `01a_run-tsa.py` to consume `femic.pipeline.tsa.target_nstrata_for(...)` instead of an
  inline TSA->target-strata dict, reducing notebook-era duplicated constants.
- Added shared `femic.pipeline.tsa.MIN_STANDCOUNT` and updated 01a strata filtering/tests to consume
  this constant instead of hardcoded local values.
- Removed additional inline bootstrap tuning constants from `01a_run-tsa.py` by relying on
  `execute_bootstrap_vdyp_runs(...)` defaults for `half_rel_ci`, `nsamples_c1`, and `ipp_mode`.
- Added `tests/test_legacy_01a_structure.py` AST guardrails that lock 01a structural cleanup:
  `run_tsa(...)` must call `target_nstrata_for(...)`, must not reintroduce an inline
  `target_nstrata` dict assignment, and must not locally reassign `si_levels`.
- Extracted 01a strata summarization logic into `femic.pipeline.tsa.build_strata_summary(...)`
  (target-strata selection, site-index/crown-closure/coverage aggregates, stand-count filtering,
  and `median_si` enrichment), reducing notebook-era inline grouping logic in `run_tsa(...)`.
- Rewired `01a_run-tsa.py` to consume `build_strata_summary(...)` for stratum candidate table
  assembly and IQR reporting.
- Expanded `tests/test_pipeline_helpers.py` with deterministic `build_strata_summary(...)` coverage
  (aggregate outputs + validation error path), and updated `tests/test_legacy_01a_structure.py`
  guardrails to assert `run_tsa(...)` calls the extracted helper seam.
- Extracted 01a lexmatch alias resolution into
  `femic.pipeline.tsa.build_stratum_lexmatch_alias_map(...)`, moving Levenshtein tie-break
  selection logic (distance + relative-area tiebreak) out of inline notebook-era code.
- Rewired `01a_run-tsa.py` to consume `build_stratum_lexmatch_alias_map(...)` when mapping
  non-selected strata onto selected strata for downstream fitting.
- Expanded tests with deterministic alias-map coverage in `tests/test_pipeline_helpers.py`, and
  added AST guardrails in `tests/test_legacy_01a_structure.py` asserting 01a calls the new
  lexmatch helper seam.
- Extracted the inline 01a stratum-fitting block into
  `femic.pipeline.vdyp_stage.fit_stratum_curves(...)`, centralizing per-SI quantile filtering,
  species-share derivation, curve-fit execution/error handling, and optional plot emission in a
  reusable stage seam.
- Rewired `01a_run-tsa.py` to call `fit_stratum_curves(...)` during pre-VDYP stratum compilation,
  removing the nested `fit_stratum(...)` function definition from `run_tsa(...)`.
- Expanded `tests/test_vdyp_stage.py` with focused `fit_stratum_curves(...)` coverage (successful
  species payload output and curve-fit error skip/log behavior), and extended
  `tests/test_legacy_01a_structure.py` guardrails to assert 01a calls the stage helper and no
  longer defines a nested `fit_stratum`.
- Extracted stratum-compilation loop orchestration into
  `femic.pipeline.vdyp_stage.compile_strata_fit_results(...)`, so 01a now delegates per-stratum
  iteration/message/result assembly through a reusable stage helper.
- Rewired `01a_run-tsa.py` pre-VDYP compilation path to call
  `compile_strata_fit_results(...)` with the extracted `fit_stratum_curves(...)` seam.
- Expanded `tests/test_vdyp_stage.py` with deterministic compile-loop helper coverage, and extended
  `tests/test_legacy_01a_structure.py` guardrails to assert 01a calls
  `compile_strata_fit_results(...)`.
- Extracted VDYP sampling-mode orchestration into
  `femic.pipeline.vdyp_stage.run_vdyp_sampling(...)`, centralizing the `auto`/`all`/fixed sample
  flow, cache-hit handling, and gap-fill loop decision logic previously embedded in 01a.
- Rewired `01a_run-tsa.py` `run_vdyp(...)` to delegate sampling decisions through
  `run_vdyp_sampling(...)` while keeping batch execution/logging in its existing `_run_vdyp(...)`
  closure.
- Expanded `tests/test_vdyp_stage.py` with focused `run_vdyp_sampling(...)` coverage
  (auto-small-sample path, auto gap-fill phase path, and invalid-mode assertion), and extended
  `tests/test_legacy_01a_structure.py` guardrails to assert 01a calls
  `run_vdyp_sampling(...)`.
- Extracted the nested 01a `run_vdyp(...)` wrapper into
  `femic.pipeline.vdyp_stage.run_vdyp_for_stratum(...)`, centralizing per-stratum VDYP runtime
  preflight checks (wine/bin/params), default log-path resolution, run-event logging, batch
  execution dispatch, and sampling orchestration handoff.
- Rewired `01a_run-tsa.py` bootstrap execution to call `run_vdyp_for_stratum(...)` directly and
  removed the nested `run_vdyp` and `_tsa_log_path` definitions from `run_tsa(...)`.
- Expanded `tests/test_vdyp_stage.py` with `run_vdyp_for_stratum(...)` coverage and updated
  `tests/test_legacy_01a_structure.py` guardrails to assert 01a no longer calls
  `run_vdyp_sampling(...)` directly and no longer defines a nested `run_vdyp`.
- Queued next extraction slice: move the remaining 01a bootstrap-callable wiring lambda into a
  dedicated stage helper so `run_tsa(...)` only passes explicit orchestration inputs without
  inline closure assembly.
- Added `femic.pipeline.vdyp_stage.build_run_vdyp_for_stratum_runner(...)`, a reusable helper that
  binds per-TSA runtime context (`tsa`, `run_id`, VDYP tables, fit hooks, and run-log paths) into
  a `run_vdyp_fn(sample_table, **kwargs)` callable compatible with
  `execute_bootstrap_vdyp_runs(...)`.
- Rewired `01a_run-tsa.py` bootstrap flow to build `run_vdyp_fn` via
  `build_run_vdyp_for_stratum_runner(...)`, removing the remaining inline lambda that assembled
  `run_vdyp_for_stratum(...)` kwargs inside `run_tsa(...)`.
- Expanded `tests/test_vdyp_stage.py` with binding/forwarding coverage for
  `build_run_vdyp_for_stratum_runner(...)`, and updated
  `tests/test_legacy_01a_structure.py` guardrails to assert 01a calls the builder helper and no
  longer calls `run_vdyp_for_stratum(...)` directly.
- Queued next extraction slice: remove the remaining inline `run_bootstrap_fn=lambda: ...`
  assembly in `01a_run-tsa.py` by introducing a dedicated stage helper for per-TSA bootstrap
  callback construction.
- Added `femic.pipeline.vdyp_stage.build_bootstrap_vdyp_results_runner(...)`, a reusable helper
  that binds per-TSA bootstrap dispatch inputs (`tsa`, `run_id`, results payload, SI levels, log
  sink, `run_vdyp_fn`, and cache map) into a zero-arg callback compatible with
  `load_or_build_vdyp_results_tsa(...)`.
- Rewired `01a_run-tsa.py` to pass `run_bootstrap_fn` built by
  `build_bootstrap_vdyp_results_runner(...)`, removing the remaining inline
  `run_bootstrap_fn=lambda: execute_bootstrap_vdyp_runs(...)` closure assembly.
- Expanded `tests/test_vdyp_stage.py` with binding/forwarding coverage for
  `build_bootstrap_vdyp_results_runner(...)`, and updated
  `tests/test_legacy_01a_structure.py` guardrails to assert 01a calls the builder helper and does
  not pass an inline lambda to `run_bootstrap_fn`.
- Queued next extraction slice: move the remaining inline `compile_one_fn=lambda: ...` assembly in
  pre-VDYP stratum compilation into a dedicated stage helper so 01a no longer builds fit-call
  closures inline.
- Added `femic.pipeline.vdyp_stage.build_fit_stratum_curves_runner(...)`, a reusable helper that
  binds per-TSA stratum-fit context into `compile_one_fn(stratumi, sc)` callbacks for
  `compile_strata_fit_results(...)`.
- Rewired `01a_run-tsa.py` to build and pass `compile_one_fn` via
  `build_fit_stratum_curves_runner(...)`, removing inline fit-call closure assembly in the pre-VDYP
  compilation path.
- Expanded `tests/test_vdyp_stage.py` with fit-runner binding coverage and updated
  `tests/test_legacy_01a_structure.py` guardrails so 01a must call the builder helper and must not
  pass inline lambdas to `compile_one_fn`.
- Extracted legacy notebook fit functions (`fit_func1`, `fit_func1_bounds_func`, `fit_func2`,
  `fit_func2_bounds_func`) from `01a_run-tsa.py` into `femic.pipeline.vdyp_curves`
  (`legacy_fit_func1`, `legacy_fit_func1_bounds_func`, `legacy_fit_func2`,
  `legacy_fit_func2_bounds_func`), and rewired 01a to consume these shared helpers.
- Expanded `tests/test_vdyp_curves.py` with deterministic coverage for legacy fit-function outputs
  and bounds, and added AST guardrails asserting 01a no longer defines nested legacy fit functions.
- Queued next extraction slice: remove the final nested `match_stratum(...)` function definition in
  `01a_run-tsa.py` by moving alias-application logic into a reusable TSA helper.
- Added `femic.pipeline.tsa.apply_stratum_alias_map(...)` to encapsulate selected-strata retention
  plus alias fallback assignment for `*_matched` stratum columns.
- Rewired `01a_run-tsa.py` to call `apply_stratum_alias_map(...)` for stratum matching, removing
  the final nested helper definition (`match_stratum`) from `run_tsa(...)`.
- Expanded `tests/test_pipeline_helpers.py` with deterministic alias-application coverage and added
  AST guardrails in `tests/test_legacy_01a_structure.py` asserting 01a calls the helper and has no
  nested `match_stratum`.
- `01a_run-tsa.run_tsa(...)` now has zero nested function definitions; remaining extraction focus is
  reducing inline notebook-style constant/plot configuration blocks into reusable stage helpers.
- Queued next extraction slice: move curve-smoothing plot setup constants
  (`palette_flavours`/palette/alpha defaults) from `01a_run-tsa.py` into a shared stage helper.
- Added `femic.pipeline.vdyp_stage.CurveSmoothingPlotConfig` and
  `build_curve_smoothing_plot_config(...)` to centralize legacy curve-smoothing plot defaults
  (plot toggle, `figsize`, palette setup, `palette_flavours`, `alphas`) behind a shared stage seam.
- Rewired `01a_run-tsa.py` curve-smoothing overlay path to call
  `build_curve_smoothing_plot_config(...)` and consume the returned config instead of defining
  inline plot/palette constants.
- Expanded `tests/test_vdyp_stage.py` with deterministic defaults coverage for
  `build_curve_smoothing_plot_config(...)`, and added AST guardrails in
  `tests/test_legacy_01a_structure.py` asserting 01a calls this helper and no longer assigns
  inline smoothing `palette_flavours`/`alphas` constants.
- Queued next extraction slice: remove dead legacy `fit_func2`/`fit_func2_bounds_func` local
  bindings from `01a_run-tsa.py` now that these values are no longer consumed by any active stage.
- Removed dead `legacy_fit_func2`/`legacy_fit_func2_bounds_func` imports and local
  `fit_func2`/`fit_func2_bounds_func` assignments from `01a_run-tsa.py`; these values were no
  longer used by any active stage path after prior smoothing-stage extraction.
- Added `tests/test_legacy_01a_structure.py` guardrails asserting `run_tsa(...)` no longer assigns
  local legacy fit2 bindings.
- Queued next extraction slice: move inline TIPSY staging defaults
  (`min_operable_years`, `si_iqrlo_quantile`, local `verbose`) into a shared helper seam so 01a no
  longer embeds these constants directly.
- Removed inline TIPSY staging constant assignments from `01a_run-tsa.py`
  (`min_operable_years`, `si_iqrlo_quantile`, local `verbose`) and now rely on
  `build_tipsy_params_for_tsa(...)` shared default thresholds.
- Expanded `tests/test_legacy_01a_structure.py` with guardrails asserting 01a no longer assigns
  these constants inline and no longer overrides corresponding
  `build_tipsy_params_for_tsa(...)` keyword defaults.
- Queued next extraction slice: move overlay axis-bound constants (`xlim`, `ylim`) passed to
  `plot_curve_overlays(...)` out of `01a_run-tsa.py` into a shared stage/default helper.
- Extended `CurveSmoothingPlotConfig` / `build_curve_smoothing_plot_config(...)` to include overlay
  axis defaults (`xlim`, `ylim`) so smoothing overlay bounds are configured in one shared stage
  seam.
- Rewired `01a_run-tsa.py` `plot_curve_overlays(...)` call to consume
  `smooth_plot_cfg.xlim`/`smooth_plot_cfg.ylim` instead of inline tuple literals.
- Expanded `tests/test_vdyp_stage.py` defaults coverage for new axis config fields and added
  `tests/test_legacy_01a_structure.py` AST guardrails asserting overlay axes are sourced from
  `smooth_plot_cfg`.
- Queued next extraction slice: move stratum-distribution plot constants (`bw`, `linewidth`,
  `inner`, `width`, `cut`, `alpha`) from `01a_run-tsa.py` into a shared plotting helper/config
  seam.
- Added `StrataDistributionPlotConfig` and `build_strata_distribution_plot_config(...)` in
  `femic.pipeline.plots` to centralize default plotting constants for 01a stratum-distribution
  diagnostics.
- Rewired the 01a stratum-distribution plotting block to consume
  `build_strata_distribution_plot_config(...)` values instead of inline constants.
- Expanded `tests/test_pipeline_helpers.py` with defaults coverage for the new plot-config helper,
  and added AST guardrails in `tests/test_legacy_01a_structure.py` asserting 01a calls the helper
  and no longer assigns inline strata-plot constants.
- Queued next extraction slice: replace inline strata plot output path literals in `01a_run-tsa.py`
  with `femic.pipeline.plots.strata_plot_paths(...)` helper output.
- Rewired `01a_run-tsa.py` strata diagnostic plot output writes to call
  `femic.pipeline.plots.strata_plot_paths(...)` and save to returned PDF/PNG paths instead of
  inline `"plots/strata-tsa%s.*"` string literals.
- Added AST guardrails in `tests/test_legacy_01a_structure.py` asserting 01a calls
  `strata_plot_paths(...)` and no longer embeds inline strata plot output path literals.
- Queued next extraction slice: move inline stratum-label ordering toggle (`sort_lex` branch) from
  `01a_run-tsa.py` into a reusable TSA/plot helper seam.
- Added `femic.pipeline.plots.resolve_strata_plot_ordering(...)` to centralize abundance-vs-lexic
  ordering for stratum distribution plots.
- Rewired `01a_run-tsa.py` to call `resolve_strata_plot_ordering(...)` and removed the inline
  `sort_lex` branch and local ordering assembly.
- Expanded `tests/test_pipeline_helpers.py` with deterministic ordering coverage for default
  (abundance) and lexical modes, and added AST guardrails in
  `tests/test_legacy_01a_structure.py` asserting 01a calls the helper and no longer assigns local
  `sort_lex`.
- Queued next extraction slice: remove residual inline notebook-style diagnostic plot calls in early
  01a flow (`site_index_median` histogram + scatter) into a reusable plotting helper.
- Added `femic.pipeline.plots.plot_strata_site_index_diagnostics(...)` to encapsulate early 01a
  stratum diagnostics plotting (`site_index_median` histogram + abundance-vs-SI scatter).
- Rewired `01a_run-tsa.py` to call `plot_strata_site_index_diagnostics(...)` and removed direct
  inline histogram/scatter plotting calls from `run_tsa(...)`.
- Expanded `tests/test_pipeline_helpers.py` with deterministic behavior coverage for the new
  diagnostics helper and added AST guardrails in `tests/test_legacy_01a_structure.py` asserting 01a
  calls the helper and no longer invokes direct `plt.scatter(...)` for this stage.
- Queued next extraction slice: centralize stratum-distribution/ordering plotting orchestration
  (bar+violin block) into a dedicated shared helper to further shrink inline plotting in 01a.
- Added `femic.pipeline.plots.render_strata_distribution_plot(...)` to encapsulate the stratum
  distribution diagnostics rendering workflow (barplot + violinplot + labels + xlim + PDF/PNG
  writes via helper-managed paths).
- Rewired `01a_run-tsa.py` to call `render_strata_distribution_plot(...)`, removing direct inline
  seaborn bar/violin calls and save-path plumbing from `run_tsa(...)`.
- Expanded `tests/test_pipeline_helpers.py` with deterministic rendering-helper coverage and added
  AST guardrails in `tests/test_legacy_01a_structure.py` asserting 01a calls the rendering helper
  and no longer performs direct `sns.barplot(...)`/`sns.violinplot(...)` calls in this stage.
- Queued next extraction slice: trim now-unused local imports from `01a_run-tsa.py` (notably early
  `seaborn` direct plotting dependencies that have moved behind helper seams) and lock with
  guardrails.
- Added `femic.pipeline.tipsy_config.resolve_tipsy_runtime_options(...)` to centralize
  `FEMIC_TIPSY_CONFIG_DIR`/`FEMIC_TIPSY_USE_LEGACY` environment resolution for TIPSY runtime
  behavior.
- Rewired `01a_run-tsa.py` to call `resolve_tipsy_runtime_options(...)` instead of reading
  `os.environ` directly for TIPSY config/legacy flags.
- Expanded `tests/test_tipsy_config.py` with defaults/override coverage for
  `resolve_tipsy_runtime_options(...)` and added AST guardrails in
  `tests/test_legacy_01a_structure.py` asserting 01a no longer reads `os.environ` directly for this
  stage.
- Queued next extraction slice: begin consolidating remaining inline 01a run-stage constants
  (`fit_rawdata`, `min_age`, `agg_type`, `verbose`, `plot`) into dedicated stage/config helpers.
- Added `StratumFitRunConfig` and `build_stratum_fit_run_config(...)` in
  `femic.pipeline.vdyp_stage` to centralize pre-VDYP stratum fit-stage defaults
  (`fit_rawdata`, `min_age`, `agg_type`, `plot`, `verbose`, `figsize`, `xlim`, `ylim`).
- Rewired `01a_run-tsa.py` pre-VDYP fit compilation path to consume
  `build_stratum_fit_run_config(...)` instead of assigning these constants inline.
- Expanded `tests/test_vdyp_stage.py` with defaults coverage for the new fit-stage config helper
  and added AST guardrails in `tests/test_legacy_01a_structure.py` asserting 01a calls the helper
  and no longer assigns inline stratum fit-stage constants.
- Queued next extraction slice: centralize pre-VDYP checkpoint filename construction
  (`"./data/vdyp_prep-tsa%s.pkl"`) into a shared path helper seam.
- Added `femic.pipeline.pre_vdyp.pre_vdyp_checkpoint_path(...)` to centralize per-TSA pre-VDYP
  checkpoint path construction.
- Rewired `01a_run-tsa.py` to call `pre_vdyp_checkpoint_path(...)` instead of constructing
  `"./data/vdyp_prep-tsa%s.pkl"` inline.
- Expanded `tests/test_pre_vdyp.py` with path-helper coverage (default dir + TSA zero-padding) and
  added AST guardrails in `tests/test_legacy_01a_structure.py` asserting 01a calls the helper and
  no longer embeds `vdyp_prep-tsa` literals.
- Queued next extraction slice: centralize remaining inline 01a path templates
  (`vdyp_results_tsa_pickle_path`, `vdyp_curves_smooth_tsa_feather_path`) into dedicated shared
  path helpers.
- Transcript review checkpoint (2026-03-02): the legacy notebook-to-script debugging tranche is
  complete (00/01a/01b script entrypoints, VDYP/Wine diagnostics hardening, config-driven TIPSY
  handoff, and broad 01a helper extraction); active work remains in Phase 2 (`P2.1b`/`P2.2`) to
  remove residual inline globals/path templates and tighten stage orchestration seams.
- Planned execution sequence after transcript review:
  1) extract remaining 01a inline path templates into shared helpers, 2) trim stale 01a imports and
  dependency injection leftovers, 3) finish converting any residual inline stage logic to helper
  calls with AST guardrails, 4) run full validation gate and capture a new end-to-end TSA debug run
  summary in changelog notes.
- Added `femic.pipeline.vdyp.build_vdyp_cache_paths(...)` to centralize per-TSA cache artifact path
  templates for `vdyp_results-tsa*.pkl` and `vdyp_curves_smooth-tsa*.feather`.
- Rewired `01a_run-tsa.py` to call `build_vdyp_cache_paths(...)` instead of constructing per-TSA
  cache paths inline via string templates.
- Expanded tests with helper and guardrail coverage:
  `tests/test_pipeline_helpers.py` now checks `build_vdyp_cache_paths(...)`, and
  `tests/test_legacy_01a_structure.py` now asserts 01a calls the helper and no longer assigns
  inline `%`-formatted cache-path templates.
- Full validation gate passes after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (154 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: trim now-stale local imports and remaining dependency handoff
  plumbing in `01a_run-tsa.py` after path-template helper extraction.
- Removed local `os` dependency from `01a_run-tsa.py` path checks by switching to
  `Path(...).is_file()` for pre-VDYP checkpoint and smoothed-curve cache detection.
- Added AST guardrail coverage in `tests/test_legacy_01a_structure.py` asserting `run_tsa(...)`
  does not import `os` locally for this path-check stage.
- Queued next extraction slice: reduce remaining 00->01a path handoff plumbing by passing a single
  resolved VDYP cache-path payload instead of separate path-prefix arguments.
- Queued execution batch (post-checklist refresh):
  1) implement a `vdyp_cache_paths` payload handoff from `00_data-prep.py` to `01a_run-tsa.py`,
  2) reduce `run_tsa(...)` argument surface by grouping remaining path/runtime plumbing into a
  typed config payload,
  3) extract 00_data-prep 01a/01b module-loader/caller loops into shared orchestration helper(s).
- Added `Legacy01ARuntimeConfig` (`femic.pipeline.legacy_runtime`) and rewired
  `01a_run-tsa.run_tsa(...)` to consume this typed runtime payload instead of discrete
  path/runtime args (`resume_effective`, `force_run_vdyp`, cache path prefixes, tipsy export paths,
  and optional fit/cache hooks).
- Collapsed 00->01a cache-path handoff to one resolved payload (`vdyp_cache_paths`) built in
  `00_data-prep.py` and passed through `Legacy01ARuntimeConfig`.
- Added shared orchestration helpers in `femic.pipeline.stages`:
  `load_legacy_module(...)` and `run_legacy_tsa_loop(...)`.
- Rewired 00_data-prep 01a/01b execution loops to use shared loader/loop helpers (instead of
  inline `importlib.util` plumbing and duplicated loop scaffolding).
- Added script-run fallback in `00_data-prep.py` to prepend `src/` on `ModuleNotFoundError` so
  direct `python 00_data-prep.py` execution can still import `femic.pipeline` helpers.
- Expanded guardrails/tests:
  `tests/test_legacy_orchestration_wiring.py` now validates runtime-config handoff plus shared
  loader/loop helper usage, `tests/test_pipeline_stages.py` now covers
  `load_legacy_module(...)`/`run_legacy_tsa_loop(...)`, and
  `tests/test_legacy_01a_structure.py` asserts 01a reads cache paths from `runtime_config`.
- Queued next extraction slice: continue `P2.2` by moving remaining 00_data-prep orchestration
  logic around stage setup/checkpoints into reusable stage helpers so the top-level script becomes a
  thin workflow shell.
- Added stage setup helpers in `femic.pipeline.stages`:
  `initialize_legacy_tsa_stage_state(...)`, `prepare_tsa_index(...)`, and
  `should_skip_if_outputs_exist(...)`.
- Added `femic.pipeline.legacy_runtime.build_legacy_01a_runtime_config(...)` so 00_data-prep no
  longer assembles the 01a runtime payload inline.
- Rewired `00_data-prep.py` to consume these helpers for state-map initialization, TSA-index
  preparation, resume-skip checks, and 01a runtime-config assembly.
- Expanded tests to cover new setup/runtime helpers and wiring:
  `tests/test_pipeline_stages.py` now covers helper behavior and runtime-config cache path build,
  and `tests/test_legacy_orchestration_wiring.py` asserts 00_data-prep calls the new setup/runtime
  helper seams.
- Queued next extraction slice: continue thinning 00_data-prep by extracting remaining post-01b
  bundle/table orchestration and path wiring into shared helpers under `femic.pipeline`.
- Added new bundle orchestration helpers in `femic.pipeline.bundle`:
  `resolve_bundle_paths(...)`, `bundle_tables_ready(...)`, `load_bundle_tables(...)`,
  `write_bundle_tables(...)`, and `ensure_scsi_au_from_table(...)`.
- Rewired 00_data-prep post-01b bundle block to use shared bundle helpers for path wiring,
  resume-time table loading, CSV persistence, and `scsi_au` backfill.
- Added focused bundle helper tests in `tests/test_bundle.py` and expanded orchestration AST
  guardrails in `tests/test_legacy_orchestration_wiring.py` to assert 00_data-prep calls bundle
  helper seams.
- Queued next extraction slice: move the heavy AU/curve table assembly loop (currently inline in
  00_data-prep) into a reusable pipeline helper with deterministic unit coverage.
- Added `build_bundle_tables_from_curves(...)` and `BundleAssemblyResult` in
  `femic.pipeline.bundle` to extract the heavy AU/curve table assembly loop from 00_data-prep.
- Rewired 00_data-prep to consume `build_bundle_tables_from_curves(...)` and retain warning summary
  behavior for missing AU mappings using returned diagnostics.
- Expanded `tests/test_bundle.py` with deterministic coverage for managed/unmanaged curve assembly
  and missing-mapping diagnostics, and extended orchestration guardrails to assert
  `build_bundle_tables_from_curves(...)` usage.
- Queued next extraction slice: continue P2.2 by moving residual stratum-matching + SI-level
  assignment orchestration (post-bundle stage) into reusable helper seams.
- Added residual post-bundle strata helpers in `femic.pipeline.tsa`:
  `assign_stratum_matches_from_au_table(...)` and
  `assign_si_levels_from_stratum_quantiles(...)`.
- Rewired `00_data-prep.py` post-bundle stage to call these helpers instead of maintaining inline
  stratum-matching and SI-level assignment loops.
- Expanded helper/wiring tests:
  `tests/test_pipeline_helpers.py` now covers both new TSA helpers, and
  `tests/test_legacy_orchestration_wiring.py` guardrails now assert
  `assign_stratum_matches_from_au_table(...)` and
  `assign_si_levels_from_stratum_quantiles(...)` seam usage.
- Queued next extraction slice: continue thinning 00_data-prep by extracting AU assignment + null
  diagnostics (`_lookup_scsi_au`, `au_from_scsi`, missing/null summaries) into reusable helper(s).
- Added AU-assignment helper seams in `femic.pipeline.tsa`:
  `lookup_scsi_au_base(...)`, `assign_au_ids_from_scsi(...)`,
  `summarize_missing_au_mappings(...)`, `build_au_assignment_null_summary(...)`, and
  `validate_nonempty_au_assignment(...)`.
- Rewired 00_data-prep AU assignment + null-diagnostics block to consume these helpers instead of
  inline `_lookup_scsi_au`/`au_from_scsi`/missing-summary logic.
- Expanded tests with deterministic helper coverage in `tests/test_pipeline_helpers.py` and updated
  orchestration guardrails in `tests/test_legacy_orchestration_wiring.py` to assert new AU helper
  seam usage.
- Queued next extraction slice: continue P2.2 by extracting the post-AU curve-ID assignment block
  (`assign_curve1`, `assign_curve2`) into reusable helper(s), then wire through tests/guardrails.
- Added `assign_curve_ids_from_au_table(...)` in `femic.pipeline.bundle` to centralize post-AU
  curve ID assignment logic (managed/unmanaged switch and fallback handling).
- Rewired 00_data-prep to call `assign_curve_ids_from_au_table(...)` in place of inline
  `assign_curve1`/`assign_curve2` functions and row-wise assignment calls.
- Expanded `tests/test_bundle.py` with deterministic coverage for managed/unmanaged curve assignment
  behavior, and updated orchestration guardrails to assert
  `assign_curve_ids_from_au_table(...)` seam usage.
- Queued next extraction slice: continue P2.2 by extracting the remaining post-curve assignment
  THLB/theme orchestration blocks into reusable helper seams.
- Added `assign_thlb_area_and_flag(...)` in `femic.pipeline.tsa` to centralize THLB area + THLB
  flag assignment rules previously embedded in 00_data-prep.
- Rewired 00_data-prep to call `assign_thlb_area_and_flag(...)` instead of inline `thlb_area(...)`
  and `assign_thlb(...)` functions.
- Expanded `tests/test_pipeline_helpers.py` with deterministic THLB helper coverage and updated
  orchestration guardrails to assert `assign_thlb_area_and_flag(...)` seam usage.
- Queued next extraction slice: continue P2.2 by extracting remaining theme/shapefile post-processing
  orchestration (`has_managed_curve`, `extract_features`, per-TSA stand export transforms) into
  reusable helper seams.
- Added `src/femic/pipeline/stands.py` to centralize stand-export post-processing helpers:
  `should_skip_stands_export(...)`, `clean_stand_geometry(...)`,
  `extract_stand_features_for_tsa(...)`, `build_stands_column_map(...)`,
  `prepare_stands_export_frame(...)`, and `export_stands_shapefiles(...)`.
- Rewired 00_data-prep stand-export orchestration to consume the new stands helpers (skip-flag
  resolution, column-map construction, per-TSA feature extraction/transform, and shapefile write
  loop) instead of inline local function definitions.
- Exported stands helpers from `femic.pipeline.__init__` and added deterministic coverage in
  `tests/test_stands.py`; updated orchestration guardrails in
  `tests/test_legacy_orchestration_wiring.py` to assert
  `build_stands_column_map(...)`, `should_skip_stands_export(...)`, and
  `export_stands_shapefiles(...)` seam usage.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (178 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by extracting remaining inline post-01b orchestration
  prints/warnings and path literals in `00_data-prep.py` into reusable logging/path helper seams so
  the script body approaches a pure stage-composition shell.
- Added `tipsy_stage_output_paths(...)` in `src/femic/pipeline/tipsy.py` to centralize legacy 01b
  per-TSA output CSV path construction.
- Added `emit_missing_au_mapping_warning(...)` in `src/femic/pipeline/tsa.py` to centralize the
  two-line warning emission for missing AU mapping diagnostics.
- Rewired 00_data-prep post-01b orchestration to consume the new helpers:
  `_should_skip_01b(...)` now uses `tipsy_stage_output_paths(...)`, and AU null-handling now uses
  `emit_missing_au_mapping_warning(...)` instead of inline `print(...)` statements.
- Exported new helpers via `femic.pipeline.__init__`, added deterministic helper tests in
  `tests/test_tipsy.py` and `tests/test_pipeline_helpers.py`, and updated AST guardrails in
  `tests/test_legacy_orchestration_wiring.py` to assert seam usage.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (180 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by centralizing remaining `00_data-prep.py` hardcoded
  `./data/...` artifact path literals (checkpoints, intermediates, and exports) behind reusable path
  builders so stage orchestration uses structured path payloads instead of inline strings.
- Added `build_ria_vri_checkpoint_paths(...)` in `src/femic/pipeline/io.py` to centralize legacy
  VRI checkpoint artifact path construction (`ria_vri_vclr1p_checkpoint{1..8}.feather`).
- Rewired `00_data-prep.py` to call `build_ria_vri_checkpoint_paths(...)` and source checkpoint path
  variables from the returned path payload instead of embedding eight inline `./data/...` literals.
- Exported the new path helper via `femic.pipeline.__init__`, added deterministic helper coverage in
  `tests/test_pipeline_helpers.py`, and extended AST guardrails in
  `tests/test_legacy_orchestration_wiring.py` to assert seam usage.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (181 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by centralizing remaining non-checkpoint
  `00_data-prep.py` `./data/...` path literals (VDYP input/output, TIPSY exports, and siteprod
  artifact prefixes) into reusable path builders so stage configuration is fully payload-driven.
- Added `LegacyDataArtifactPaths` and `build_legacy_data_artifact_paths(...)` in
  `src/femic/pipeline/io.py` to centralize non-checkpoint legacy `data/` artifact paths under a
  single reusable payload.
- Rewired `00_data-prep.py` to source non-checkpoint data artifact paths from
  `build_legacy_data_artifact_paths(...)`, including VDYP input/output paths, TIPSY input-column
  file path and prefix, siteprod artifacts, bundle root, THLB raster, and stands shapefile output
  directory.
- Exported new I/O path payload helpers via `femic.pipeline.__init__`, added deterministic coverage
  in `tests/test_pipeline_helpers.py`, and updated AST guardrails in
  `tests/test_legacy_orchestration_wiring.py` to assert
  `build_legacy_data_artifact_paths(...)` seam usage.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (182 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by removing residual duplicated path-to-string
  coercion and remaining ad-hoc path joins in `00_data-prep.py` (favor passing `Path` objects
  through helper boundaries directly) so orchestration has a consistent typed path surface.
- Reworked `00_data-prep.py` path handling to keep legacy artifact paths as `Path` objects through
  helper boundaries (removed residual `str(...)` coercions for non-external artifact paths).
- Replaced remaining ad-hoc path joins in 00_data-prep with helper/path-native composition:
  `build_vdyp_cache_paths(...)` + `tipsy_params_excel_path(...)` now drive 01a resume-skip output
  checks; siteprod layer temp paths now use `Path` joins/globs instead of `%s` string templates.
- Replaced residual string-shell path checks/builds in this stage:
  `Path.is_file()` for local executable/artifact presence, list-based `subprocess.run(...)` calls
  with pathlike args, and `Path.read_text().splitlines()` for TIPSY column loading.
- Added `tipsy_params_excel_path(...)` in `src/femic/pipeline/tipsy.py`, exported it in
  `femic.pipeline.__init__`, added deterministic coverage in `tests/test_tipsy.py`, and updated AST
  guardrails in `tests/test_legacy_orchestration_wiring.py` to assert
  `build_vdyp_cache_paths(...)` + `tipsy_params_excel_path(...)` seam usage in 00_data-prep.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (183 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by centralizing remaining inline external-data root
  resolution and path selection logic in `00_data-prep.py` (`_select_external_data_root`,
  candidate list assembly, VRI/TSA source roots) into reusable I/O helper seams.
- Added `LegacyExternalDataPaths` + `resolve_legacy_external_data_paths(...)` in
  `src/femic/pipeline/io.py` to centralize external data-root candidate resolution and canonical
  VRI/TSA source path construction.
- Rewired `00_data-prep.py` to consume `resolve_legacy_external_data_paths(...)`, removing inline
  `_select_external_data_root` and candidate-list assembly logic from the script body.
- Exported external-path helpers in `femic.pipeline.__init__`, added deterministic helper coverage
  in `tests/test_pipeline_helpers.py`, and updated AST orchestration guardrails in
  `tests/test_legacy_orchestration_wiring.py` to assert
  `resolve_legacy_external_data_paths(...)` seam usage.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (184 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by extracting remaining inline siteprod raster
  export/stack orchestration in `00_data-prep.py` (ArcRasterRescue command assembly, temporary
  layer path enumeration, cleanup loop) into dedicated stage/helper seams.
- Added `src/femic/pipeline/siteprod.py` with reusable siteprod orchestration helpers:
  `parse_arc_raster_rescue_layer_mappings(...)`, `list_siteprod_layers(...)`,
  `build_siteprod_layer_tif_path(...)`, `enumerate_siteprod_layer_tif_paths(...)`, and
  `export_and_stack_siteprod_layers(...)`.
- Rewired `00_data-prep.py` siteprod stage to consume `list_siteprod_layers(...)` and
  `export_and_stack_siteprod_layers(...)`, removing inline ArcRasterRescue command assembly,
  temporary-layer path enumeration, and temp cleanup loop logic.
- Exported siteprod helpers via `femic.pipeline.__init__`, added deterministic coverage in
  `tests/test_siteprod.py`, and updated AST guardrails in
  `tests/test_legacy_orchestration_wiring.py` to assert
  `list_siteprod_layers(...)` + `export_and_stack_siteprod_layers(...)` seam usage.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (188 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by extracting remaining inline siteprod sampling
  orchestration in `00_data-prep.py` (`siteprod_species_lookup`, `mean_siteprod` closure, and row
  apply wiring) into reusable helper seams under `femic.pipeline.siteprod`.
- Expanded `src/femic/pipeline/siteprod.py` with reusable siteprod sampling helpers:
  `DEFAULT_SITEPROD_SPECIES_LOOKUP`, `siteprod_species_lookup(...)`,
  `mean_siteprod_for_row(...)`, and `assign_siteprod_from_raster(...)`.
- Rewired `00_data-prep.py` checkpoint2 siteprod assignment to call
  `assign_siteprod_from_raster(...)`, removing inline `siteprod_species_lookup` and nested
  `mean_siteprod(...)` closure logic from the script.
- Exported new sampling helpers via `femic.pipeline.__init__`, extended
  `tests/test_siteprod.py` with lookup + row-mean + assignment coverage, and updated AST guardrails
  in `tests/test_legacy_orchestration_wiring.py` to assert
  `assign_siteprod_from_raster(...)` seam usage.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (190 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by extracting remaining inline species-volume
  compilation orchestration in checkpoint3 (`compile_species_vol` local function, map dispatch, and
  per-species assignment loop) into reusable helper seams.
- Added `src/femic/pipeline/species_volume.py` with reusable checkpoint3 species-volume helpers:
  `species_volume_input_columns(...)`, `compile_species_volume_series(...)`, and
  `compile_species_volume_columns(...)`.
- Rewired checkpoint3 species-volume compilation in `00_data-prep.py` to call
  `compile_species_volume_columns(...)`, removing inline `compile_species_vol(...)`, manual column
  assembly, map dispatch, and per-species assignment loop.
- Exported species-volume helpers via `femic.pipeline.__init__`, added deterministic coverage in
  `tests/test_species_volume.py`, and updated AST guardrails in
  `tests/test_legacy_orchestration_wiring.py` to assert
  `compile_species_volume_columns(...)` seam usage.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (193 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by extracting remaining inline checkpoint2
  pre-filter/fillna normalization block (species/soil/BCLCS/LIVE_VOL defaults and filters) into a
  dedicated reusable helper seam.
- Added `src/femic/pipeline/vri.py` with
  `normalize_and_filter_checkpoint2_records(...)` to centralize checkpoint2 fill-defaults and
  row-filter rules (species slots, soil/BCLCS defaults, operability filters).
- Rewired `00_data-prep.py` checkpoint2 normalization stage to call
  `normalize_and_filter_checkpoint2_records(...)`, removing the large inline fillna/filter block.
- Exported VRI helper seams via `femic.pipeline.__init__`, added deterministic unit coverage in
  `tests/test_vri.py`, and updated AST guardrails in
  `tests/test_legacy_orchestration_wiring.py` to assert
  `normalize_and_filter_checkpoint2_records(...)` seam usage.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (195 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by extracting remaining inline conifer/deciduous
  classification helpers (`is_conif`, `is_decid`, `pconif`, `pdecid`, stand-type classifiers) from
  `00_data-prep.py` into reusable helper seams.
- Expanded `src/femic/pipeline/vri.py` with reusable stand-classification helpers:
  `is_conifer_species_code(...)`, `is_deciduous_species_code(...)`, `pconif(...)`, `pdecid(...)`,
  `classify_stand_cdm(...)`, `classify_stand_forest_type(...)`, and
  `assign_forest_type_from_species_pct(...)`.
- Rewired `00_data-prep.py` to remove inline conifer/deciduous classifier function definitions and
  call `assign_forest_type_from_species_pct(...)` for forest-type assignment.
- Exported new VRI classification helpers via `femic.pipeline.__init__`, expanded
  `tests/test_vri.py` coverage for all classification helpers, and updated AST guardrails in
  `tests/test_legacy_orchestration_wiring.py` to assert
  `assign_forest_type_from_species_pct(...)` seam usage.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (198 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by extracting remaining inline stratum-code assembly
  logic (`stratify_stand` + `stratify_stand_lexmatch` partial wiring) from `00_data-prep.py` into
  reusable helper seams.
- Expanded `src/femic/pipeline/vri.py` with reusable stratum-code helpers:
  `stratify_stand(...)` and `assign_stratum_codes_with_lexmatch(...)`.
- Rewired `00_data-prep.py` to remove inline `stratify_stand`/`stratify_stand_lexmatch` wiring and
  call `assign_stratum_codes_with_lexmatch(...)` at both stratum derivation stages.
- Exported new VRI stratum helpers via `femic.pipeline.__init__`, expanded
  `tests/test_vri.py` with deterministic stratification coverage, and updated AST guardrails in
  `tests/test_legacy_orchestration_wiring.py` to assert
  `assign_stratum_codes_with_lexmatch(...)` seam usage count.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (200 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by extracting the remaining inline THLB sampling
  closure (`mean_thlb`) into a reusable helper seam so raster masking logic is no longer defined
  inline in `00_data-prep.py`.
- Added reusable THLB raster sampling helpers in `src/femic/pipeline/tsa.py`:
  `mean_thlb_for_geometry(...)` and `assign_thlb_raw_from_raster(...)`.
- Rewired `00_data-prep.py` THLB sampling stage to call
  `assign_thlb_raw_from_raster(...)`, removing inline `with rio.open(...): mean_thlb(...)` closure
  logic.
- Exported new THLB raster helpers via `femic.pipeline.__init__`, expanded deterministic coverage in
  `tests/test_pipeline_helpers.py`, and updated AST guardrails in
  `tests/test_legacy_orchestration_wiring.py` to assert
  `assign_thlb_raw_from_raster(...)` seam usage.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (201 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by extracting the remaining inline checkpoint83
  post-THLB stand-filter block (`BCLCS_LEVEL_2`, management base, BEC, species/site-index null
  filters) into a reusable helper seam in `femic.pipeline.vri`.
- Expanded `src/femic/pipeline/vri.py` with
  `filter_post_thlb_stands(...)` to centralize checkpoint83 post-THLB stand filtering rules.
- Rewired `00_data-prep.py` checkpoint83 post-THLB filtering stage to call
  `filter_post_thlb_stands(...)`, removing the remaining inline filter chain.
- Exported the new VRI filter helper via `femic.pipeline.__init__`, expanded deterministic coverage
  in `tests/test_vri.py`, and updated AST guardrails in
  `tests/test_legacy_orchestration_wiring.py` to assert
  `filter_post_thlb_stands(...)` seam usage.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (202 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by extracting remaining inline species-list
  derivation (`set().union(...)` over `SPECIES_CD_1..6`) into a reusable helper seam so derived
  species universes are no longer assembled ad hoc inside `00_data-prep.py`.
- Expanded `src/femic/pipeline/vri.py` with
  `derive_species_list_from_slots(...)` to centralize species-universe derivation from
  `SPECIES_CD_1..6` slot columns.
- Rewired `00_data-prep.py` to call `derive_species_list_from_slots(...)` instead of inline
  `set().union(...)` species-list assembly.
- Exported the new species-list helper via `femic.pipeline.__init__`, expanded deterministic
  coverage in `tests/test_vri.py`, and updated AST guardrails in
  `tests/test_legacy_orchestration_wiring.py` to assert
  `derive_species_list_from_slots(...)` seam usage.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (203 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by extracting remaining inline post-bundle warning
  formatting for missing AU/curve mappings into a reusable diagnostics helper seam so 00_data-prep
  no longer assembles this warning text block inline.
- Added `emit_missing_au_curve_mapping_warning(...)` in `src/femic/pipeline/bundle.py` to
  centralize post-bundle missing AU/curve warning formatting and emission.
- Rewired `00_data-prep.py` post-bundle diagnostics to call
  `emit_missing_au_curve_mapping_warning(...)` instead of assembling warning text inline.
- Exported the new bundle diagnostics helper via `femic.pipeline.__init__`, expanded deterministic
  coverage in `tests/test_bundle.py`, and updated AST guardrails in
  `tests/test_legacy_orchestration_wiring.py` to assert
  `emit_missing_au_curve_mapping_warning(...)` seam usage.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (204 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by extracting residual inline `f.shape` diagnostic
  notebook artifacts from `00_data-prep.py` into optional helper/log seams (or remove where dead)
  so the script body remains pure orchestration.
- Removed residual dead inline `f.shape` notebook diagnostic expressions from
  `00_data-prep.py` where they had no runtime effect.
- Verified this cleanup does not alter pipeline behavior; all required gates passed:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (204 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by removing remaining dead notebook preview artifacts
  (`au_table.head()`, `curve_table.head()`, `curve_points_table.head()`) so `00_data-prep.py`
  remains a pure orchestration script.
- Removed remaining dead notebook preview artifacts
  (`au_table.head()`, `curve_table.head()`, `curve_points_table.head()`) from `00_data-prep.py`.
- Verified no behavior change and full validation gate success:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (204 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by trimming residual notebook-only `if 1:` wrappers
  in `00_data-prep.py` where they no longer control branching, so orchestration flow is explicit.
- Removed residual notebook-only `if 1:` wrappers in `00_data-prep.py` that no longer controlled
  branching (01a stage block and checkpoint83 post-THLB block), leaving explicit orchestration
  flow.
- Verified behavior parity and full validation gate success:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (204 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by removing or gating remaining notebook-only plot
  diagnostics (`f.thlb_raw.describe()` / `f.thlb_raw.hist()`) so headless/script runs stay focused
  on pipeline outputs.
- Gated remaining notebook-only THLB diagnostics in `00_data-prep.py` behind
  `FEMIC_THLB_DIAGNOSTICS` (`0` default; enable with `1`/`true`/`yes`) so headless/script runs do
  not emit notebook-style plotting/stat calls unless explicitly requested.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (204 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by removing remaining dead inline aggregate preview
  expressions (`f.query(...).groupby(...).sum()` and `f.groupby(...).sum()`) from
  `00_data-prep.py` so script-mode orchestration contains only side-effecting pipeline steps.
- Removed remaining dead inline aggregate preview expressions from `00_data-prep.py`
  (`f.query("thlb == 1").groupby(...).sum()` and `f.groupby("tsa_code").thlb_area.sum()`), leaving
  only side-effecting pipeline steps in this stage.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (204 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by removing notebook carry-over no-op aliases like
  `stratify_stand = stratify_stand` if any remain, or mark completion of this cleanup tranche if
  none remain.
- Confirmed no residual notebook no-op alias assignments remained; removed adjacent dead empty cell
  marker artifacts in `00_data-prep.py` (`# --- cell 85 ---`, `# --- cell 101 ---`,
  `# --- cell 105 ---`) as part of the same cleanup tranche.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (204 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by reducing residual generic exception handling in
  `00_data-prep.py` (e.g., broad `except:` blocks around helperable operations) into explicit helper
  seams or narrowed exception paths.
- Added `ensure_au_table_index(...)` in `src/femic/pipeline/bundle.py` and rewired
  `00_data-prep.py` to call it in place of the broad `try/except:` around
  `au_table.set_index("au_id", inplace=True)`.
- Exported the helper via `femic.pipeline.__init__`, expanded deterministic coverage in
  `tests/test_bundle.py`, and updated AST guardrails in
  `tests/test_legacy_orchestration_wiring.py` to assert `ensure_au_table_index(...)` seam usage.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (206 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by narrowing broad `except Exception` around
  ipyparallel client initialization into explicit import/runtime exception paths (or helper seam)
  while preserving serial fallback behavior.
- Added `ParallelExecutionBackend` and `initialize_parallel_execution_backend(...)` in
  `src/femic/pipeline/stages.py` to centralize ipyparallel bootstrap + serial fallback behavior with
  explicit fallback exception classes (instead of broad `except Exception`), and rewired
  `00_data-prep.py` to consume that helper seam.
- Exported the new parallel backend seam via `femic.pipeline.__init__`, expanded deterministic
  coverage in `tests/test_pipeline_stages.py`, and updated AST guardrails in
  `tests/test_legacy_orchestration_wiring.py` to assert
  `initialize_parallel_execution_backend(...)` seam usage.
- Narrowed `stratify_stand(...)` row lookup fallback handling in `src/femic/pipeline/vri.py` from
  broad `except Exception` to explicit lookup errors (`KeyError`, `TypeError`, `IndexError`) and
  expanded coverage in `tests/test_vri.py` for attribute-style row objects.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (209 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by narrowing remaining broad exception fallbacks in
  THLB helper seams (`mean_thlb_for_geometry(...)` / `assign_thlb_raw_from_raster(...)` in
  `src/femic/pipeline/tsa.py`) into explicit raster/row-lookup exception paths while preserving
  legacy default-on-error behavior.
- Narrowed broad THLB helper fallback scopes in `src/femic/pipeline/tsa.py`:
  `mean_thlb_for_geometry(...)` now catches explicit raster/mask runtime classes
  (`ValueError`, `TypeError`, `RuntimeError`, `OSError`) and
  `assign_thlb_raw_from_raster(...)` row geometry fallback now catches explicit lookup errors
  (`KeyError`, `TypeError`, `IndexError`).
- Expanded deterministic coverage in `tests/test_pipeline_helpers.py` to assert
  `mean_thlb_for_geometry(...)` still returns `default_on_error` for expected runtime failures while
  unexpected exceptions propagate.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (211 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing remaining broad `except Exception`
  handlers in pipeline helper modules that support legacy orchestration (next target:
  `src/femic/pipeline/vdyp_curves.py`) and narrow them to explicit operational fallback classes
  without changing emitted diagnostics.
- Narrowed remaining broad curve-smoothing exception handling in
  `src/femic/pipeline/vdyp_curves.py` by introducing an explicit
  `_curve_fit_fallback_exception_types()` tuple and applying it to both body-fit and toe-fit retry
  fallback paths in `process_vdyp_out(...)`.
- Preserved legacy fallback behavior for expected operational fit failures while allowing unexpected
  exceptions to propagate for visibility/debuggability.
- Expanded deterministic coverage in `tests/test_vdyp_curves.py` to assert:
  runtime body-fit failures still fallback to quasi-origin outputs, and unexpected body/toe failures
  (`ZeroDivisionError`) now propagate.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (214 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing broad fallback handlers in
  `src/femic/pipeline/vdyp_stage.py` and narrowing them to explicit subprocess/IO/parsing exception
  classes while preserving current logging semantics.
- Narrowed a first safe subset of broad exception handlers in `src/femic/pipeline/vdyp_stage.py`:
  `fit_stratum_curves(...)` now catches explicit curve-fit operational failures, and
  `execute_vdyp_batch(...)` now catches explicit subprocess execution and parse/import failure
  classes for `status=error` / `status=parse_error` logging paths.
- Preserved existing logging semantics for expected operational failures while allowing unexpected
  exceptions to propagate.
- Expanded deterministic coverage in `tests/test_vdyp_stage.py` to assert:
  `RuntimeError` curve-fit failures still skip species with `fit error` messages, and unexpected
  `ZeroDivisionError` failures in curve-fit, subprocess execution, and parse stages propagate.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (217 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by narrowing the remaining broad exception handler in
  `execute_bootstrap_vdyp_runs(...)` (`dispatch_error` logging wrapper around `run_vdyp_fn`) into
  explicit run-stage exception classes while preserving JSONL diagnostics.
- Narrowed the remaining broad dispatch wrapper in
  `execute_bootstrap_vdyp_runs(...)` (`src/femic/pipeline/vdyp_stage.py`) to explicit
  `_bootstrap_dispatch_exception_types()` while preserving `dispatch_error` JSONL emission for known
  operational failures.
- Expanded deterministic coverage in `tests/test_vdyp_stage.py` to assert unexpected bootstrap
  dispatch failures (`ZeroDivisionError`) now propagate without being converted into
  `dispatch_error` records.
- Verified `src/femic/pipeline/vdyp_stage.py` now contains no `except Exception` handlers.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (218 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing remaining broad exception handlers in
  legacy-adapter modules (`src/femic/pipeline/tipsy.py`, `tipsy_config.py`, `tipsy_legacy.py`) and
  narrowing first safe operational fallback paths with explicit exception classes.
- Narrowed a first safe subset of broad exception fallbacks in tipsy adapter modules:
  `compute_vdyp_site_index(...)` and `compute_vdyp_oaf1(...)` in `src/femic/pipeline/tipsy.py`,
  forest-type mode fallback in `src/femic/pipeline/tipsy_config.py`, and species-slot unpack
  fallback in `tipsy_params_tsa40(...)` (`src/femic/pipeline/tipsy_legacy.py`).
- Preserved malformed-input fallback behavior for expected data-shape/key issues while allowing
  unexpected exceptions to propagate.
- Expanded deterministic coverage in `tests/test_tipsy.py`, `tests/test_tipsy_config.py`, and
  `tests/test_tipsy_legacy.py` to assert both expected fallback behavior and unexpected-error
  propagation.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (222 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by narrowing the remaining broad exception wrapper in
  `build_tipsy_params_for_tsa(...)` (`src/femic/pipeline/tipsy.py`, around
  `evaluate_tipsy_candidate(...)`) to explicit candidate-evaluation data/runtime exception classes
  while preserving current debug message emission and re-raise behavior.
- Narrowed the remaining broad candidate-evaluation wrapper in
  `build_tipsy_params_for_tsa(...)` (`src/femic/pipeline/tipsy.py`) to explicit
  `_tipsy_candidate_exception_types()` while preserving legacy debug message emission and re-raise
  behavior for expected candidate-evaluation failures.
- Expanded deterministic coverage in `tests/test_tipsy.py` to assert:
  candidate `ValueError` paths still emit debug context then re-raise, and unexpected
  candidate-evaluation failures (`ZeroDivisionError`) propagate.
- Verified no `except Exception` handlers remain in tipsy adapter modules
  (`src/femic/pipeline/tipsy.py`, `tipsy_config.py`, `tipsy_legacy.py`).
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (224 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing remaining broad exception handlers
  outside tipsy/vdyp modules (current highest-priority target: `src/femic/pipeline/tsa.py`) and
  narrowing operational fallback paths with explicit exception classes plus propagation tests.
- Narrowed the broad pre-VDYP resume checkpoint load handler in `01a_run-tsa.py` from
  `except Exception` to explicit pickle/IO/runtime classes
  (`OSError`, `EOFError`, `pickle.UnpicklingError`, `TypeError`, `AttributeError`,
  `ModuleNotFoundError`) while preserving existing failure message + non-fatal resume fallback
  behavior.
- Expanded AST guardrails in `tests/test_legacy_01a_structure.py` with
  `test_run01a_no_broad_exception_handlers` to prevent reintroduction of bare/broad exception
  handlers in `run_tsa(...)`.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (225 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by narrowing the remaining broad exception handler in
  CLI entry wiring (`src/femic/cli/main.py`) with explicit command/runtime exception classes and
  targeted CLI regression coverage.
- Narrowed the remaining broad CLI debug-traceback handler in `src/femic/cli/main.py`
  (`_enable_rich_tracebacks`) to explicit optional-import failures
  (`ModuleNotFoundError`, `ImportError`) so unexpected import-time/runtime failures are no longer
  silently swallowed.
- Added targeted CLI coverage in `tests/test_cli_main.py` to assert missing optional `rich`
  dependency is ignored while unexpected import failures propagate.
- Completed broad-exception hardening audit for active orchestration/code paths:
  no `except Exception` or bare `except:` handlers remain in `src/`, `tests/`,
  `00_data-prep.py`, or `01a_run-tsa.py`.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (227 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by replacing remaining sentinel `assert False`
  branches in legacy orchestration/helper modules with explicit typed errors carrying actionable
  context (start with legacy TIPSY builders in `src/femic/pipeline/tipsy_legacy.py`).
- Replaced sentinel `assert False` branches in legacy TIPSY builders
  (`src/femic/pipeline/tipsy_legacy.py`) with explicit typed errors carrying actionable context:
  `ValueError` for invalid unsupported species/BEC rule selections and `NotImplementedError` for
  explicitly unimplemented legacy forest-type branches.
- Added reusable error helpers (`_raise_invalid_legacy_tipsy_rule(...)`,
  `_raise_unimplemented_legacy_tipsy_rule(...)`) so failure paths are explicit and consistent.
- Expanded deterministic coverage in `tests/test_tipsy_legacy.py` to assert unsupported inputs raise
  typed/contextual errors and added an AST guardrail ensuring `tipsy_legacy.py` contains no
  `assert False` sentinels.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (231 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by replacing remaining `assert False` sentinels in
  `src/femic/pipeline/vdyp_stage.py` (unreachable load-balanced branch and invalid `nsamples`
  guard) with explicit typed errors plus regression tests.
- Replaced remaining `assert False` sentinels in `src/femic/pipeline/vdyp_stage.py` with explicit
  typed errors:
  `NotImplementedError` for unsupported `ipp_mode='load_balanced'` branch in
  `run_vdyp_sampling(...)`, and `ValueError` for invalid `nsamples` mode values.
- Expanded deterministic coverage in `tests/test_vdyp_stage.py` to assert these branches now raise
  typed errors with informative messages.
- Verified no `assert False` sentinels remain in production orchestration/pipeline modules
  (`src/`, `00_data-prep.py`, `01a_run-tsa.py`).
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (232 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing remaining broad `assert`-style runtime
  sentinels in production helper/orchestration paths (non-test) and replacing inappropriate
  runtime assertions with explicit typed errors where behavior is user/input dependent.
- Replaced remaining non-test runtime assertion control-flow checks with explicit typed errors in
  production modules:
  `resolve_tipsy_param_builder(...)` (`src/femic/pipeline/tipsy_config.py`),
  `run_legacy_subprocess(...)` (`src/femic/pipeline/stages.py`),
  `clean_stand_geometry(...)` (`src/femic/pipeline/stands.py`), and runtime config validation in
  `run_tsa(...)` (`01a_run-tsa.py`).
- Expanded deterministic coverage with new regression/guardrail tests in
  `tests/test_tipsy_config.py`, `tests/test_pipeline_stages.py`, `tests/test_stands.py`, and
  `tests/test_legacy_01a_structure.py` for new typed error branches and assertion-removal guards.
- Completed runtime assertion hardening audit:
  no `assert` statements remain in production orchestration/pipeline code
  (`src/`, `00_data-prep.py`, `01a_run-tsa.py`).
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (237 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by consolidating repeated legacy rule-error
  construction patterns (currently duplicated across TIPSY/VDYP helper seams) into shared diagnostic
  helpers where practical, while preserving existing external behavior and messages.
- Added shared diagnostics formatting helpers in `src/femic/pipeline/diagnostics.py`
  (`format_context_kv(...)`, `build_contextual_error_message(...)`) to centralize contextual
  error-string construction.
- Rewired legacy TIPSY and VDYP typed-error branches to use shared diagnostics formatting:
  `src/femic/pipeline/tipsy_legacy.py` and `src/femic/pipeline/vdyp_stage.py`, preserving existing
  behavior while reducing duplicated message assembly logic.
- Added deterministic coverage in `tests/test_diagnostics.py` and verified existing regression
  coverage still exercises the rewired TIPSY/VDYP error branches.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (240 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by consolidating repeated structured event payload
  assembly in VDYP/TIPSY warning/error logging paths into shared builders where this can be done
  without changing emitted field sets.
- Extended shared diagnostics utilities in `src/femic/pipeline/diagnostics.py` with
  `build_timestamped_event(...)` to centralize structured event payload construction.
- Rewired duplicated VDYP/TIPSY event payload assembly to use shared helpers without changing
  emitted field sets:
  `build_tipsy_warning_event(...)` (`src/femic/pipeline/tipsy.py`) and bootstrap/batch
  VDYP run event logging paths in `src/femic/pipeline/vdyp_stage.py`
  (`dispatch`, `dispatch_error`, `timeout`, `error`, `parse_error`, `ok|empty_output`).
- Added deterministic unit coverage in `tests/test_diagnostics.py` for the shared event helper and
  validated existing TIPSY/VDYP regression suites against the rewired event construction paths.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (240 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing remaining ad hoc timestamped event/log
  payload builders outside VDYP/TIPSY (if any) and consolidating them into shared diagnostics
  helpers where this can be done with zero field-shape drift.
- Continued event-payload consolidation by rewiring remaining ad hoc VDYP run-event builders in
  `src/femic/pipeline/vdyp_stage.py` (`cache_only`, `start`, and curve-input missing-output
  warning) to use shared `build_timestamped_event(...)` helper.
- Preserved emitted field shapes/status semantics for existing log consumers and regression tests.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (240 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by evaluating whether `process_vdyp_out(...)`
  (`src/femic/pipeline/vdyp_curves.py`) can adopt shared timestamped event builder without
  changing its intentional single-base-event timestamp semantics; if not, explicitly document that
  rationale and mark this consolidation sub-track complete.
- Completed the queued `vdyp_curves.py` evaluation and successfully adopted shared event helpers
  without changing its single-base-event timestamp semantics: `process_vdyp_out(...)` now builds its
  base event via shared `build_timestamped_event(...)` exactly once per run and reuses that payload
  across emitted events.
- Extended `build_timestamped_event(...)` (`src/femic/pipeline/diagnostics.py`) to support optional
  `status` and explicit `timestamp` override so both per-event and base-event patterns are supported
  through one helper.
- Expanded deterministic coverage in `tests/test_diagnostics.py` for status-optional event payloads
  and validated `tests/test_vdyp_curves.py` against the rewired base-event construction path.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (241 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by closing the event-consolidation sub-track with a
  quick repo-wide audit for remaining ad hoc `event` + `timestamp` payload construction in
  production code and either (a) rewire to shared diagnostics helpers or (b) document explicit
  exceptions where intentional.
- Closed the queued event-consolidation audit by rewiring the final ad hoc structured event path in
  `src/femic/pipeline/vdyp_curves.py` (`vdyp_curve_anchor`) to shared
  `build_timestamped_event(...)` while preserving one-timestamp-per-run semantics.
- Extended `build_timestamped_event(...)` (`src/femic/pipeline/diagnostics.py`) to support optional
  `status` and explicit timestamp override, enabling both per-event and base-event reuse patterns.
- Added `build_vdyp_stream_header(...)` in `src/femic/pipeline/vdyp_logging.py` and rewired
  `execute_vdyp_batch(...)` (`src/femic/pipeline/vdyp_stage.py`) to consume it, removing the last
  inline timestamped stream-header string assembly from execution flow.
- Expanded deterministic coverage in `tests/test_diagnostics.py`, `tests/test_vdyp_curves.py`, and
  `tests/test_vdyp_logging.py` for the rewired helpers and timestamp-semantics guard.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (242 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by reducing duplicated fallback-event assembly inside
  `process_vdyp_out(...)` (`src/femic/pipeline/vdyp_curves.py`) via a small internal event-builder
  seam that reuses shared diagnostics helpers without changing emitted fields.
- Reduced duplicated fallback-event assembly in `process_vdyp_out(...)`
  (`src/femic/pipeline/vdyp_curves.py`) by adding a small internal `emit_curve_event(...)` seam that
  reuses shared diagnostics event helpers while preserving emitted field sets and timestamp/context
  semantics.
- Rewired all `process_vdyp_out(...)` event emissions (fallback, body-fit error, toe-fit success,
  toe-fit warning, quasi-origin anchor) through the new internal seam; behavior remains unchanged.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (242 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing duplicate formatting/serialization logic in
  logging helpers (`append_jsonl`, stream-header and related callers) for additional safe
  centralization seams now that event payload assembly is consolidated.
- Consolidated duplicate logging-format/serialization logic in `src/femic/pipeline/vdyp_logging.py`
  by introducing `serialize_jsonl_payload(...)` and `append_line(...)`, then rewiring
  `append_jsonl(...)` to use these shared seams.
- Preserved existing external behavior (`default=str` JSON serialization and newline-terminated line
  append semantics) while removing repeated parent-dir + line-write patterns.
- Expanded deterministic coverage in `tests/test_vdyp_logging.py` for payload serialization and
  generic line-appending helpers.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (244 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing whether remaining specialized appenders
  (plain-text stream append and JSONL append callsites) can share a single file-append primitive
  end-to-end without reducing clarity or changing output contract.
- Completed the queued append-primitive audit in `src/femic/pipeline/vdyp_logging.py` by adding a
  shared internal file-append helper (`_append_text_fragment(...)`) and rewiring both
  `append_line(...)` and `append_text(...)` to consume it.
- Preserved output contracts: `append_line(...)` still appends newline-terminated records and
  `append_text(...)` still appends exact text fragments.
- Expanded deterministic coverage in `tests/test_vdyp_logging.py` with
  `test_append_text_appends_without_overwriting` to guard append-vs-overwrite behavior.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (245 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing remaining direct append-file writes
  outside `vdyp_logging`/`append_line` callsites and centralizing them only where behavior can
  remain byte-for-byte unchanged.
- Completed the queued direct-append audit across production Python paths (`src/`,
  `00_data-prep.py`, `01a_run-tsa.py`, `01b_run-tsa.py`): no remaining direct file-append writes
  exist outside `src/femic/pipeline/vdyp_logging.py`.
- Confirmed the only append-file primitive in production code is now
  `_append_text_fragment(...)` via `append_line(...)`/`append_text(...)`; no behavior-preserving
  rewires were needed in this slice.
- Completed validation gate after this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (245 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing duplicated newline/stream framing usage
  around legacy subprocess output (`run_legacy_subprocess` and VDYP batch stream capture) and
  centralizing safe formatting seams without altering emitted log text.
