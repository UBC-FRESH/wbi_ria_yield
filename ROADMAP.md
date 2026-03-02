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
