# Change Log

## 2026-02-24
- Added the `femic` Typer CLI scaffold under `src/femic` with stub commands and module entry point.
- Added `typer` and `rich` to `requirements.txt` to support the new CLI.
- Created `ROADMAP.md` (moved from planning) with phased refactor tasks, a Next Focus list, and detailed next steps.
- Added `AGENTS.md` contributor operating notes.
- Added `pyproject.toml` with a `femic` console script entrypoint and verified `python -m femic --help` works in the venv.
- Wired `femic run` to the legacy `00_data-prep.py` pipeline with `--tsa`/`--resume` overrides and resume-aware skips.
- Fixed the legacy workflow wrapper to locate `00_data-prep.py` from the repo root.
- Added preflight checks in `femic run` for Wine, VDYP assets, and required data inputs.
- Made `--resume` skip the AU/curve table rebuild when cached model input bundle CSVs exist.
- Replaced downstream bundle naming with `model_input_bundle` (no legacy auto-copy).
- Removed legacy `data/spadescbm_bundle` directory.
- Normalized TSA codes to zero-padded strings when loading data to avoid `KeyError: '08'`.
- Added a fail-fast guard with null-summary diagnostics when AU assignment yields no rows.
- Rebuilt `scsi_au` from the bundle `au_table` on resume to restore AU lookups.
- Added a `--debug-rows` CLI option to limit VRI input rows for faster debugging.
- Re-applied debug row limiting after checkpoint reloads to keep the dataset small.
- Fixed debug row helper ordering so early checkpoint loads can call it.
- Skipped strata without VDYP curves to prevent failures in debug runs.
- Disabled cached checkpoint/output reuse when debug rows are enabled.
- Resolved external dataset paths relative to the repo root (`../data`).
- Added `FEMIC_EXTERNAL_DATA_ROOT` override for external dataset locations.
- Fixed raster masking calls to pass geometry lists for MultiPolygon support.

## 2026-02-26
- Guarded AU/curve assignment against missing stratum+SI mappings and emit a warning summary before
  dropping unmapped rows.
- Documented missing AU/curve mapping behavior in the README and roadmap notes.

## 2026-02-28
- Added `planning/VDYP_debug_notes.md` capturing missing-curve causes and VDYP fragility notes.
- Expanded the roadmap with VDYP diagnostics + metadata hardening tasks.
- Added VDYP run diagnostics with JSONL logs and extra preflight checks for the Wine runner.
- Added curve-fit diagnostics plus toe-fit auto-trimming with warning fallback logging.
- Documented VDYP diagnostic log locations in the README and roadmap notes.
- Switched curve anchoring to quasi-origin `(1, 1e-6)` to preserve positive-value filtering.
- Added pre-VDYP TSA prep checkpoints (`data/vdyp_prep-tsa{tsa}.pkl`) for warm-start debugging.
- Made pre-VDYP checkpoint serialization robust by removing non-picklable fit-function closures.
- Added missing validation scaffolding (`tests/`, `docs/`, `.pre-commit-config.yaml`) so required
  repo checks run successfully.
- Completed a TSA 08 rerun and verified curve-event logs record quasi-origin points
  (`first_age=1.0`, `first_volume=1e-06`).
- Added `femic vdyp report` (new `src/femic/vdyp/reporting.py`) to summarize VDYP JSONL diagnostics,
  including status/stage/phase counts, parse errors, and first-point anchor conformance.
- Added fallback handling in `run_vdyp(nsamples=\"auto\")` for small strata (`n < min_samples`) to run
  all available records instead of failing with `AssertionError`.
- Added extra missing-output guards in curve smoothing/TIPSY input stages so absent
  stratum+SI VDYP outputs emit warning events and do not crash immediately.
- Forced a fresh TSA 08 debug rerun (`--debug-rows 500`) and captured populated diagnostics:
  `vdyp_runs.jsonl` (77 events) and `vdyp_curve_events.jsonl` (26 events).

## 2026-03-01
- Hardened `process_vdyp_out` against sparse/degenerate curve inputs by falling back to a
  quasi-origin-anchored curve with warning metadata instead of crashing on empty MAI/argmax
  calculations.
- Updated VDYP stratum+SI registration so `scsi_au`/`au_scsi` entries are created only for combos
  that survive operability/species filters and have usable VDYP results.
- Hardened AU/curve table assembly in `00_data-prep.py` to skip VDYP curve combos missing AU
  mappings and print a summarized warning instead of raising `KeyError`.
- Re-ran a forced fresh TSA 08 debug run (`femic run --tsa 08 --resume --debug-rows 500`) to
  verify progress; run now completes end-to-end with populated diagnostics
  (`vdyp_runs.jsonl`: 77 events, `vdyp_curve_events.jsonl`: 27 events).
- Replaced most row-wise `swifter.apply(...)` usage with pandas `.apply(...)` by default
  (optional opt-in via `FEMIC_USE_SWIFTER=1`) to reduce nondeterministic debug-run behavior.
- Added `FEMIC_DISABLE_IPP` control (default enabled) so debug runs do not depend on an
  ipyparallel controller.
- Added `FEMIC_SKIP_STANDS_SHP` control and defaulted it to on during debug runs to skip final
  TSA shapefile export while iterating.
- Investigated persistent end-of-run `sys.excepthook` noise; message still appears despite
  successful run completion (`exit code 0`), but no longer blocks pipeline outputs/log generation.
- Updated `CITATION.cff` repository metadata URL to
  `https://github.com/UBC-FRESH/wbi_ria_yield`.
- Fixed `fit_stratum` row selection to keep DataFrame shape (`f_.loc[[sc]]`) and prevent
  singleton-stratum `KeyError: np.False_` failures in SI filtering.
- Added empty-species safeguards in TIPSY input assembly: stratum+SI combinations with no
  species candidates now emit `no_species_candidates` warnings and are skipped instead of
  raising `IndexError`.
- Made `swifter` import lazy in `00_data-prep.py` so monkeypatching is only enabled when
  `FEMIC_USE_SWIFTER=1`, reducing side effects in default debug runs.
- Changed `run_data_prep` to run `00_data-prep.py` in a subprocess and stream filtered output,
  eliminating persistent non-fatal legacy shutdown noise from normal `femic run` logs.
- Reviewed and reconciled roadmap next-focus status:
  marked completed items for README quickstart and VDYP diagnostics hardening,
  updated NF2a wording to reflect subprocess execution, and added new NF7/NF8 work queues
  for operator-facing run artifacts and deterministic regression checks.
- Added `femic run` options `--run-id` and `--log-dir`, propagated through the legacy wrapper as
  `FEMIC_RUN_ID` and `FEMIC_LOG_DIR`.
- Added per-run manifest emission at `run_manifest-<run_id>.json` with command metadata,
  options, env flags, TSA list, checkpoint presence, and expected run-scoped log paths.
- Switched VDYP diagnostic outputs to run-scoped TSA files:
  `vdyp_runs-tsa{tsa}-{run_id}.jsonl` and `vdyp_curve_events-tsa{tsa}-{run_id}.jsonl`.
- Added deterministic TSA08 VDYP regression fixtures and tests for stable summary counts.
- Added warning-budget guardrails in `femic vdyp report` with threshold flags
  (`--max-curve-warnings`, `--max-first-point-mismatches`, parse-error maxima, and minimum event
  counts) and non-zero exit on budget violations.
- Added raw VDYP process stream artifact capture per TSA/run:
  `vdyp_stdout-tsa{tsa}-{run_id}.log` and `vdyp_stderr-tsa{tsa}-{run_id}.log`.
- Expanded run manifest payloads with runtime/package versions, resolved key paths, and
  per-TSA artifact existence inventory for run/curve JSONL and stdout/stderr artifacts.
- Reconciled Phase 1 roadmap checkboxes with completed NF deliverables so roadmap state now shows
  Phase 1 complete and Phase 2 as the active next implementation frontier.
- Started Phase 2 extraction by adding `src/femic/pipeline/{io,vdyp,tsa,plots}.py` helper modules.
- Updated legacy workflow to consume shared pipeline helpers for TSA normalization, run-path
  resolution, and VDYP artifact log path construction.
- Added unit tests for new pipeline helper modules and updated manifest tests to import shared
  VDYP path builders.
- Replaced hardcoded default TSA list in pipeline helpers with dev-config-driven defaults from
  `config/dev.toml` (`[run].default_tsa_list`), using `["08"]` fallback for local testing.
- Added `PipelineRunConfig` and `build_pipeline_run_config` so `femic run` now passes explicit
  typed run settings from CLI to legacy workflow wrapper (first `P2.1b` seam).
- Added `LegacyExecutionPlan` and `build_legacy_execution_plan` so legacy subprocess command/env/
  path/checkpoint resolution is centralized in pipeline helpers instead of inline workflow code.
- Added `femic.pipeline.stages.run_legacy_subprocess` plus tests, and refactored legacy workflow
  to call this stage executor for filtered subprocess streaming.
- Added `femic.pipeline.manifest` and moved run-manifest payload/version/file-write logic out of
  workflow wrapper into reusable helpers; updated workflow/tests to consume the new module.
- Added `femic.pipeline.pre_vdyp` to centralize pre-VDYP checkpoint serialization/load/save and
  refactored `01a_run-tsa.py` to use these helpers; added dedicated unit tests.
- Removed the redundant roadmap `Next Focus` section after folding completed items into phase
  status/checklist tracking.
- Added `femic.pipeline.vdyp_io` for shared VDYP infile writer and output table parser helpers,
  refactored `01a_run-tsa.py` to consume them, and added unit tests.
- Added `femic.pipeline.vdyp_sampling.nsamples_from_curves` and refactored legacy auto-sampling
  loop to call this helper; added focused unit tests for empty and finite-result cases.
- Added `femic.pipeline.vdyp_logging` for run-id resolution, run-scoped VDYP log paths, and JSONL/
  text append helpers; refactored `01a_run-tsa.py` to consume these helpers and added unit tests.
- Updated `femic.pipeline.vdyp.build_vdyp_log_paths` to reuse
  `femic.pipeline.vdyp_logging.build_tsa_vdyp_log_paths`, removing duplicate VDYP artifact filename
  construction logic.
- Added `femic.pipeline.vdyp_curves` with reusable quasi-origin anchoring, toe-fill, and
  `process_vdyp_out` helpers; refactored `01a_run-tsa.py` to consume this module and added focused
  unit tests for empty-input and toe-fit-fallback behavior.
- Added `femic.pipeline.tipsy` with shared VDYP-derived scalar helpers
  (`compute_vdyp_site_index`, `compute_vdyp_oaf1`) and refactored TSA-specific TIPSY parameter
  builders in `01a_run-tsa.py` to use these helpers; added dedicated unit tests.
- Added `evaluate_tipsy_candidate` and `build_tipsy_warning_event` to
  `femic.pipeline.tipsy`, and refactored `01a_run-tsa.py` TIPSY AU selection to consume these
  helpers for centralized eligibility checks and standardized warning-event payloads.
- Added draft TIPSY manual-handoff config scaffolding in `config/tipsy/` (`README.md` and
  `template.tsa.yaml`) and documented the human-in-the-loop TIPSY boundary in `README.md`,
  including variability expectations across legacy TSA rule implementations.
- Added `femic.pipeline.tipsy_config` with TSA YAML loading/validation and config-rule parameter
  generation, plus optional runtime wiring in `01a_run-tsa.py` to use
  `config/tipsy/tsa{tsa}.yaml` (or `.yml`) when present (legacy in-code dict logic remains fallback).
- Added `config/tipsy/tsa08.yaml` as the first concrete TSA migration to config-driven TIPSY rules,
  and extended config assignment resolution to support dynamic tokens like
  `$leading_species_tipsy` for legacy-compatible species normalization (`SX -> SW`).
- Added `config/tipsy/tsa16.yaml` as a second concrete migration (capturing higher-complexity
  multi-species/GW assignment logic) and expanded tests to validate repo-backed TSA16 config loading
  and rule selection.
- Added `config/tipsy/tsa24.yaml` with BEC-dependent branching (`SBS`/`ESSF`) translated from legacy
  rules, and expanded tests to validate repo-backed TSA24 rule selection for both branches.
- Added `config/tipsy/tsa40.yaml` and `config/tipsy/tsa41.yaml`, completing migration coverage for
  the original five TSA rule examples, and extended config token resolution with
  `$species_rank_<n>_tipsy` / `$species_pct_<n>` for dynamic species composition assignments.
- Updated legacy run behavior to require TSA YAML TIPSY config by default (fail-fast when missing),
  with explicit opt-in fallback to legacy in-code dispatch via `FEMIC_TIPSY_USE_LEGACY=1`; added a
  test asserting all five migrated TSA config files are present/loadable.
- Added `femic tipsy validate` CLI command to validate config-driven TIPSY handoff files
  (`config/tipsy/tsaXX.yaml`) and report missing requested TSAs before pipeline execution.
- Reduced notebook-script global coupling at the 00/01a/01b stage boundary by changing
  `01a_run-tsa.run_tsa(...)` and `01b_run-tsa.run_tsa(...)` to accept explicit runtime args, and
  updating `00_data-prep.py` to pass these values directly instead of setting `tsa`/`stratum_col`
  module globals before invocation.
- Replaced broad legacy module namespace injection (`__dict__.update(globals())`) with explicit,
  validated context binding through `femic.pipeline.legacy_context.bind_legacy_module_context(...)`
  plus scoped 01a/01b symbol allowlists, and added tests for the new binder.
- Extracted VDYP batch prep/run/import orchestration into new
  `femic.pipeline.vdyp_stage.execute_vdyp_batch(...)` helper and rewired `01a_run-tsa.py` to call
  this stage seam for subprocess execution + structured run logging.
- Added `tests/test_vdyp_stage.py` coverage for success, parse-error, and timeout behavior of the
  extracted VDYP stage helper.
- Extracted bootstrap dispatch orchestration into
  `femic.pipeline.vdyp_stage.execute_bootstrap_vdyp_runs(...)` and rewired the `force_run_vdyp`
  branch in `01a_run-tsa.py` to use the shared helper for per-stratum SI run-context logging and
  result accumulation.
- Extended `tests/test_vdyp_stage.py` with bootstrap success and dispatch-error coverage.
- Extracted curve-smoothing dispatch orchestration into
  `femic.pipeline.vdyp_stage.execute_curve_smoothing_runs(...)` and rewired `01a_run-tsa.py` to
  consume returned smoothed-curve records for `vdyp_smoothxy` table assembly and downstream plot
  overlays.
- Extended `tests/test_vdyp_stage.py` with curve-smoothing coverage for missing-output warning
  logging and per-curve kwarg-override propagation.
- Extracted legacy VDYP overlay plotting into
  `femic.pipeline.vdyp_stage.plot_curve_overlays(...)` and rewired `01a_run-tsa.py` to delegate
  per-stratum overlay plotting through this shared helper.
- Reduced the explicit 01a legacy context allowlist by removing stale symbols no longer used after
  stage extraction (`Path`, `curve_fit`, `shlex`, `subprocess`).
- Extended `tests/test_vdyp_stage.py` with overlay-plot orchestration assertions for plot calls and
  axis/legend behavior.
- Extracted smooth-curve table assembly/write into
  `femic.pipeline.vdyp_stage.build_smoothed_curve_table(...)` and rewired `01a_run-tsa.py` to use
  this helper for consolidated DataFrame construction + feather persistence.
- Reduced `RUN_01A_CONTEXT_SYMBOLS` further by dropping no-longer-used symbols
  (`_curve_fit`, `wraps`) after curve-table helper extraction.
- Extended `tests/test_vdyp_stage.py` with `build_smoothed_curve_table(...)` coverage for assembled
  rows and output write callback behavior.
- Extracted VDYP result-resolution branching into
  `femic.pipeline.vdyp_stage.load_or_build_vdyp_results_tsa(...)` and rewired `01a_run-tsa.py` to
  use this helper for force-run/bootstrap, per-TSA cache loads, combined-cache fallback, and cache
  persistence.
- Reduced `RUN_01A_CONTEXT_SYMBOLS` again by removing stale `pickle` dependency after migrating
  cache/load orchestration into the shared stage helper.
- Extended `tests/test_vdyp_stage.py` with `load_or_build_vdyp_results_tsa(...)` coverage for
  force-run, TSA-cache, combined-cache, and compat-loader fallback paths.
- Extracted VDYP polygon/layer table loading into
  `femic.pipeline.vdyp_stage.load_vdyp_input_tables(...)` and rewired `01a_run-tsa.py` to use this
  shared loader instead of inline source/feather branch logic.
- Reduced `RUN_01A_CONTEXT_SYMBOLS` again by removing stale `gpd` dependency after input-table
  loader extraction.
- Extended `tests/test_vdyp_stage.py` with `load_vdyp_input_tables(...)` coverage for feather-cache
  reads and source-geodatabase load+persist behavior.
- Added `femic.pipeline.vdyp_stage.build_curve_fit_adapter(...)` and rewired `01a_run-tsa.py` to
  build a local `curve_fit` adapter from `curve_fit_impl`, centralizing legacy
  `maxfev -> max_nfev` compatibility handling.
- Removed obsolete `wraps_impl` argument plumbing from `01a_run-tsa.run_tsa(...)` and the
  `00_data-prep.py` `run_tsa(...)` callsite.
- Extended `tests/test_vdyp_stage.py` with `build_curve_fit_adapter(...)` coverage for
  `maxfev` translation and existing `max_nfev` passthrough behavior.
- Reduced additional legacy global-state coupling by extending `01a_run-tsa.run_tsa(...)` with
  explicit path/export arguments (`vdyp_results_*`, `vdyp_input_pandl_path`,
  `vdyp_{ply,lyr}_feather_path`, `tipsy_params_columns`, `tipsy_params_path_prefix`) and passing
  these from `00_data-prep.py`.
- Trimmed `RUN_01A_CONTEXT_SYMBOLS` to remove now-redundant path/export globals after the signature
  handoff refactor.
- Extended `01a_run-tsa.run_tsa(...)` to accept mutable run-state/data inputs explicitly
  (`results`, `vdyp_results`, `vdyp_curves_smooth`, `scsi_au`, `au_scsi`, `tipsy_params`,
  `si_levelquants`, `species_list`, `vdyp_curves_smooth_tsa_feather_path_prefix`) and passed these
  from `00_data-prep.py`.
- Trimmed `RUN_01A_CONTEXT_SYMBOLS` again so context binding now only injects baseline runtime
  helper modules/flags instead of per-run dataset/state payload variables.
- Converted `01b_run-tsa.run_tsa(...)` to accept explicit runtime data inputs
  (`results`, `au_scsi`, `tipsy_curves`, `vdyp_curves_smooth`) with direct argument passing from
  `00_data-prep.py`.
- Removed all 01b legacy context payload requirements by setting `RUN_01B_CONTEXT_SYMBOLS = ()`
  and localizing `matplotlib.pyplot`/`seaborn` imports inside `01b_run-tsa.py`.
- Extracted TIPSY table assembly/export logic into `femic.pipeline.tipsy`
  (`build_tipsy_input_table`, `write_tipsy_input_exports`) and rewired `01a_run-tsa.py` to
  delegate xlsx/dat output generation through these helpers.
- Extended `tests/test_tipsy.py` with coverage for TIPSY export helper behavior (row assembly,
  empty-input error, and output file writes).
- Extracted config-vs-legacy TIPSY builder selection into
  `femic.pipeline.tipsy_config.resolve_tipsy_param_builder(...)` and rewired `01a_run-tsa.py` to
  use this shared resolver instead of inline branch logic.
- Extended `tests/test_tipsy_config.py` with resolver coverage for config-preferred, forced-legacy,
  and missing-config failure behavior.
- Localized `distance`/`itertools`/`operator`/`os` imports inside `01a_run-tsa.run_tsa(...)`,
  removing these requirements from injected legacy context.
- Trimmed `RUN_01A_CONTEXT_SYMBOLS` accordingly; 01a context now only injects
  `_femic_resume_effective`, `kwarg_overrides`, `np`, `pd`, `plt`, and `sns`.
- Extracted TIPSY candidate-selection/AU-assignment orchestration into
  `femic.pipeline.tipsy.build_tipsy_params_for_tsa(...)` and rewired `01a_run-tsa.py` to delegate
  eligibility filtering, warning logging, and `scsi_au`/`au_scsi`/`tipsy_params` map updates.
- Added explicit runtime arguments to `01a_run-tsa.run_tsa(...)` for
  `resume_effective`, `force_run_vdyp`, and `kwarg_overrides_for_tsa`, with direct argument passing
  from `00_data-prep.py`.
- Localized `numpy`/`pandas`/`matplotlib`/`seaborn` imports inside `01a_run-tsa.run_tsa(...)` and
  reduced `RUN_01A_CONTEXT_SYMBOLS` to `()`, eliminating required 01a context injection.
- Extended `tests/test_tipsy.py` with `build_tipsy_params_for_tsa(...)` coverage for success,
  missing-VDYP warning, and no-species warning paths.
- Extracted legacy in-code TIPSY rule implementations and exclusion setup from `01a_run-tsa.py`
  into `femic.pipeline.tipsy_legacy` and rewired 01a to consume
  `build_tipsy_exclusion()`/`get_legacy_tipsy_builders()` from this module.
- Added `tests/test_tipsy_legacy.py` with coverage for legacy TSA key dispatch, exclusion-map
  presence, and baseline TSA08 builder output fields.
- Added legacy-context regression tests asserting `RUN_01A_CONTEXT_SYMBOLS` and
  `RUN_01B_CONTEXT_SYMBOLS` are empty and that binding with an empty required-symbol list is a
  no-op.
- Removed `bind_legacy_module_context(...)` callsites and related legacy-context imports from
  `00_data-prep.py` now that both 01a/01b required-symbol lists are empty.
- Removed the inactive `if 0:` duplicate TIPSY export branch in `01a_run-tsa.py`, leaving the
  helper-driven export path (`build_tipsy_input_table` + `write_tipsy_input_exports`) as the single
  active flow.
- Removed `legacy_context` symbol re-exports from `femic.pipeline.__init__` to reflect current
  runtime behavior (no required legacy context injection path in the active orchestration flow).
- Removed additional inactive `if 0:` notebook-era debug/reload blocks from `00_data-prep.py`
  (manual checkpoint rollback/cache/load snippets and dormant shapefile export path) to reduce dead
  code around active orchestration logic.
- Added `tests/test_legacy_orchestration_wiring.py` AST-based regression checks that enforce explicit
  01a/01b `run_tsa(...)` keyword handoff arguments and verify no
  `bind_legacy_module_context(...)` call remains in `00_data-prep.py`.
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
  checks (wine/bin/params), default log-path resolution, run-event logging, batch execution, and
  sampling orchestration handoff.
- Rewired `01a_run-tsa.py` bootstrap execution to call `run_vdyp_for_stratum(...)` directly and
  removed nested `run_vdyp`/`_tsa_log_path` definitions from `run_tsa(...)`.
- Extended `tests/test_vdyp_stage.py` with `run_vdyp_for_stratum(...)` coverage and updated
  `tests/test_legacy_01a_structure.py` guardrails to assert 01a no longer calls
  `run_vdyp_sampling(...)` directly and no longer defines nested `run_vdyp`.
- Added `femic.pipeline.vdyp_stage.build_run_vdyp_for_stratum_runner(...)`, a reusable helper that
  binds per-TSA runtime context (`tsa`, `run_id`, VDYP tables, fit hooks, and run-log paths) into
  a bootstrap-compatible `run_vdyp_fn(sample_table, **kwargs)` callable.
- Rewired `01a_run-tsa.py` bootstrap flow to build `run_vdyp_fn` through
  `build_run_vdyp_for_stratum_runner(...)`, removing inline lambda assembly of
  `run_vdyp_for_stratum(...)` kwargs from `run_tsa(...)`.
- Extended `tests/test_vdyp_stage.py` with forwarding/binding coverage for the new runner-builder
  helper, and updated `tests/test_legacy_01a_structure.py` guardrails to assert 01a calls the
  builder helper and no longer calls `run_vdyp_for_stratum(...)` directly.
- Added `femic.pipeline.vdyp_stage.build_bootstrap_vdyp_results_runner(...)`, a reusable helper
  that binds per-TSA bootstrap dispatch inputs into a zero-argument callback compatible with
  `load_or_build_vdyp_results_tsa(...)`.
- Rewired `01a_run-tsa.py` to pass `run_bootstrap_fn` produced by
  `build_bootstrap_vdyp_results_runner(...)`, removing inline
  `run_bootstrap_fn=lambda: execute_bootstrap_vdyp_runs(...)` closure assembly.
- Extended `tests/test_vdyp_stage.py` with coverage for bootstrap-runner binding/forwarding and
  updated `tests/test_legacy_01a_structure.py` guardrails to assert 01a uses the builder helper
  and does not pass an inline lambda to `run_bootstrap_fn`.
- Added `femic.pipeline.vdyp_stage.build_fit_stratum_curves_runner(...)`, a reusable helper that
  binds stratum-fit context into `compile_one_fn(stratumi, sc)` callbacks for
  `compile_strata_fit_results(...)`.
- Rewired `01a_run-tsa.py` to build/pass `compile_one_fn` via
  `build_fit_stratum_curves_runner(...)`, removing inline fit-call closure assembly in the pre-VDYP
  compilation path.
- Extended `tests/test_vdyp_stage.py` with fit-runner binding coverage and updated
  `tests/test_legacy_01a_structure.py` guardrails so 01a must call the builder helper and must not
  pass inline lambdas to `compile_one_fn`.
- Extracted legacy notebook fit functions from `01a_run-tsa.py` into
  `femic.pipeline.vdyp_curves` (`legacy_fit_func1`, `legacy_fit_func1_bounds_func`,
  `legacy_fit_func2`, `legacy_fit_func2_bounds_func`) and rewired 01a to consume these shared
  helpers.
- Extended `tests/test_vdyp_curves.py` with deterministic checks for legacy fit-function outputs and
  bounds, and updated `tests/test_legacy_01a_structure.py` guardrails to assert 01a no longer
  defines nested legacy fit functions.
- Added `femic.pipeline.tsa.apply_stratum_alias_map(...)` to encapsulate selected-strata retention
  and alias-fallback assignment for `*_matched` stratum columns.
- Rewired `01a_run-tsa.py` to call `apply_stratum_alias_map(...)` for stratum matching, removing
  the final nested helper definition (`match_stratum`) from `run_tsa(...)`.
- Extended `tests/test_pipeline_helpers.py` with deterministic alias-application coverage and
  updated `tests/test_legacy_01a_structure.py` guardrails to assert 01a calls the helper and has no
  nested `match_stratum`.
- Added `femic.pipeline.vdyp_stage.CurveSmoothingPlotConfig` and
  `build_curve_smoothing_plot_config(...)` to centralize legacy curve-smoothing plot defaults
  (plot toggle, `figsize`, palette setup, `palette_flavours`, `alphas`) behind a shared stage
  helper seam.
- Rewired `01a_run-tsa.py` curve-smoothing overlay path to call
  `build_curve_smoothing_plot_config(...)` and consume returned defaults instead of defining inline
  smoothing plot/palette constants.
- Extended `tests/test_vdyp_stage.py` with deterministic defaults coverage for the new helper and
  updated `tests/test_legacy_01a_structure.py` guardrails to assert 01a calls this helper and no
  longer assigns inline smoothing `palette_flavours`/`alphas` constants.
- Removed dead `legacy_fit_func2`/`legacy_fit_func2_bounds_func` imports and local
  `fit_func2`/`fit_func2_bounds_func` assignments from `01a_run-tsa.py`; these values were no
  longer consumed by active stage paths.
- Added `tests/test_legacy_01a_structure.py` guardrails asserting `run_tsa(...)` no longer assigns
  local legacy fit2 bindings.
- Removed inline TIPSY staging constant assignments from `01a_run-tsa.py`
  (`min_operable_years`, `si_iqrlo_quantile`, local `verbose`) and now rely on
  `build_tipsy_params_for_tsa(...)` shared defaults.
- Extended `tests/test_legacy_01a_structure.py` with guardrails asserting 01a no longer assigns
  these constants inline and does not override corresponding
  `build_tipsy_params_for_tsa(...)` keyword defaults.
- Extended `CurveSmoothingPlotConfig` / `build_curve_smoothing_plot_config(...)` to include overlay
  axis defaults (`xlim`, `ylim`) and rewired `01a_run-tsa.py` to pass
  `smooth_plot_cfg.xlim`/`smooth_plot_cfg.ylim` to `plot_curve_overlays(...)` instead of inline
  tuple literals.
- Extended `tests/test_vdyp_stage.py` defaults coverage for new axis config fields and added
  `tests/test_legacy_01a_structure.py` AST guardrails asserting overlay axes are sourced from
  `smooth_plot_cfg`.
- Added `StrataDistributionPlotConfig` and `build_strata_distribution_plot_config(...)` in
  `femic.pipeline.plots` to centralize 01a stratum-distribution plotting defaults.
- Rewired the 01a stratum-distribution plotting block to consume
  `build_strata_distribution_plot_config(...)` values instead of inline constants.
- Extended `tests/test_pipeline_helpers.py` with defaults coverage for the new helper and added AST
  guardrails in `tests/test_legacy_01a_structure.py` asserting 01a calls the helper and no longer
  assigns inline strata-plot constants.
- Rewired `01a_run-tsa.py` strata diagnostic plot output writes to call
  `femic.pipeline.plots.strata_plot_paths(...)` and save to helper-provided PDF/PNG paths instead
  of inline `"plots/strata-tsa%s.*"` literals.
- Added AST guardrails in `tests/test_legacy_01a_structure.py` asserting 01a calls
  `strata_plot_paths(...)` and no longer embeds inline strata output path literals.
- Added `femic.pipeline.plots.resolve_strata_plot_ordering(...)` to centralize
  abundance-vs-lexical stratum ordering for distribution plots.
- Rewired `01a_run-tsa.py` to call `resolve_strata_plot_ordering(...)`, removing the inline
  `sort_lex` branch and local ordering assembly.
- Extended `tests/test_pipeline_helpers.py` with deterministic ordering coverage for default and
  lexical modes, and added AST guardrails in `tests/test_legacy_01a_structure.py` asserting 01a
  calls the helper and no longer assigns local `sort_lex`.
- Added `femic.pipeline.plots.plot_strata_site_index_diagnostics(...)` to encapsulate early 01a
  stratum diagnostics plotting (`site_index_median` histogram + abundance-vs-SI scatter).
- Rewired `01a_run-tsa.py` to call `plot_strata_site_index_diagnostics(...)` and removed direct
  inline histogram/scatter plotting calls from `run_tsa(...)`.
- Extended `tests/test_pipeline_helpers.py` with deterministic coverage for this helper and added
  AST guardrails in `tests/test_legacy_01a_structure.py` asserting 01a calls the helper and no
  longer invokes direct `plt.scatter(...)` for this stage.
- Added `femic.pipeline.plots.render_strata_distribution_plot(...)` to encapsulate 01a stratum
  distribution rendering (barplot + violinplot + labels + xlim + PDF/PNG writes).
- Rewired `01a_run-tsa.py` to call `render_strata_distribution_plot(...)`, removing direct inline
  seaborn bar/violin calls and save-path plumbing from `run_tsa(...)`.
- Extended `tests/test_pipeline_helpers.py` with deterministic coverage for the new rendering helper
  and added AST guardrails in `tests/test_legacy_01a_structure.py` asserting 01a calls the helper
  and no longer performs direct `sns.barplot(...)`/`sns.violinplot(...)` calls in this stage.
- Added `femic.pipeline.tipsy_config.resolve_tipsy_runtime_options(...)` to centralize
  `FEMIC_TIPSY_CONFIG_DIR`/`FEMIC_TIPSY_USE_LEGACY` environment resolution.
- Rewired `01a_run-tsa.py` to call `resolve_tipsy_runtime_options(...)` instead of reading
  `os.environ` directly for TIPSY config/legacy flags.
- Extended `tests/test_tipsy_config.py` with defaults/override coverage for the new helper and
  added AST guardrails in `tests/test_legacy_01a_structure.py` asserting 01a no longer reads
  `os.environ` directly for this stage.
- Added `StratumFitRunConfig` and `build_stratum_fit_run_config(...)` in
  `femic.pipeline.vdyp_stage` to centralize pre-VDYP stratum fit-stage defaults.
- Rewired `01a_run-tsa.py` pre-VDYP fit compilation path to consume
  `build_stratum_fit_run_config(...)` instead of assigning fit-stage constants inline.
- Extended `tests/test_vdyp_stage.py` with defaults coverage for the new helper and added AST
  guardrails in `tests/test_legacy_01a_structure.py` asserting 01a calls the helper and no longer
  assigns inline stratum fit-stage constants.
- Added `femic.pipeline.pre_vdyp.pre_vdyp_checkpoint_path(...)` to centralize per-TSA pre-VDYP
  checkpoint path construction.
- Rewired `01a_run-tsa.py` to call `pre_vdyp_checkpoint_path(...)` instead of constructing
  `"./data/vdyp_prep-tsa%s.pkl"` inline.
- Extended `tests/test_pre_vdyp.py` with path-helper coverage and added AST guardrails in
  `tests/test_legacy_01a_structure.py` asserting 01a calls the helper and no longer embeds
  `vdyp_prep-tsa` literals.

## 2026-03-02
- Added `femic.pipeline.vdyp.build_vdyp_cache_paths(...)` to centralize per-TSA cache path
  templates for `vdyp_results-tsa*.pkl` and `vdyp_curves_smooth-tsa*.feather`.
- Rewired `01a_run-tsa.py` to source per-TSA cache artifact paths via
  `build_vdyp_cache_paths(...)` instead of inline `%`-formatted string templates.
- Expanded helper/guardrail coverage:
  `tests/test_pipeline_helpers.py` now validates `build_vdyp_cache_paths(...)`, and
  `tests/test_legacy_01a_structure.py` asserts 01a calls the helper and no longer assigns inline
  VDYP cache path templates.
- Removed local `os.path` checks from `01a_run-tsa.py` in favor of `Path(...).is_file()` for
  checkpoint/cache existence checks, reducing stale local import coupling.
- Added an AST guardrail in `tests/test_legacy_01a_structure.py` asserting `run_tsa(...)` no longer
  imports `os` locally for path checks.
- Ran full required validation gate successfully:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (154 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Updated the Phase 2 task checklist in `ROADMAP.md` with explicit `P2.1b` subtask status
  (cache-path extraction done, local path-check cleanup done, remaining handoff/signature reduction
  still queued).
- Queued the next execution batch in roadmap notes:
  `vdyp_cache_paths` payload handoff from 00->01a, `run_tsa(...)` argument surface reduction via
  typed config payload, and extraction of 00_data-prep 01a/01b module-load orchestration helpers.
- Added `Legacy01ARuntimeConfig` in `src/femic/pipeline/legacy_runtime.py` and rewired
  `01a_run-tsa.run_tsa(...)` to consume this typed runtime payload instead of a long list of
  individual path/runtime parameters.
- Collapsed 00->01a VDYP cache handoff to a single `vdyp_cache_paths` payload built in
  `00_data-prep.py` via `build_vdyp_cache_paths(...)` and passed through runtime config.
- Added shared legacy orchestration helpers in `src/femic/pipeline/stages.py`:
  `load_legacy_module(...)` and `run_legacy_tsa_loop(...)`, and rewired 00_data-prep 01a/01b loops
  to use them.
- Added direct-script import fallback in `00_data-prep.py` that prepends `src/` when needed so
  `python 00_data-prep.py` can resolve `femic.pipeline` helpers without requiring prior editable
  install.
- Expanded tests and guardrails:
  `tests/test_pipeline_stages.py` now covers new stage helpers,
  `tests/test_legacy_orchestration_wiring.py` validates runtime-config + shared helper wiring, and
  `tests/test_legacy_01a_structure.py` checks cache-path reads from `runtime_config`.
- Added reusable stage-setup helpers in `src/femic/pipeline/stages.py`:
  `initialize_legacy_tsa_stage_state(...)`, `prepare_tsa_index(...)`, and
  `should_skip_if_outputs_exist(...)`.
- Added `build_legacy_01a_runtime_config(...)` in `src/femic/pipeline/legacy_runtime.py` so
  00_data-prep no longer assembles the 01a runtime payload inline.
- Rewired `00_data-prep.py` to use these helpers for stage-state initialization, TSA index setup,
  resume output-skip checks, and 01a runtime-config construction.
- Expanded tests:
  `tests/test_pipeline_stages.py` now covers the new setup/runtime helpers and
  `tests/test_legacy_orchestration_wiring.py` asserts 00-data-prep wiring uses these helper seams.
- Added `src/femic/pipeline/bundle.py` to centralize model-input bundle pathing and I/O helpers
  (`resolve_bundle_paths`, `bundle_tables_ready`, `load_bundle_tables`, `write_bundle_tables`,
  `ensure_scsi_au_from_table`).
- Rewired 00_data-prep post-01b bundle orchestration to consume shared bundle helpers for
  resume-time bundle reads, path wiring, CSV writes, and `scsi_au` backfill.
- Added `tests/test_bundle.py` with deterministic coverage for bundle path readiness, table
  load/write behavior, TSA normalization, and `scsi_au` reconstruction from AU tables.
- Expanded `tests/test_legacy_orchestration_wiring.py` guardrails to assert 00_data-prep calls
  bundle helper seams.
- Added `build_bundle_tables_from_curves(...)` and `BundleAssemblyResult` to
  `src/femic/pipeline/bundle.py`, extracting the heavy AU/curve table assembly loop from
  00_data-prep into a reusable helper.
- Rewired 00_data-prep to call `build_bundle_tables_from_curves(...)` and consume returned
  diagnostics for missing AU mappings while preserving existing warning output behavior.
- Expanded `tests/test_bundle.py` with deterministic coverage for managed/unmanaged curve assembly
  and missing AU-mapping diagnostics.
- Extended `tests/test_legacy_orchestration_wiring.py` guardrails to assert
  `build_bundle_tables_from_curves(...)` seam usage in 00_data-prep.
- Added residual post-bundle strata helpers in `src/femic/pipeline/tsa.py`:
  `assign_stratum_matches_from_au_table(...)` and
  `assign_si_levels_from_stratum_quantiles(...)`.
- Rewired 00_data-prep to use these helpers for stratum matching against AU-table strata and SI
  level assignment by quantile bands, replacing the corresponding inline loops.
- Expanded `tests/test_pipeline_helpers.py` with deterministic coverage for both new TSA helpers.
- Extended `tests/test_legacy_orchestration_wiring.py` guardrails to assert
  `assign_stratum_matches_from_au_table(...)` and
  `assign_si_levels_from_stratum_quantiles(...)` seam usage in 00_data-prep.
- Added AU assignment/null-diagnostics helpers to `src/femic/pipeline/tsa.py`:
  `lookup_scsi_au_base`, `assign_au_ids_from_scsi`, `summarize_missing_au_mappings`,
  `build_au_assignment_null_summary`, and `validate_nonempty_au_assignment`.
- Rewired the 00_data-prep AU assignment stage to consume these helpers, removing inline
  `_lookup_scsi_au` / `au_from_scsi` logic and preserving warning + fail-fast behavior.
- Expanded `tests/test_pipeline_helpers.py` with deterministic AU helper coverage and updated
  `tests/test_legacy_orchestration_wiring.py` guardrails to assert AU helper seam usage.
- Added `assign_curve_ids_from_au_table(...)` to `src/femic/pipeline/bundle.py` to centralize
  managed/unmanaged curve ID assignment from AU table records.
- Rewired 00_data-prep to call `assign_curve_ids_from_au_table(...)` instead of inline
  `assign_curve1`/`assign_curve2` function definitions and row-wise assignments.
- Expanded `tests/test_bundle.py` with deterministic curve-id assignment coverage and updated
  `tests/test_legacy_orchestration_wiring.py` guardrails to assert
  `assign_curve_ids_from_au_table(...)` seam usage.
- Added `assign_thlb_area_and_flag(...)` to `src/femic/pipeline/tsa.py` to centralize THLB area and
  THLB binary-flag assignment rules.
- Rewired 00_data-prep to call `assign_thlb_area_and_flag(...)` instead of inline `thlb_area` and
  `assign_thlb` functions.
- Expanded `tests/test_pipeline_helpers.py` with deterministic THLB helper coverage and updated
  `tests/test_legacy_orchestration_wiring.py` guardrails to assert
  `assign_thlb_area_and_flag(...)` seam usage.
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
