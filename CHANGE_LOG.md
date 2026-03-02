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
