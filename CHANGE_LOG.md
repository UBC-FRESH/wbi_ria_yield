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

## 2026-03-02
- Completed the queued append-primitive audit in `src/femic/pipeline/vdyp_logging.py` by adding a
  shared internal file-append helper (`_append_text_fragment(...)`) and rewiring both
  `append_line(...)` and `append_text(...)` to consume it.
- Preserved output contracts: `append_line(...)` still appends newline-terminated records and
  `append_text(...)` still appends exact text fragments.
- Expanded deterministic coverage in `tests/test_vdyp_logging.py` with
  `test_append_text_appends_without_overwriting` to guard append-vs-overwrite behavior.
- Completed validation gate for this slice:
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
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (245 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing duplicated newline/stream framing usage
  around legacy subprocess output (`run_legacy_subprocess` and VDYP batch stream capture) and
  centralizing safe formatting seams without altering emitted log text.
- Completed the queued subprocess/stream-format audit by adding explicit formatting seams for both
  line-forwarded legacy subprocess output and VDYP stream artifact capture.
- Added `stream_filtered_subprocess_output(...)` in `src/femic/pipeline/stages.py` and rewired
  `run_legacy_subprocess(...)` to consume this helper, preserving line text/newline behavior while
  centralizing known-noise filtering.
- Added `build_vdyp_stream_log_block(...)` in `src/femic/pipeline/vdyp_logging.py` and rewired
  `execute_vdyp_batch(...)` (`src/femic/pipeline/vdyp_stage.py`) to use it for both stdout/stderr
  stream block assembly (`header + stream + trailing newline`), removing duplicated inline framing.
- Expanded deterministic coverage in `tests/test_pipeline_stages.py` and
  `tests/test_vdyp_logging.py` for these new stream-formatting helper seams.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (247 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing duplicated VDYP subprocess command-string
  assembly/metadata capture in `execute_vdyp_batch(...)` and centralizing it behind a helper seam
  without changing emitted command text or event fields.
- Completed the queued `execute_vdyp_batch(...)` command/metadata consolidation slice with two
  shared helper seams in `src/femic/pipeline/vdyp_stage.py`:
  `build_vdyp_batch_command(...)` (legacy command-string assembly) and
  `collect_vdyp_batch_run_metadata(...)` (shared returncode/duration/file-size/head capture).
- Rewired `execute_vdyp_batch(...)` to consume these helpers for timeout/error/parse-error/ok
  logging paths while preserving emitted command text and event field shape.
- Expanded deterministic coverage in `tests/test_vdyp_stage.py` for both new helpers, including
  legacy command-string shape and metadata-field extraction behavior.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (249 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing duplicated base-context enrichment in
  VDYP run orchestration (`run_vdyp_for_stratum`, `execute_vdyp_batch`) and centralizing it via a
  helper seam without changing emitted context keys/values.
- Completed the queued VDYP base-context consolidation by adding
  `build_vdyp_run_context(...)` in `src/femic/pipeline/vdyp_stage.py`.
- Rewired both `run_vdyp_for_stratum(...)` and `execute_vdyp_batch(...)` to consume the shared
  context helper so run-id/log-path/bin/params context defaults are centralized while preserving
  existing `setdefault(...)` semantics and emitted context fields.
- Expanded deterministic coverage in `tests/test_vdyp_stage.py` for
  `build_vdyp_run_context(...)`, including default-key population and preservation of
  caller-provided context values.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (251 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing repeated VDYP run-event payload fields
  in `execute_vdyp_batch(...)` (timeout/error/parse_error/ok) and centralizing shared payload
  assembly without changing emitted event keys/values.
- Completed the queued VDYP run-event payload consolidation in
  `src/femic/pipeline/vdyp_stage.py` by adding `build_vdyp_run_event(...)` for shared base field
  assembly (`event/status/phase/feature_count/cache_hits/ply_rows/lyr_rows/cmd/context`).
- Rewired `execute_vdyp_batch(...)` timeout/error/parse_error/ok|empty_output paths to consume
  `build_vdyp_run_event(...)`, preserving emitted event keys/values while removing duplicated
  inline payload assembly.
- Expanded deterministic coverage in `tests/test_vdyp_stage.py` for
  `build_vdyp_run_event(...)`, including int normalization of count fields and passthrough extra
  event fields.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (252 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing duplicated event-emission callsites in
  `execute_vdyp_batch(...)` (`append_jsonl_(vdyp_log_path, ...)`) and centralizing them via a
  local helper seam without changing write order or payload content.
- Completed the queued VDYP event-emission callsite consolidation in
  `src/femic/pipeline/vdyp_stage.py` by adding a local `_emit_run_event(...)` seam inside
  `execute_vdyp_batch(...)`.
- Rewired timeout/error/parse_error/ok|empty_output paths to call `_emit_run_event(...)`, removing
  duplicated `append_jsonl_(vdyp_log_path, ...)` callsites while preserving event payload content
  and emission order.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (252 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing duplicated temporary-file basename/path
  extraction in `execute_vdyp_batch(...)` and centralizing it behind a helper seam without changing
  runtime filenames or downstream parse behavior.
- Completed the queued temporary-file extraction consolidation in
  `src/femic/pipeline/vdyp_stage.py` by adding `VdypBatchTempArtifacts` and
  `resolve_vdyp_batch_temp_artifacts(...)` to centralize basename/path derivation from temp files.
- Rewired `execute_vdyp_batch(...)` to consume resolved temp artifacts for infile writing, command
  assembly, output-table import path resolution, and run-metadata file stats while preserving
  runtime filename behavior.
- Expanded deterministic coverage in `tests/test_vdyp_stage.py` for
  `resolve_vdyp_batch_temp_artifacts(...)` (basename + full-path expectations).
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (253 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing duplicated numeric coercion (`int(...)`)
  across VDYP batch run-event payload construction and consolidating this coercion at one seam
  without changing emitted values.
- Completed the queued VDYP numeric-coercion consolidation by adding
  `VdypRunEventCounts` + `normalize_vdyp_run_event_counts(...)` in
  `src/femic/pipeline/vdyp_stage.py` and routing shared count coercion through this seam.
- Rewired `build_vdyp_run_event(...)` to consume normalized count payloads and updated
  `execute_vdyp_batch(...)` to reuse the same normalized counts for both run-event emission and
  stream-header construction.
- Expanded deterministic coverage in `tests/test_vdyp_stage.py` for
  `normalize_vdyp_run_event_counts(...)` and updated `build_vdyp_run_event(...)` tests to assert
  unchanged emitted values under the new count wrapper.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (254 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing repeated `Path(...)` coercions in VDYP
  helpers (`build_vdyp_batch_command`, `resolve_vdyp_batch_temp_artifacts`,
  `collect_vdyp_batch_run_metadata`) and centralizing only where behavior remains unchanged.
- Completed the queued VDYP path-coercion consolidation by adding `_as_path(...)` in
  `src/femic/pipeline/vdyp_stage.py` and reusing it in:
  `build_vdyp_batch_command(...)`, `resolve_vdyp_batch_temp_artifacts(...)`, and
  `collect_vdyp_batch_run_metadata(...)`.
- Preserved behavior while reducing repeated inline `Path(...)` casts and broadened
  `collect_vdyp_batch_run_metadata(...)` to accept either `str` or `Path` path-like inputs.
- Expanded deterministic coverage in `tests/test_vdyp_stage.py` with a string-path metadata test
  to confirm unchanged size/head extraction behavior across path input types.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (255 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing repeated callable-cast setup in
  `execute_vdyp_batch(...)` and centralizing safe dependency-resolution/cast seams without changing
  runtime defaults or injection points.
- Completed the queued callable-resolution/cast consolidation in
  `src/femic/pipeline/vdyp_stage.py` by adding `VdypBatchExecutionDependencies` and
  `resolve_vdyp_batch_execution_dependencies(...)`.
- Rewired `execute_vdyp_batch(...)` to consume resolved dependency fields
  (`write_vdyp_infiles`, `import_vdyp_tables`, `append_jsonl`, `append_text`,
  `build_stream_header`, `build_stream_log_block`, `subprocess_run`) while preserving default
  runtime imports and explicit injection override behavior.
- Expanded deterministic coverage in `tests/test_vdyp_stage.py` with an injection-preservation test
  for `resolve_vdyp_batch_execution_dependencies(...)`.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (256 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing repeated ephemeral helper closures inside
  `execute_vdyp_batch(...)` (`_emit_run_event`) and promoting reusable pieces where this improves
  clarity without changing event emission semantics or order.
- Completed the queued closure-promotion slice in `src/femic/pipeline/vdyp_stage.py` by replacing
  the local `_emit_run_event` closure with reusable module helper `emit_vdyp_run_event(...)`.
- Rewired `execute_vdyp_batch(...)` timeout/error/parse_error/ok|empty_output branches to call
  `emit_vdyp_run_event(...)`, preserving event payload shape, write order, and log sink behavior.
- Expanded deterministic coverage in `tests/test_vdyp_stage.py` with
  `test_emit_vdyp_run_event_appends_payload` to assert helper emission semantics.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (257 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice: continue P2.2 by auditing repeated `dict(...)` defensive copies in
  VDYP helper seams (`build_vdyp_run_context`, `build_vdyp_run_event`) and centralizing copy policy
  where clarity improves without mutability regressions.
- Closed P2.2c by adding shared stage executor `execute_legacy_tsa_stage(...)` in
  `src/femic/pipeline/stages.py` and rewiring `00_data-prep.py` 01a/01b orchestration to use
  explicit kwargs builders (`_build_01a_run_kwargs`, `_build_01b_run_kwargs`) instead of inline
  module-load + per-TSA run-loop plumbing.
- Updated orchestration wiring guardrails in `tests/test_legacy_orchestration_wiring.py` to assert
  helper-driven 01a/01b dispatch and preserved explicit keyword handoff payloads.
- Added stage-helper regression coverage in `tests/test_pipeline_stages.py` for
  `execute_legacy_tsa_stage(...)` success and missing-symbol failure behavior.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (259 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice (ASAP closure path): finish `P2.1b` by eliminating remaining
  implicit/global state handoff at 00->01a/01b boundaries, then close `P2.2a`/`P2.2b` with
  explicit major-step wrappers and thin orchestration sequencing.
- Reduced remaining `P2.1b` implicit-state handoff by removing `globals().get(...)` runtime
  injection in `00_data-prep.py` for 01a runtime config (`vdyp_out_cache`, `curve_fit_impl`) and
  replacing it with explicit stage-level variables passed through `_build_01a_run_kwargs(...)`.
- Added AST guardrail coverage in `tests/test_legacy_orchestration_wiring.py` to assert no
  `globals().get(...)` orchestration handoff remains.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (260 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice (ASAP closure path): continue `P2.1b` by auditing remaining 01b
  hard-coded runtime paths and introducing explicit runtime config handoff (mirroring 01a-style
  typed runtime payload) to eliminate residual implicit file-path globals at stage boundaries.
- Closed remaining `P2.1b` boundary implicitness by introducing `Legacy01BRuntimeConfig` +
  `build_legacy_01b_runtime_config(...)` in `src/femic/pipeline/legacy_runtime.py` and wiring
  explicit runtime handoff from `00_data-prep.py` into `01b_run-tsa.py`.
- Refactored `01b_run-tsa.py` to require typed `runtime_config` and consume shared TIPSY path
  helpers (`tipsy_params_excel_path`, `tipsy_stage_output_paths`) plus runtime output-root/template
  settings instead of hard-coded stage-path literals.
- Extended orchestration/runtime guardrails in `tests/test_legacy_orchestration_wiring.py` and
  `tests/test_pipeline_stages.py` for 01b runtime config builder usage and explicit handoff.
- Marked `P2.1b` complete: 00->01a/01b stage boundaries now pass typed runtime payloads and no
  longer rely on implicit `globals().get(...)` runtime injection.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (261 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice (ASAP closure path): close `P2.2a` by wrapping the largest remaining
  major orchestration block in `00_data-prep.py` (post-01b bundle + AU/curve assignment segment)
  behind a shared helper with explicit inputs/outputs, then sequence it under `P2.2b`.
- Closed `P2.2a` by wrapping the largest remaining post-01b orchestration block in
  `00_data-prep.py` behind explicit input/output helper
  `_run_post_01b_bundle_and_curve_assignment_stage(...)`, including bundle load/build,
  stratum/AU assignment, curve-id mapping, and checkpoint writes.
- Stage output handoff is now explicit (`f`, `au_table`, `curve_table`, `curve_points_table`),
  removing the last large inline notebook-style block from top-level execution flow.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest` (261 passed),
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice (ASAP closure path): close `P2.2b` by adding one thin
  top-level orchestration function in `00_data-prep.py` that sequences the extracted stage calls
  with explicit intermediate payload handoff and minimal side effects.
- Closed `P2.2b` by adding `_run_legacy_tsa_orchestration_stage(...)` in `00_data-prep.py` to
  sequence 01a stage execution, 01b stage execution, and post-01b bundle/AU/curve assignment under
  one explicit handoff seam.
- Removed remaining inline top-level sequencing calls for 01a/01b and bundle-path stage dispatch;
  stage outputs now flow through the orchestration helper return payload.
- Marked `P2.2` complete in `ROADMAP.md` now that `P2.2a`/`P2.2b`/`P2.2c` are all closed.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest`,
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice (ASAP closure path): start `P2.3a` with smoke tests for extracted
  core helpers (path/validation and key deterministic transforms) to lock in current behavior before
  Phase 3 workflow hardening.
- Started and closed `P2.3a` by extending smoke coverage with CLI preflight file-validation tests
  (`tests/test_cli_main.py`) and lightweight transform smoke checks for TSA normalization/checkpoint
  path building (`tests/test_smoke.py`).
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest`,
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice (ASAP closure path): start `P2.3b` by adding deterministic,
  small-sample assertions for one or two extracted core helpers where behavior contracts are
  currently implicit (without expanding runtime-heavy legacy integration scope).
- Closed `P2.3b` with deterministic, small-sample CLI preflight assertions in
  `tests/test_cli_main.py`, including exact missing-required-file failure behavior and stable error
  classification under controlled repo layouts.
- Marked `P2.3` complete in `ROADMAP.md` now that both `P2.3a` and `P2.3b` are closed.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest`,
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice (ASAP closure path): begin Phase 3 (`P3.1a`) by validating and
  tightening Sphinx config/package surface (theme/extensions/autosummary defaults) now that Phase 2
  modularization + minimal helper test coverage are complete.
- Closed `P3.1a` by upgrading `docs/conf.py` with explicit extension defaults
  (`sphinx.ext.autodoc`, `sphinx.ext.autosummary`, `sphinx.ext.napoleon`,
  `sphinx.ext.viewcode`) plus optional enablement for `nbsphinx` and
  `sphinx_rtd_theme` when installed in the environment.
- Added `autosummary_generate = True`, notebook-checkpoint exclusions, and resilient theme/static
  settings so docs builds stay warning-clean under `-W` even when optional packages are absent.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest`,
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice (ASAP closure path): continue `P3.1` with `P3.1b` by adding
  `docs/reference/cli.rst` and wiring `docs/index.rst` to mirror current CLI help surface.
- Closed `P3.1b` by replacing the docs placeholder index with a real reference toctree and adding
  `docs/reference/cli.rst` containing the current `python -m femic --help` command/option surface
  (top-level plus `run`, `prep`, `vdyp`, `tsa`, and `tipsy` subcommand entries).
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest`,
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice (ASAP closure path): close `P3.1c` with a GitHub Pages docs build
  workflow that runs Sphinx in CI and publishes `_build/html`.
- Closed `P3.1c` by adding `.github/workflows/docs-pages.yml` with PR/push docs build, strict
  `sphinx-build -W` gating, artifact upload, and deploy-to-Pages on pushes to `main`.
- Marked `P3.1` complete in `ROADMAP.md` now that docs config, reference content, and Pages CI
  publishing are all in place.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest`,
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice (ASAP closure path): start `P3.2a` by mapping current `femic` CLI
  commands/subcommands to a draft Nemora task taxonomy table in docs.
- Closed `P3.2a` by adding `docs/reference/nemora-task-map.rst` and wiring it into docs index
  to map current CLI entries (`run`, `prep run`, `vdyp run/report`, `tsa run`,
  `tipsy validate`) to draft Nemora task keys.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest`,
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice (ASAP closure path): close `P3.2b` by inventorying extracted shared
  utilities and tagging top upstream candidates (diagnostics/logging/path/runtime helpers).
- Closed `P3.2b` by adding `docs/reference/nemora-upstream-candidates.rst` and wiring it into docs
  index with a prioritized inventory of extracted helper modules suitable for Nemora upstreaming.
- Marked `P3.2` complete in `ROADMAP.md` now that CLI taxonomy mapping and upstream-candidate
  inventory are both in place.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest`,
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice (ASAP closure path): start `P3.3a` by adding a first config file
  schema for selecting TSA/mode flags and mapping it into existing run option parsing.
- Closed `P3.3a` by adding YAML/JSON run-profile loading
  (`load_pipeline_run_profile(...)`) and explicit CLI/profile merge logic
  (`resolve_effective_run_options(...)`) for `femic run` TSA/strata/mode selection.
- Added `--run-config` support in `femic run`, a template profile at
  `config/run_profile.example.yaml`, and reference docs for schema/precedence in
  `docs/reference/run-config.rst`.
- Added deterministic coverage for run-profile loading/validation and CLI integration in
  `tests/test_pipeline_helpers.py` and `tests/test_cli_main.py`.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest`,
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice (ASAP closure path): close `P3.3b` by extending run manifest payload
  metadata with profile/config provenance and versioned output-root annotations.
- Closed `P3.3b` by extending run metadata through `PipelineRunConfig`/`LegacyExecutionPlan` with
  output-root + config provenance fields and surfacing them in manifest payload sections
  (`config_provenance`, `outputs`, and output-root option/path annotations).
- Added manifest/run-config coverage updates in `tests/test_pipeline_helpers.py` and
  `tests/test_legacy_manifest.py` plus SHA256 helper coverage for profile provenance digests.
- Marked `P3.3` complete in `ROADMAP.md` now that config selection/mode wiring and
  manifest/version metadata are both in place.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest`,
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice (ASAP closure path): start `P3.4a` by auditing bootstrap/sample
  randomness seams and introducing explicit seed controls where stochastic behavior still exists.
- Closed `P3.4a` by adding explicit deterministic seed controls across VDYP sampling helpers:
  `run_vdyp_sampling(...)`, `run_vdyp_for_stratum(...)`, and bootstrap dispatch sequencing with
  per-stratum/SI derived seeds.
- Added `FEMIC_SAMPLING_SEED` env support for deterministic bootstrap/sample draws and coverage in
  `tests/test_vdyp_stage.py` for fixed-seed sampling stability and per-dispatch seed derivation.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest`,
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice (ASAP closure path): close `P3.4b` by ensuring run manifests capture
  full runtime/tool version metadata consistently for config-driven and non-config runs.
- Closed `P3.4b` by extending manifest payload runtime metadata capture with an explicit
  `runtime_parameters` block and seed/config provenance fields (`FEMIC_SAMPLING_SEED`,
  `FEMIC_RUN_CONFIG_*`, output-root metadata).
- Added regression assertions in `tests/test_legacy_manifest.py` for runtime-parameter sections and
  seed/config provenance values.
- Marked `P3.4` complete in `ROADMAP.md` now that deterministic seed control and runtime
  parameter/version metadata capture are both implemented.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest`,
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice (ASAP closure path): start `P3.5a` by updating README workflow docs
  to reflect run-config profiles, manifest provenance fields, and deterministic sampling controls.
- Closed `P3.5a` by updating `README.md` workflow documentation for config-driven runs
  (`--run-config`), deterministic sampling control (`FEMIC_SAMPLING_SEED`), and manifest metadata
  sections used for reproducibility/audit.
- Closed `P3.5b` by adding a concise end-to-end quickstart flow in `README.md` covering
  CLI help check, TIPSY config validation, single-TSA run, and VDYP diagnostics reporting.
- Marked `P3.5` complete in `ROADMAP.md` now that workflow handoff docs and quickstart are in
  place.
- Completed validation gate for this slice:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest`,
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W`.
- Queued next extraction slice (ASAP closure path): run a final roadmap consistency pass and
  prepare branch for merge/deployment handoff.
- Completed final roadmap consistency pass: all Phase 1/2/3 checklist items are now checked,
  including parent closeout for `P2.1` (its sub-items were already complete).
- Branch is ready for merge/deployment handoff.
- Added `planning/TSA29_dataset_compile_plan.md` with an explicit runbook for compiling TSA 29,
  including the required `config/tipsy/tsa29.yaml` gate, config-driven run steps, diagnostics, and
  completion criteria.
- Debugged TSA29 TIPSY config mismatch and rebuilt ruleset for functional AU coverage:
  `config/tipsy/tsa29.yaml` now uses a catch-all matching rule (`when: {}`) with
  `Density=1400` and `SPP_1=$leading_species_tipsy`.
- Added null defaults for optional TIPSY schema fields (`SPP_2..5`, `PCT_2..5`, `GW_*`,
  `GW_age_*`) so table projection to `data/tipsy_params_columns` succeeds for every AU.
- Re-ran the TSA29 TIPSY stage directly from cached outputs and regenerated
  `data/tipsy_params_tsa29.xlsx` and `data/02_input-tsa29.dat` (30 AU rows).
- Current blocker moved downstream to manual BatchTIPSY handoff (`04_output-tsa29.out`) before 01b
  and final bundle assembly can be validated.
- Added `femic tsa post-tipsy` command to run downstream stages only (01b + bundle assembly)
  after manual BatchTIPSY output is uploaded.
- Implemented `run_post_tipsy_bundle(...)` in `src/femic/workflows/legacy.py` to:
  load cached TSA prep/smoothed-curve artifacts, execute 01b per TSA, and rebuild
  `data/model_input_bundle/{au_table,curve_table,curve_points_table}.csv`.
- Added regression tests:
  `tests/test_workflows_post_tipsy.py` (workflow output assembly) and
  `tests/test_cli_main.py` (CLI command behavior and wiring).
- Updated user docs for the new downstream recovery command in `README.md` and
  `docs/reference/cli.rst`.
- Added `.gitignore` coverage for generated `vdyp_io` scratch files:
  `vdyp_err_*.err`, `vdyp_out_*.out`, `vdyp_ply_*.csv`, `vdyp_lyr_*.csv`, and `tmp*`.
  This removes hundreds of transient artifacts from normal `git status` output.
- Added `.gitignore` entries for volatile local runtime files under `vdyp_io/VDYP_CFG`
  (`VDYP7_BACK.ctl`, `VDYP7_VDYP.ctl`, `vdyp7.log`) and removed them from git tracking index so
  local model execution no longer dirties the branch on every run.
- Cleaned up 01b downstream runtime warnings:
  switched TIPSY output parsing to `sep="\\s+"` (pandas deprecation fix), pre-sorted VDYP
  stratum/SI index before per-AU lookups, and closed each Matplotlib figure after save to avoid
  open-figure buildup warnings during large TSA runs.
- Added manifest/audit logging for `femic tsa post-tipsy` runs via
  `run_post_tipsy_bundle_with_manifest(...)`, including run status, duration, runtime metadata, and
  output artifact existence checks.
- Extended `femic tsa post-tipsy` with `--run-id` and `--log-dir`, and now prints the generated
  manifest path (e.g., `vdyp_io/logs/run_manifest-<run_id>.json`).
- Added regression coverage for post-tipsy manifest emission and updated CLI/docs references.
- Tuned `config/tipsy/tsa29.yaml` from a single catch-all rule to ordered provisional
  BEC/species-group pathways (pine/fir/spruce/balsam) with explicit species mixes, density, DBH
  utility thresholds, and modest GW settings; retained a final catch-all for full AU coverage.
- Added TSA29-specific regression checks in `tests/test_tipsy_config.py` for representative
  MS-pine and IDF-fir rule matching behavior.
- Regenerated TSA29 TIPSY input artifacts (`data/tipsy_params_tsa29.xlsx`,
  `data/02_input-tsa29.dat`) from cached pipeline outputs using the tuned ruleset.
- Upgraded TSA29 parameterization from provisional tuning to TSR-anchored assumptions by extracting
  guidance from Williams Lake TSA data packages:
  `reference/29ts_dpkg_2024-2.pdf` (Section 8.5) and
  `reference/williams_lake_tsa_data_package-2.pdf` (Section 6.3 Tables 23–25).
- Reworked `config/tipsy/tsa29.yaml` rule assignments for pine/fir/spruce/balsam pathways with
  explicit planted-vs-natural proportions, regen delays, species mixes, densities, and GW values
  tied to TSR assumptions; retained fallback coverage.
- Updated TSA29 expectations in `tests/test_tipsy_config.py` to match the new rules.
- Fixed a resumed-run bug in `src/femic/pipeline/vdyp_stage.py` where
  `geopandas.read_feather(...)` crashed on plain Feather caches lacking geo metadata by adding a
  pandas fallback for both polygon/layer cache loads.
- Forced TSA29 01a rerun and regenerated `data/02_input-tsa29.dat` under the new ruleset
  (same 30 AU rows, materially updated per-AU parameters).
- Added custom management-unit boundary support to run profiles:
  `selection.boundary_path`, `selection.boundary_layer`, `selection.boundary_code` now parse
  through `PipelineRunProfile`/`PipelineRunConfig` and are exported as `FEMIC_BOUNDARY_*`.
- Updated `00_data-prep.py` boundary ingestion to support custom geometry masks:
  in boundary mode FEMIC reads the provided layer, unions geometry, validates requested run code
  coverage, and clips VRI extraction to that geometry.
- Added K3Z case scaffolding:
  `config/run_profile.k3z.yaml`, `config/tipsy/tsak3z.yaml`, and
  `planning/K3Z_dataset_compile_plan.md`.
- Extended TIPSY config discovery and validation to support named case codes
  (for example `tsak3z.yaml`) in addition to numeric TSA files.
- Removed numeric-only TSA assumptions in AU/curve ID paths by adding deterministic named-code
  prefixing in `src/femic/pipeline/bundle.py` and `src/femic/pipeline/tsa.py`.
- Added/updated coverage in `tests/test_pipeline_helpers.py`, `tests/test_tipsy_config_cli.py`,
  and `tests/test_bundle.py` for profile boundary fields, named TIPSY configs, and named-case
  bundle ID behavior.
- Executed K3Z smoke run (`--debug-rows 20`) successfully through full legacy workflow with
  missing-BatchTIPSY fallback, producing manifest
  `vdyp_io/logs/run_manifest-k3z_smoke5_20260304_221317.json` and K3Z step-1a artifacts
  (`data/02_input-tsak3z.dat`, `data/tipsy_params_tsak3z.xlsx`).
- Hardened config-driven TIPSY planted-row mix normalization in
  `src/femic/pipeline/tipsy_config.py`:
  `SX -> SW` normalization across species slots, planted broadleaf removal with share
  reallocation, dominant-species-first slot ordering, and exact integer `%` rounding to 100.
- Added regression tests in `tests/test_tipsy_config.py` for normalized mix behavior and TSA29
  expectations (no planted `AT`/`SX` in `f` rows, dominant species in `SPP_1`, sum of
  `PCT_1..PCT_5 == 100`).
- Completed validation gate for this slice:
  `.venv/bin/ruff format src tests`, `.venv/bin/ruff check src tests`,
  `.venv/bin/mypy src`, `.venv/bin/pytest`, `.venv/bin/pre-commit run --all-files`.
- Installed `pandas-stubs` into `.venv` to satisfy strict `mypy src` import-typing requirements.
- TSA29 full rerun remains pending due run-path stall/noise during heavy `FEMIC_NO_CACHE=1`
  data-prep stage; immediate next action is deterministic regeneration of step-1a outputs and
  BatchTIPSY revalidation.
- Added config-driven SI offset support for TIPSY rule assignments in
  `src/femic/pipeline/tipsy_config.py`:
  per-side `SI_offset`/`si_offset` can be declared in config defaults or per-rule assignments,
  and is applied as an additive adjustment to computed VDYP SI before row export.
- Updated `config/tipsy/tsa29.yaml` to include `defaults.f.SI_offset: 2.0`, enabling a
  managed-side +2 SI bump directly from config (no manual `.dat` edits required).
- Added regression coverage in `tests/test_tipsy_config.py` for side-specific SI offset
  behavior and updated TSA29 expected SI values under the new +2 managed offset.
- Regenerated TSA29 step-1a artifacts from cached TSA29 prep data with the new config:
  `data/tipsy_params_tsa29.xlsx` and `data/02_input-tsa29.dat`.
- Completed validation gate for this slice:
  `.venv/bin/ruff format src tests`, `.venv/bin/ruff check src tests`,
  `.venv/bin/mypy src`, `.venv/bin/pytest`, `.venv/bin/pre-commit run --all-files`.
- Extended TIPSY config SI tuning to support linear transforms in
  `src/femic/pipeline/tipsy_config.py` via `SI_c1` and `SI_c2` (with lowercase aliases).
  Final SI is now computed per side as:
  `SI_final = SI_c1 * SI_baseline + SI_c2` (plus legacy additive `SI_offset` if present).
- Updated TSA29 config to linear-form managed SI bump in `config/tipsy/tsa29.yaml`:
  `defaults.f.SI_c1: 1.0`, `defaults.f.SI_c2: 2.0` (equivalent to previous fixed +2 offset).
- Added regression coverage in `tests/test_tipsy_config.py` for linear SI transform behavior.
- Updated TIPSY config docs/templates with SI transform guidance:
  `config/tipsy/README.md`, `config/tipsy/template.tsa.yaml`.
- Revalidated and regenerated TSA29 step-1a outputs under linear-form config:
  `data/tipsy_params_tsa29.xlsx` and `data/02_input-tsa29.dat` (matches the prior manual +2
  scenario).
- Completed validation gate for this slice:
  `.venv/bin/ruff format src tests`, `.venv/bin/ruff check src tests`,
  `.venv/bin/mypy src`, `.venv/bin/pytest`, `.venv/bin/pre-commit run --all-files`,
  `.venv/bin/sphinx-build -b html docs _build/html -W`.
- Added TSA29 VDYP override in `src/femic/pipeline/vdyp_overrides.py` for
  `("SBPS_PL", "L"): {"skip1": 50}` to correct pathological unmanaged curve behavior in AU 21005.
- Added default VDYP fit diagnostic plot output in `src/femic/pipeline/vdyp_stage.py` during
  smoothing runs:
  `plots/vdyp_fitdiag_tsaXX-<stratumi>-<stratum>-<si>.png` now overlays observed 5-year binned
  median/IQR with the fitted best-fit curve for visual QA.
- Re-ran TSA29 01a/01b and post-tipsy stages; AU 21005 unmanaged curve changed from a pathological
  early spike (max 943.91 at age 19) to a coherent trajectory (max 96.29 at age 223).
- Generated targeted AU21005 diagnostics:
  `plots/diag_au21005_fit_check.png` and companion CSVs for observed bins/current/candidate curve
  comparison.
- Completed validation gate for this slice:
  `.venv/bin/ruff format src tests`, `.venv/bin/ruff check src tests`,
  `.venv/bin/mypy src`, `.venv/bin/pytest`, `.venv/bin/pre-commit run --all-files`.
- Expanded VDYP fit-comparison diagnostics:
  `src/femic/pipeline/vdyp_curves.py` now supports right-tail sigma asymmetry and optional
  right-tail linear blend controls; `src/femic/pipeline/vdyp_stage.py` now computes and overlays
  `current`, `sigma_asym`, `tail_blend`, and conditionally validated `auto_skip` candidates on
  each `plots/vdyp_fitdiag_tsaXX-*.png`.
- Added heuristic auto left-tail anomaly handling in smoothing runs:
  infer a suggested `skip1` from early-age overshoot, rerun candidate fit, and only surface it
  when strict quality gates improve baseline (`rmse`, `tail_rmse`, `early_overshoot`).
- Ran TSA29 targeted smoothing directly from cached TSA artifacts and regenerated
  `data/vdyp_curves_smooth-tsa29.feather` plus 30 fitdiag PNGs with multi-flavour overlays.
- Added quantitative comparison artifact
  `plots/vdyp_fitdiag_tsa29_metrics_compare.csv` (30 stratum+SI rows):
  best RMSE counts = tail blend 18, sigma asymmetry 9, current 3;
  best tail-RMSE counts = sigma asymmetry 18, tail blend 9, current 3.
  Auto-skip was suggested for 18 curves but validated for 0 under current acceptance criteria.
- Refined VDYP improved-fit comparison workflow to drop the sigma-asymmetry candidate from
  default diagnostics and focus on current-vs-tail-blend evaluation.
- Reworked right-tail blending in `src/femic/pipeline/vdyp_curves.py`:
  the tail logic now auto-detects the maximal rightmost near-linear binned segment
  (`R²` + normalized-RMSE gates), fits the main NLLS body on the left as before, and blends into
  the detected linear tail. When no acceptable linear segment exists, tail override is skipped.
- Added configurable linear-tail detection controls:
  `tail_linear_min_points`, `tail_linear_min_r2`, `tail_linear_max_nrmse`.
- Updated fitdiag overlays in `src/femic/pipeline/vdyp_stage.py` to display only:
  `current`, `tail_blend`, and validated `auto_skip`.
- Regenerated TSA29 curve-smoothing artifacts and diagnostics from cached TSA inputs:
  `data/vdyp_curves_smooth-tsa29.feather` and 30 refreshed
  `plots/vdyp_fitdiag_tsa29-*.png` files.
- Added tail-focused summary artifact
  `plots/vdyp_fitdiag_tsa29_metrics_tail_only.csv`:
  tail blend improved overall RMSE on 17/30 curves and tail RMSE on 17/30 curves
  (auto-skip still suggested in 18 curves under current heuristic).
- Diagnosed residual tail-blend regressions: detector could still pick early-age
  pseudo-linear segments when no acceptable late-age segment existed, leading to severe errors.
- Updated `src/femic/pipeline/vdyp_curves.py` linear-tail selection to require
  preferred-age candidates (`tail_linear_prefer_min_age`, default 200) and return no blend when
  none exist (instead of dropping to non-preferred segments).
- Added tests in `tests/test_vdyp_curves.py` for:
  1) no-blend behavior when no linear/preferred segment is available, and
  2) preference for late linear segments when present.
- Re-ran TSA29 diagnostic smoothing with the revised heuristic and regenerated
  `plots/vdyp_fitdiag_tsa29-*.png` plus refreshed
  `plots/vdyp_fitdiag_tsa29_metrics_tail_only.csv`.
- Post-fix metrics: catastrophic tail-blend outliers were removed; worst RMSE regression dropped
  to ~0.045 (from prior multi-unit failures), while preserving blend improvements where suitable
  late-age linear tails exist.
- Ran a relaxed-linearity tuning pass to address missed long near-linear late tails:
  updated stage-level candidate settings to
  `tail_linear_min_r2=0.82`, `tail_linear_max_nrmse=0.12`,
  `tail_linear_prefer_min_age=190.0`.
- Regenerated TSA29 diagnostics (`plots/vdyp_fitdiag_tsa29-*.png`) and refreshed
  `plots/vdyp_fitdiag_tsa29_metrics_tail_only.csv`.
- Relaxed thresholds increased detected blended tails from 22/30 to 26/30 curves.
  Resulting quality tradeoff remained bounded (no catastrophic regressions), with
  `tail_better_rmse=15/30`, `tail_better_tail_rmse=15/30`, and worst observed
  `ΔRMSE ~ +0.67` (`IDF_PL-H`).
- Added detailed implementation summary document:
  `planning/VDYP_curve_fit_enhancements_2026-03-05.md`, including history, current controls,
  observed metrics, and explicit follow-up note to keep tuning tail-fit hyperparameters later.
- Updated VDYP fit diagnostics to include raw per-sample VDYP trajectories as faint grey lines
  (low-alpha) behind binned summaries/fitted curves in
  `src/femic/pipeline/vdyp_stage.py`, for teaching/demo visualization of raw -> smoothed workflow.
- Re-ran full K3Z case with updated curve-fit/plotting stack:
  `--run-id k3z_curvefit_enh_20260305`; run completed and wrote manifest
  `vdyp_io/logs/run_manifest-k3z_curvefit_enh_20260305.json`.
- Generated updated K3Z fitdiag outputs:
  `plots/vdyp_fitdiag_tsak3z-*.png` (9 plots for available VDYP strata/SI combinations).
- Ran K3Z end-to-end with user-provided BatchTIPSY output by mapping
  `data/02_output-tsak3z.out` to the runtime-expected `data/04_output-tsak3z.out`
  and executing:
  `python -m femic run --run-config config/run_profile.k3z.yaml -v --resume --run-id k3z_posttipsy_20260306_062442`.
- Run finished `status=ok` (manifest:
  `vdyp_io/logs/run_manifest-k3z_posttipsy_20260306_062442.json`) and regenerated current K3Z
  post-TIPSY outputs, including `plots/strata-tsak3z.png`,
  `plots/tipsy_vdyp_tsak3z-*.png`, `data/tipsy_params_tsak3z.xlsx`,
  and `data/tipsy_curves_tsak3z.csv`.
- Fixed K3Z strata diagnostics bug where `build_strata_summary(...)` could return NaN
  abundance/coverage rows after `min_standcount` filtering by:
  1) keeping filtered frames as `.copy()` and
  2) falling back to unfiltered top strata when small custom-boundary runs would
     otherwise filter out all strata.
- Improved strata plotting robustness in `src/femic/pipeline/plots.py`:
  abundance ordering now falls back from `totalarea_p` to `coverage`,
  SI axes auto-expand to observed min/max values, and sparse-point strip overlays are
  drawn on top of violin plots for low-sample strata.
- Added `tipsy_vdyp_ylim_for_tsa(...)` and wired `01b_run-tsa.py` to use it;
  K3Z TIPSY-vs-VDYP comparison plots now use a `0..1500` y-axis range.
- Added regression tests in `tests/test_pipeline_helpers.py` covering:
  small-boundary standcount fallback behavior, K3Z y-limit helper behavior,
  and stripplot invocation in strata distribution rendering.
- Re-ran K3Z end-to-end with fixes:
  `python -m femic run --run-config config/run_profile.k3z.yaml -v --run-id k3z_plotfix_20260306_063833`;
  run completed `status=ok` (manifest:
  `vdyp_io/logs/run_manifest-k3z_plotfix_20260306_063833.json`) with corrected
  strata diagnostics (`coverage 1.0`) and refreshed K3Z outputs.
- Scoped K3Z strata selection to top 4 strata by area by adding
  `TARGET_NSTRATA_BY_TSA["k3z"] = 4` in `src/femic/pipeline/tsa.py`.
- Updated K3Z downstream unmanaged-curve selection so comparison plots use
  tail-blend curves when available:
  `src/femic/pipeline/vdyp_stage.py::execute_curve_smoothing_runs(...)` now writes
  tail-blend output for `tsa == "k3z"` into `vdyp_curves_smooth-tsak3z.feather`
  (fitdiag visualization still shows current + candidate overlays).
- Added tests:
  `tests/test_pipeline_helpers.py` asserts `target_nstrata_for("k3z") == 4`;
  `tests/test_vdyp_stage.py` validates K3Z tail-blend output preference.
- Deleted stale K3Z plot artifacts (`plots/*tsak3z*`) and recompiled K3Z from scratch:
  `python -m femic run --run-config config/run_profile.k3z.yaml -v --run-id k3z_n4_tailblend_20260306_064902`.
  Run completed `status=ok` (manifest:
  `vdyp_io/logs/run_manifest-k3z_n4_tailblend_20260306_064902.json`) with
  step-1a diagnostics now showing `count 4` and `coverage 0.9882`.
- Implemented adaptive SI split-count logic in `src/femic/pipeline/tsa.py` from per-stratum
  5th-95th percentile SI width:
  `< 5` -> `M` only, `5..10` -> `L/H`, `> 10` -> `L/M/H`.
- Wired the same adaptive SI quantile resolver into VDYP curve fitting
  (`src/femic/pipeline/vdyp_stage.py::fit_stratum_curves`) so fit outputs and AU definitions
  stay aligned for narrow-SI strata.
- Hardened SI assignment and AU mapping for variable split counts:
  `assign_si_levels_from_stratum_quantiles(...)` now supports optional
  `allowed_levels_by_stratum`, and `00_data-prep.py` passes allowed levels inferred from
  `au_table` so post-01b stand assignment cannot request non-existent SI bins.
- Updated TIPSY parameter assembly to tolerate missing per-stratum SI bins cleanly
  (`src/femic/pipeline/tipsy.py::build_tipsy_params_for_tsa` skips absent fit levels).
- Added regression coverage for adaptive split behavior and missing-level handling:
  `tests/test_pipeline_helpers.py`, `tests/test_tipsy.py`, `tests/test_vdyp_stage.py`.
- Re-validated K3Z end-to-end under the adaptive SI split logic:
  `FEMIC_NO_CACHE=1 PYTHONPATH=src .venv/bin/python -m femic run --run-config config/run_profile.k3z.yaml -v --run-id k3z_siwidth_verify_20260306_070055`.
  Run completed `status=ok` (manifest:
  `vdyp_io/logs/run_manifest-k3z_siwidth_verify_20260306_070055.json`) and emitted
  an 8-row K3Z TIPSY input table where `CWH_CW` is correctly split into `L/H` only.
- Updated K3Z comparison plot y-range:
  `src/femic/pipeline/plots.py::tipsy_vdyp_ylim_for_tsa(...)` now returns `(0.0, 2000.0)`
  for `k3z` (previously `(0.0, 1500.0)`), and test expectation was updated in
  `tests/test_pipeline_helpers.py`.
- Fixed fitdiag regeneration behavior in non-resume runs:
  `01a_run-tsa.py` now rebuilds smoothed curves whenever `resume_effective=False`
  instead of only when the smooth-feather cache is missing.
- Hardened fitdiag emission in `src/femic/pipeline/vdyp_stage.py`:
  diagnostic PNGs now emit even when binned observations are unavailable (observed overlays
  are conditional); this prevents silent drop-out of fitdiag files.
- Fixed no-cache VDYP bootstrap reuse:
  `00_data-prep.py` now sets `force_run_vdyp = 1` whenever `_femic_no_cache` is true,
  so stale `data/vdyp_results-tsa*.pkl` cannot be reused during no-cache runs.
- Fixed adaptive-SI bootstrap dispatch bug:
  `src/femic/pipeline/vdyp_stage.py::execute_bootstrap_vdyp_runs(...)` now skips missing/empty
  SI payloads and logs a `status=skipped` event (`missing_or_empty_si_sample`) instead of
  raising `KeyError` when strata have fewer than three SI bins.
- Re-ran full K3Z no-cache pipeline with forced fresh VDYP:
  `FEMIC_NO_CACHE=1 PYTHONPATH=src .venv/bin/python -m femic run --run-config config/run_profile.k3z.yaml -v --run-id k3z_forcevdyp_fix_20260306_072037`.
  Run completed `status=ok` (manifest:
  `vdyp_io/logs/run_manifest-k3z_forcevdyp_fix_20260306_072037.json`) and regenerated
  fresh K3Z artifacts including:
  `data/vdyp_results-tsak3z.pkl` (updated timestamp),
  8 fitdiag plots (`plots/vdyp_fitdiag_tsak3z-*.png`), and
  8 comparison plots (`plots/tipsy_vdyp_tsak3z-*.png`).
- Extracted K3Z stocking parameter guidance from
  `data/bc/cfa/k3z/NICF-LP-Forest-Stewardship-Plan-Appendices-2020.pdf`
  (Appendix B, pages 4-6) and converted `config/tipsy/tsak3z.yaml` from
  placeholder defaults to FSP-informed CWH pathway rules.
- Replaced K3Z TIPSY assumptions with mixed-species, 900 sph pathways keyed by
  leading species group (`CW/YC`, `HW/HM`, `FD/FDC`, `SS/SX`) plus an FSP-style
  fallback rule; all compositions now sum to 100 and avoid single-species
  placeholder stocking.
- Executed refreshed K3Z run with new TIPSY rules:
  `PYTHONPATH=src .venv/bin/python -m femic run --run-config config/run_profile.k3z.yaml -v --run-id k3z_fsp_rules_20260306_073524`.
  Run completed successfully (`status=ok`) with manifest
  `vdyp_io/logs/run_manifest-k3z_fsp_rules_20260306_073524.json`.
- Verified regenerated `data/02_input-tsak3z.dat` now carries the new rule
  outputs (8 AUs, `Density=900`, `Regen_Delay=2`, mixed species such as
  `CW60/HW25/YC15`, `HW70/CW20/FD10`, `FD60/HW25/CW15`).
- Added `planning/CFAK3Z_dataset_compile_plan.md` by cloning the TSA29 planning
  structure and adapting it to K3Z-specific compile constraints, including fixed
  BatchTIPSY field-map handling and small-area stratification caveats.
- Recorded next K3Z refinement experiments in the new plan:
  BEC subzone/variant/phase stratification and top-N leading-species combination
  stratification (N=2 first, then N=3 trial).
- Verified local VRI schema support for these experiments from
  `data/bc/vri/2019/VEG_COMP_LYR_R1_POLY.gdb`:
  `BEC_ZONE_CODE`, `BEC_SUBZONE`, `BEC_VARIANT`, `BEC_PHASE`,
  `SITE_INDEX`, `EST_SITE_INDEX*`, `SPECIES_CD_1..6`, `SPECIES_PCT_1..6`.
- Verified `data/bc/vri/VEG_COMP_LYR_R1_POLY_2024.gdb.zip` is currently corrupt/
  incomplete (`End-of-central-directory signature not found`) and cannot be
  unzipped yet.
- Implemented configurable stratum-key controls in the run-profile pipeline and
  wired them end-to-end into legacy 00-data-prep execution:
  - `selection.stratification.bec_grouping` (`zone|subzone|variant|phase`)
  - `selection.stratification.species_combo_count` (top-N by `SPECIES_PCT_1..6`)
  - `selection.stratification.include_tm_species2_for_single`
  These now flow through `src/femic/pipeline/io.py` -> CLI effective options ->
  legacy env (`FEMIC_STRAT_*`) -> `00_data-prep.py`.
- Refactored `src/femic/pipeline/vri.py` stratum builders to support:
  - BEC grouping levels beyond zone (`subzone`, `variant`, `phase`)
  - Species-combination keys using ranked top-N species shares
  while preserving legacy default behavior for existing TSA runs.
- Updated K3Z profile defaults in `config/run_profile.k3z.yaml` to start from
  finer stratification (`bec_grouping: subzone`, `species_combo_count: 2`) and
  documented new options in `config/run_profile.example.yaml`.
- Updated K3Z planning doc (`planning/CFAK3Z_dataset_compile_plan.md`) with the
  new stratification controls and expected console confirmation output.
- Added/updated regression coverage for new stratification plumbing and behavior:
  `tests/test_vri.py` and `tests/test_pipeline_helpers.py`.
- Validation run status:
  - `.venv/bin/ruff check src tests` passed
  - `.venv/bin/mypy src` passed
  - `.venv/bin/pytest` passed (`312 passed`)
  - `.venv/bin/pre-commit run --all-files` passed
- Switched legacy VRI source auto-resolution to prefer 2024 VRI datasets when available,
  with 2019 fallback preserved for compatibility:
  `bc/vri/2024/VEG_COMP_LYR_R1_POLY_2024.gdb` before
  `bc/vri/2019/VEG_COMP_LYR_R1_POLY.gdb`.
  Implemented in `src/femic/pipeline/io.py::resolve_legacy_external_data_paths(...)`.
- Added startup visibility in `00_data-prep.py` to print the resolved VRI path and TSA
  boundaries path at run start, so active data-source selection is explicit.
- Added regression coverage:
  `tests/test_pipeline_helpers.py::test_resolve_legacy_external_data_paths_prefers_2024_vri_when_available`.
- Validation run status:
  - `.venv/bin/ruff format src tests 00_data-prep.py` passed
  - `.venv/bin/ruff check src tests` passed
  - `.venv/bin/mypy src` passed
  - `.venv/bin/pytest` passed (`313 passed`)
  - `.venv/bin/pre-commit run --all-files` passed
- Extended external source resolution so VRI and VDYP input layers are selected together
  from the same preferred vintage (2024 first, then 2019 fallback):
  - VRI candidates: `bc/vri/2024/VEG_COMP_LYR_R1_POLY_2024.gdb`,
    `bc/vri/2019/VEG_COMP_LYR_R1_POLY.gdb`
  - VDYP input candidates:
    `bc/vri/2024/VEG_COMP_VDYP7_INPUT_POLY_AND_LAYER_2024.gdb`,
    `bc/vri/2019/VEG_COMP_VDYP7_INPUT_POLY_AND_LAYER_2019.gdb`,
    `VEG_COMP_VDYP7_INPUT_POLY_AND_LAYER_2019.gdb`
  Implemented in `src/femic/pipeline/io.py::resolve_legacy_external_data_paths(...)`.
- Updated `00_data-prep.py` to consume the resolved external VDYP input path and print all
  active source paths at runtime:
  - `using VRI source: ...`
  - `using TSA boundaries source: ...`
  - `using VDYP input source: ...`
- Added regression assertions in `tests/test_pipeline_helpers.py` for the new
  `vdyp_input_pandl_path` resolution behavior (including 2024-preferred selection).
- Added a non-fatal guard in `00_data-prep.py` for empty AU-table outcomes after 01b/bundle
  assembly so no-cache exploratory runs can complete and preserve diagnostics even when
  no TIPSY-compatible AU mapping exists.
- Executed fresh 2024 K3Z runs (`k3z_vri2024_refresh2_20260307`,
  `k3z_vri2024_zone1_fixvdyp_20260307`) and confirmed 2024 sources were selected; however,
  VDYP run logs show `empty_output` across bootstrap events, yielding empty smoothed curves
  and an empty `data/02_input-tsak3z.dat` (next debugging target: 2024 VDYP input prep/schema alignment).
- Completed 2024 VDYP ID-domain fix for K3Z:
  in `run_vdyp_for_stratum(...)` (`src/femic/pipeline/vdyp_stage.py`), bootstrap dispatch now
  resolves sampled source `FEATURE_ID`s to the VDYP table key space using `MAP_ID` when direct
  `FEATURE_ID` overlap is absent, then maps returned VDYP outputs back to source IDs for cache
  compatibility.
- Added regression coverage for the map-join fallback:
  `tests/test_vdyp_stage.py::test_run_vdyp_for_stratum_maps_source_feature_ids_via_map_id`
  asserts that non-overlapping source IDs are bridged through `MAP_ID` and still return results
  keyed by original source `FEATURE_ID`.
- Re-ran full no-cache K3Z pipeline against 2024 VRI+VDYP inputs:
  `FEMIC_NO_CACHE=1 PYTHONPATH=src .venv/bin/python -u -m femic run --run-config config/run_profile.k3z.yaml -v --run-id k3z_vri2024_mapfix_20260307`.
  Run completed `status=ok` with non-empty outputs (`data/vdyp_curves_smooth-tsak3z.feather`
  rows `= 3588`, `data/02_input-tsak3z.dat` lines `= 13`) and VDYP report showing no empty-output
  failures (`status counts: dispatch=12, start=12, ok=12`).
- Consulted local VRI metadata PDFs in `docs/reference` while debugging
  (`vegcomp_poly_rank1_data_dictionaryv5_2019*.pdf`,
  `vegcomp_toc_data_dictionaryv5_2019.pdf`); practical takeaway for this run path remains:
  `MAP_ID` is the reliable bridge field across 2024 VRI rank1 samples and 2024 VDYP input layers
  when `FEATURE_ID` domains diverge.
- Added profile/env support for cumulative top-strata selection by area coverage:
  new config key `selection.stratification.top_area_coverage` (wired through CLI/profile/env as
  `FEMIC_STRAT_TOP_AREA_COVERAGE`) and 01a runtime (`target_area_coverage`) now drive
  `build_strata_summary(..., target_coverage=...)`.
- Updated K3Z profile to `top_area_coverage: 0.95` in
  `config/run_profile.k3z.yaml`.
- Re-ran K3Z no-cache with 95% top-area cutoff:
  `FEMIC_NO_CACHE=1 PYTHONPATH=src .venv/bin/python -u -m femic run --run-config config/run_profile.k3z.yaml -v --run-id k3z_cov95_20260307`.
  01a now selects `13` strata at cumulative coverage `0.95565930139286`.
- BEC hierarchy check for selected K3Z strata:
  all selected strata remain identical at zone+subzone (`CWHvm`), and also at
  zone+subzone+variant (`CWHvm1`) with phase null throughout; deeper BEC hierarchy
  does not add partition signal for this case.
- SI split diagnostics on the 95% run show frequent sparse SI bins in tail strata
  (many `L/M/H` bins with 0-2 stands), with corresponding VDYP `skipped`/`empty_output`
  events; this supports collapsing SI splits for sparse K3Z strata in the next tuning step.
- Implemented requested K3Z stratification reset: lowered `top_area_coverage` to `0.80`, removed adaptive SI-width split overrides, and restored fixed SI quantile bins (`L=5..35`, `M=35..65`, `H=65..95`).
- Added post-fit adjacent SI-curve merge behavior in TIPSY AU assembly (`src/femic/pipeline/tipsy.py`), including per-stratum merge diagnostics (`si-groups`) and shared-AU mapping for merged SI levels.
- Fixed merged-AU downstream bundle failure by making `assign_curve_ids_from_au_table(...)` robust to duplicate `au_id` rows (select first non-null managed/unmanaged curve IDs before managed/unmanaged assignment).
- Hardened stand export for merged AUs by resolving duplicate-`au_id` lookups in `prepare_stands_export_frame(...)` to a stable `canfi_species` scalar.
- Added regression tests:
  - `tests/test_bundle.py::test_assign_curve_ids_from_au_table_handles_duplicate_au_rows`
  - `tests/test_stands.py::test_prepare_stands_export_frame_handles_duplicate_au_rows`
- Re-ran K3Z end-to-end with no-cache and requested settings:
  `FEMIC_NO_CACHE=1 PYTHONPATH=src .venv/bin/python -u -m femic run --run-config config/run_profile.k3z.yaml -v --run-id k3z_cov80_fixedsi_merge_debug2_20260307`.
  Run completed successfully (`status=ok`, manifest: `vdyp_io/logs/run_manifest-k3z_cov80_fixedsi_merge_debug2_20260307.json`).
- Implemented pre-fit SI-bin stabilization in `src/femic/pipeline/vdyp_stage.py::fit_stratum_curves(...)`:
  added `min_stands_per_si_bin` (default `25`) and automatic adjacent-bin collapse before NLLS;
  collapse actions are logged per stratum.
- Updated SI-level AU merge behavior in `src/femic/pipeline/tipsy.py::build_tipsy_params_for_tsa(...)`:
  merges now require both bounded max-relative-gap and bounded age-window NRMSE
  (plus existing common-age checks), with per-pair `gap/rmse/nrmse` diagnostics.
- Added deterministic weak-species override hooks for config-driven TIPSY:
  `species_code_overrides` and `siteprod_si_fallback_by_species` are now supported in
  `src/femic/pipeline/tipsy_config.py` and used during candidate evaluation/assignment.
- Updated `config/tipsy/tsa29.yaml` and `config/tipsy/tsak3z.yaml` with explicit
  `species_code_overrides` (`SX->SW`, `DR->FD`) plus `siteprod_si_fallback_by_species`.
- Added requested L/M/H comparison diagnostics: `execute_curve_smoothing_runs(...)` now emits
  per-stratum overlays (`plots/vdyp_lmh_tsa*-*.png`) showing L/M/H best-fit VDYP curves on one plot.
- Wired site productivity source resolution to prefer the fresh dataset path
  `data/bc/siteprod/Site_Prod_BC.gdb` (with fallback), and surfaced the active siteprod path
  in startup logging.
- Re-ran full no-cache K3Z compile against 2024 VRI/VDYP + fresh siteprod source:
  `FEMIC_NO_CACHE=1 PYTHONPATH=src .venv/bin/python -u -m femic run --run-config config/run_profile.k3z.yaml -v --run-id k3z_siteprod_refresh_20260307`
  completed `status=ok` and regenerated current K3Z fitdiag/TIPSY comparison artifacts.
- Isolated the K3Z two-pass SI rebin failure to pipeline regressions (not a BC schema change):
  stale TSA-specific VDYP feathers were being reused under no-cache runs and output remap
  did not robustly handle table-number keyed VDYP outputs with extra tables.
- Fixed `load_vdyp_input_tables(...)` precedence to prefer explicit `source_feature_ids`
  when both feature IDs and map IDs are provided, with map-id fallback only if feature-id
  lookup returns empty.
- Updated 01a VDYP-table load behavior to force source reads whenever
  `runtime_config.force_run_vdyp` is true, preventing stale TSA-scoped VDYP caches from
  contaminating no-cache debug runs.
- Hardened `run_vdyp_for_stratum(...)` remap logic to use VDYP output table attrs
  (`vdyp_map_name` + `vdyp_polygon_id`) back to resolved feature IDs before key/order fallbacks.
- Updated `import_vdyp_tables(...)` to key outputs by `Table Number` (preserving map/polygon attrs)
  to avoid polygon-key collisions/overwrites in mixed-map batches.
- Added regression tests for:
  - feature-id loader precedence when both feature IDs and map IDs are supplied
  - table-number output remap via VDYP table attrs
  - map-id and map+polygon remap paths
- Revalidated no-cache K3Z two-pass run:
  `FEMIC_NO_CACHE=1 PYTHONPATH=src .venv/bin/python -u -m femic run --run-config config/run_profile.k3z.yaml -v --run-id k3z_twopass_fix5_20260307`
  now reports `two-pass SI rebin: mapped VDYP SI for 194/251 rows` and completes downstream
  TIPSY/bundle stages (previously `0/251` with empty downstream outputs).
- 2026-03-08: Added configurable SI-bin collapse threshold for 01a fitting (`modes.vdyp_min_stands_per_si_bin` -> `FEMIC_VDYP_MIN_STANDS_PER_SI_BIN` -> runtime `min_stands_per_si_bin`).
- 2026-03-08: Updated `config/run_profile.k3z.yaml` for requested test settings (`top_area_coverage: 0.90`, `vdyp_min_stands_per_si_bin: 10`).
- 2026-03-08: Re-ran no-cache K3Z with requested settings; 01a selected 9 strata at 90.655% coverage, AU bundle contains 27 AUs, and SS remains represented (`CWHvm_HW+SS`).
- 2026-03-08: Ran comparison compile with `species_combo_count: 3`; 01a selected 25 strata at 90.153% coverage and downstream AU bundle expanded to 66 AUs (22 strata x 3 SI levels), indicating substantially higher fragmentation than combo=2.
- 2026-03-08: Added run-profile docs for `vdyp_min_stands_per_si_bin` in `config/run_profile.example.yaml` and `docs/reference/run-config.rst`.
- 2026-03-08: Added species-proportion curve export to post-TIPSY bundle assembly. For each AU, bundle `curve_table.csv` and `curve_points_table.csv` now include `unmanaged_species_prop_<SPP>` and `managed_species_prop_<SPP>` curves (single-point `x=1`, `y=proportion`) when inventory species-universe scanning is available.
- 2026-03-08: Implemented TSA-scoped inventory pre-scan of top-6 VRI species from `data/ria_vri_vclr1p_checkpoint8.feather` (`SPECIES_CD_1..6` + positive `SPECIES_PCT_*`) so each AU receives a full, consistent species curve set (zero for absent species).
- 2026-03-08: Wired unmanaged species proportions from VDYP fit payload species shares and managed species proportions from `tipsy_sppcomp_tsa<tsa>.csv`.
- 2026-03-08: Added regression test `tests/test_bundle.py::test_build_bundle_tables_from_curves_adds_species_proportion_curves` and updated README notes for the new bundle behavior.
- 2026-03-08: Hardened TIPSY DAT export to a truly fixed schema in `src/femic/pipeline/tipsy.py`.
  - Switched DAT writing to explicit start-position rendering (header + row), instead of `pandas.to_string` heuristics.
  - Enforced full 32-column schema on every DAT row, including blank columns, so sparse K3Z rows do not collapse/shift downstream fields.
  - Kept line lengths fixed and removed variable trailing-trim behavior.
  - Updated/added tests in `tests/test_tipsy.py` for stable header-start expectations.
- 2026-03-08: Regenerated `data/02_input-tsak3z.dat` from `data/tipsy_params_tsak3z.xlsx` with the fixed writer. Verified row-field slices preserve intended values (for example `PCT_1=70`, `SI=23.9`, `SPP_2=CW`, `PCT_2=20`, `SPP_3=FD`, `PCT_3=10`) instead of prior concatenation.
- 2026-03-08: Rebased TIPSY DAT writer field ranges to the exact BatchTIPSY GUI indices from user screenshots (instead of inferred spacing), eliminating merged-token failures like `900P`/`0.95I`.
- 2026-03-08: Added anti-regression hardening for TIPSY DAT generation.
  - Canonicalized all DAT field positions as one 1-based BatchTIPSY schema constant copied from the GUI index spec.
  - Added strict row validation (`_validate_tipsy_dat_row`) to fail on width overflow or slice mismatch before file write.
  - Added regression test `test_write_tipsy_input_exports_fails_fast_on_width_overflow`.
  - Regenerated `data/02_input-tsak3z.dat` via the hardened writer.
- 2026-03-08: Cleared stale plot artifacts (`plots/*`) and executed a full fresh no-cache K3Z run from top of pipeline with current `config/run_profile.k3z.yaml` parameters (`run_id=k3z_fresh_20260308_032428`).
- 2026-03-08: Run completed successfully and regenerated 52 K3Z plot artifacts (strata, VDYP fitdiag, L/M/H overlays, and TIPSY-vs-VDYP AU plots), with manifest at `vdyp_io/logs/run_manifest-k3z_fresh_20260308_032428.json`.
- 2026-03-08: Implemented synthetic managed-yield fallback mode for unstable TIPSY cases.
  - New run-profile modes: `managed_curve_mode` (`tipsy|vdyp_transform`), `managed_curve_x_scale`, `managed_curve_y_scale`, `managed_curve_truncate_at_culm`, `managed_curve_max_age`.
  - New helper module `src/femic/pipeline/managed_curves.py` for AU-wise VDYP->managed curve synthesis.
  - Updated `01b_run-tsa.py` to apply `vdyp_transform` mode and overwrite managed yield outputs (`tipsy_curves_tsa*.csv`) with transformed curves.
  - Added regression coverage in `tests/test_managed_curves.py` and run-profile parsing/env propagation coverage in `tests/test_pipeline_helpers.py`.
  - Updated `config/run_profile.k3z.yaml` to use `vdyp_transform` with `x=0.8`, `y=1.2`, truncated post-culmination tail.
- 2026-03-08: Cleared old plot artifacts and ran a full no-cache K3Z compile with synthetic managed curves (`run_id=k3z_vdyp_managed_20260308_1`), regenerating fresh K3Z strata/fitdiag/LMH/TIPSY-vs-VDYP plots and model-input bundle tables.
- 2026-03-08: Extended `ROADMAP.md` with a new `Phase 4` for `femic.fmg` delivery, including tracked subtasks for proprietary Patchworks guide handling, Python 3 port of legacy fmg core, Patchworks ForestModel XML generation, fragments shapefile generation from BC VRI, Woodstock carry-over, and end-to-end validation.

## 2026-03-08 - Phase 4 kickoff: Patchworks export path
- Added new module `src/femic/fmg/patchworks.py` plus `src/femic/fmg/__init__.py` with:
  `build_forestmodel_xml_tree(...)`, `write_forestmodel_xml(...)`,
  `build_fragments_geodataframe(...)`, `write_fragments_shapefile(...)`, and
  `export_patchworks_package(...)`.
- Added `femic export patchworks` CLI in `src/femic/cli/main.py` for TSA-scoped export of
  `forestmodel.xml` and `fragments.shp` from existing FEMIC bundle/checkpoint outputs.
- Fixed checkpoint geometry handling for export: fragments builder now decodes WKB payloads
  (bytes/memoryview/hex string) before GeoDataFrame construction, resolving smoke-run
  failures against `data/ria_vri_vclr1p_checkpoint7.feather`.
- Added regression tests in `tests/test_fmg_patchworks.py` and `tests/test_cli_main.py` for:
  XML/treatment/curve references, fragments field content, CLI wiring, and WKB geometry decode.
- Updated docs for the new workflow:
  `README.md` (Patchworks export quickstart) and `docs/reference/cli.rst` (command reference).
- Verified with full quality gates:
  `ruff format src tests`, `ruff check src tests`, `mypy src`, `pytest`,
  `pre-commit run --all-files`, and `sphinx-build -b html docs _build/html -W` all passed.
- Verified runtime smoke export:
  `PYTHONPATH=src .venv/bin/python -m femic export patchworks --tsa k3z --output-dir output/patchworks_k3z_smoke`
  completed successfully (`au=14`, `fragments=218`, `curves=54`).

## 2026-03-08 - Patchworks export validation hardening (P4.4b, P4.6a)
- Added strict export validators in `src/femic/fmg/patchworks.py`:
  - `validate_forestmodel_xml_tree(...)` for required root attributes, `<input>/<output>`,
    required `<define field=...>` entries, curve/idref integrity, and CC treatment presence.
  - `validate_fragments_geodataframe(...)` for required columns, CRS presence, geometry sanity,
    numeric constraints, unique block IDs, positive area, and valid `IFM` values.
- Wired both validators into `export_patchworks_package(...)` so malformed exports fail before write.
- Expanded regression tests in `tests/test_fmg_patchworks.py` to cover:
  missing curve-idref detection and invalid `IFM` rejection.
- Added explicit export contract docs in `docs/reference/patchworks-export.rst`
  and linked it from `docs/index.rst` to record required XML/fragments fields.
- Re-validated direct K3Z export:
  `PYTHONPATH=src .venv/bin/python -m femic export patchworks --tsa k3z --output-dir output/patchworks_k3z_validated`
  succeeded (`au=14`, `fragments=218`, `curves=54`).
- Completed TSA29 export validation path from cached artifacts by reconstructing
  a TSA29 bundle/checkpoint under `output/patchworks_tsa29_validation/` and exporting with:
  `PYTHONPATH=src .venv/bin/python -m femic export patchworks --tsa 29 --bundle-dir output/patchworks_tsa29_validation/bundle --checkpoint output/patchworks_tsa29_validation/checkpoint7-tsa29.feather --output-dir output/patchworks_tsa29_validated`
  succeeded (`au=30`, `fragments=147959`, `curves=660`).

## 2026-03-08 - Woodstock compatibility export bootstrap (P4.2c)
- Added `src/femic/fmg/woodstock.py` with a Python 3 Woodstock compatibility export path:
  `export_woodstock_package(...)` now emits:
  - `woodstock_yields.csv` (long-form AU/IFM/age/volume curve rows)
  - `woodstock_areas.csv` (stand/AU/IFM/age/area table from checkpoint geometry/areas)
- Added CLI command `femic export woodstock` in `src/femic/cli/main.py`.
- Added regression tests:
  - `tests/test_fmg_woodstock.py`
  - new CLI wiring tests in `tests/test_cli_main.py`
- Updated docs:
  - `README.md` quickstart snippet for Woodstock compatibility export
  - `docs/reference/cli.rst` export command reference updates

## 2026-03-08 - Shared FMG core/adapters refactor (P4.2a foundation, P4.3 consolidation)
- Added shared core dataclasses in `src/femic/fmg/core.py`:
  `CurvePoint`, `CurveDefinition`, `AnalysisUnitDefinition`, `BundleModelContext`.
- Added shared bundle adapters in `src/femic/fmg/adapters.py`:
  - `normalize_tsa_code(...)`
  - `build_bundle_model_context_from_tables(...)`
  - `build_bundle_model_context(...)`
- Refactored Patchworks export (`src/femic/fmg/patchworks.py`) to consume
  shared `BundleModelContext` for AU/curve/species maps and retained prior
  user-facing counts (`curve_count` now sourced from original curve-table row count in context).
- Refactored Woodstock export (`src/femic/fmg/woodstock.py`) to consume
  shared `BundleModelContext` instead of local AU/curve parsing.
- Added adapter regression coverage in `tests/test_fmg_adapters.py`.
- Revalidated exporter flows after refactor:
  - Patchworks `k3z`: `au=14`, `fragments=218`, `curves=54`
  - Woodstock `k3z`: `yield_rows=16162`, `area_rows=218`
  - Woodstock `tsa29` (validation bundle/checkpoint): `yield_rows=10050`, `area_rows=147959`

## 2026-03-08 - Initial XML fixture parity coverage (P4.2b groundwork)
- Added deterministic Patchworks XML fixture:
  `tests/fixtures/fmg/forestmodel_minimal.xml`.
- Added parity test:
  `tests/test_fmg_patchworks.py::test_write_forestmodel_xml_matches_fixture`,
  which asserts serialized XML output is byte-identical to fixture content for
  a stable minimal AU/curve case.

## 2026-03-08 - Core ForestModel/Treatment class migration (P4.2a)
- Expanded `src/femic/fmg/core.py` with explicit ForestModel/Treatment classes:
  `ForestModelDefinition`, `SelectDefinition`, `TreatmentDefinition`,
  `AttributeBinding`, `DefineFieldDefinition`, `TreatmentAssignment`.
- Refactored `src/femic/fmg/patchworks.py` so XML generation now follows:
  shared bundle context -> `build_patchworks_forestmodel_definition(...)`
  -> `forestmodel_definition_to_xml_tree(...)` -> write/validate.
- Added regression test
  `tests/test_fmg_patchworks.py::test_build_patchworks_forestmodel_definition_contains_treatment`
  to assert treatment-bearing select blocks are present in the core definition.
- Revalidated patchworks export smoke:
  `PYTHONPATH=src .venv/bin/python -m femic export patchworks --tsa k3z --output-dir output/patchworks_k3z_modelclass_smoke`
  succeeded (`au=14`, `fragments=218`, `curves=54`).

## 2026-03-08 - Expanded deterministic XML fixture parity (P4.2b)
- Added richer multi-AU/species fixture parity coverage for Patchworks XML:
  - `tests/fixtures/fmg/forestmodel_multi_au.xml`
  - `tests/test_fmg_patchworks.py::test_write_forestmodel_xml_matches_multi_au_fixture`
- Marked `P4.2` and `P4.2b` complete in `ROADMAP.md` and updated the
  detailed next-step queue toward treatment transition/action parity and
  Woodstock ingest conventions.

## 2026-03-08 - Treatment transition + Woodstock ingest table extensions
- Extended Patchworks treatment serialization for transition semantics:
  - `TreatmentDefinition` now supports `transition_assignments`
  - serializer now emits `<transition><assign .../></transition>` blocks
  - default CC treatment includes transition assignment `IFM='managed'`
- Added new Patchworks CLI/export control:
  - `--cc-transition-ifm` (default `managed`)
- Extended Woodstock compatibility package outputs:
  - `woodstock_actions.csv` (baseline CC action rows by AU)
  - `woodstock_transitions.csv` (baseline managed transition rows by AU)
  - corresponding result metadata (`action_rows`, `transition_rows`)
  - CLI now accepts `--cc-min-age` / `--cc-max-age` for Woodstock export too
- Updated docs for new export behavior:
  - `README.md` (new Woodstock output files)
  - `docs/reference/cli.rst` (new options)
  - `docs/reference/woodstock-export.rst` (new reference page)
  - `docs/index.rst` and `docs/reference/patchworks-export.rst`
- Revalidated runtime smoke exports:
  - `femic export patchworks --tsa k3z` (`au=14`, `fragments=218`, `curves=54`)
  - `femic export woodstock --tsa k3z`
    (`yield_rows=16162`, `area_rows=218`, `action_rows=14`,
    `transition_rows=14`)

## 2026-03-08 - Patchworks species-wise yield curve derivation
- Extended `src/femic/fmg/patchworks.py` to derive species-wise yield curves from
  total-volume and species-proportion curves:
  - unmanaged: `feature.Yield.unmanaged.<SPP>`
  - managed: `feature.Yield.managed.<SPP>` and `product.Yield.managed.<SPP>`
- Derivation logic now evaluates species proportions at total-curve ages using
  constant or piecewise-linear interpolation, then multiplies by total volume.
- Added regression coverage:
  `tests/test_fmg_patchworks.py::test_build_forestmodel_xml_tree_adds_species_yield_curves`.
- Regenerated deterministic XML fixture baselines to include derived species
  yield attributes/curves:
  - `tests/fixtures/fmg/forestmodel_minimal.xml`
  - `tests/fixtures/fmg/forestmodel_multi_au.xml`
- Updated docs:
  - `docs/reference/patchworks-export.rst`
  - `README.md`

## 2026-03-08 - Patchworks XML flat-tail deduplication
- Updated Patchworks XML serialization to remove redundant repeated far-left
  and far-right y-values for non-`unity` curves while preserving the inner edge
  points of terminal plateaus.
- Added regression coverage:
  `tests/test_fmg_patchworks.py::test_forestmodel_xml_trims_repeated_curve_values_on_both_tails`.
- Documented behavior in `docs/reference/patchworks-export.rst`.

## 2026-03-08 - Patchworks XML non-finite value and all-flat curve hardening
- Hardened curve-point serialization in `src/femic/fmg/patchworks.py`:
  - non-finite `y` values are coerced to `0.0`
  - non-finite `x` values are dropped
  - points are sorted/normalized to monotonic `x` with duplicate-`x` collapse
- Fixed all-flat curve trimming edge case so single-point flat curves retain
  the earliest age point instead of collapsing to max-age `(299,0)` points.
- Added regression tests:
  - `test_forestmodel_xml_all_flat_curve_keeps_earliest_point`
  - `test_forestmodel_xml_sanitizes_nan_point_values`

## 2026-03-08 - Readable Patchworks curve IDs
- Replaced opaque numeric XML curve IDs (`C<id>`) with readable deterministic
  ids while preserving uniqueness and stable idref linkage:
  - `managed_total_<id>`, `unmanaged_total_<id>`
  - `managed_prop_<SPP>_<id>`, `unmanaged_prop_<SPP>_<id>`
  - `au_<au_id>_<managed|unmanaged>_yield_<SPP>` for derived species-yield curves
- Updated serializer curve ordering to deterministic lexical ordering
  (`unity` first, then sorted readable ids).

## 2026-03-08 - Integer age formatting for Patchworks curve x-values
- Updated Patchworks XML point serialization to format integral age `x` values
  as integers (for example `x="10"` instead of `x="10.000000"`).
- Kept fallback float formatting for non-integral `x` values to preserve
  compatibility with transformed or custom curves.
- Updated fixture baselines and regression expectations accordingly.

## 2026-03-08 - Patchworks y-value precision policy by curve family
- Updated Patchworks XML `y` formatting to reduce precision noise:
  - volume-yield curves (`managed_total_*`, `unmanaged_total_*`,
    `au_*_..._yield_*`) are now rounded to 1 decimal place
  - normalized/proportion curves are now rounded to at most 5 decimals
- Updated fixture baselines and tests accordingly.
- Updated fixture baselines and tests to assert new id conventions.

## 2026-03-08 - CC harvested-volume product consequences (species-wise)
- Added Patchworks product consequence attributes for CC harvested volume in
  `src/femic/fmg/patchworks.py`:
  - `product.HarvestedVolume.managed.Total.CC`
  - `product.HarvestedVolume.managed.<SPP>.CC`
- Bound harvested-volume attributes to managed total/species yield curves so
  per-species harvested volume tracks managed species-yield definitions.
- Extended regression checks in `tests/test_fmg_patchworks.py` and regenerated
  deterministic XML fixtures:
  - `tests/fixtures/fmg/forestmodel_minimal.xml`
  - `tests/fixtures/fmg/forestmodel_multi_au.xml`
- Regenerated validated K3Z Patchworks export:
  `output/patchworks_k3z_validated/forestmodel.xml`.

## 2026-03-08 - Patchworks managed/unmanaged semantics audit and fragment fix
- Reviewed `reference/UserGuide.pdf` semantics for block-vs-fragment,
  managed/unmanaged components, and treatment eligibility.
- Simplified fragments export logic in `src/femic/fmg/patchworks.py` for the
  K3Z teaching model:
  - exactly one output row per stand fragment (`1 fragment = 1 block`);
  - each row is assigned a single IFM state (`managed` or `unmanaged`);
  - `BLOCK` values are unique per row (no multi-row block components);
  - IFM assignment uses THLB signal precedence:
    `thlb` > `thlb_fact` > `thlb_area` > `thlb_raw` (positive => managed).
- Tightened IFM transition semantics by validating `cc_transition_ifm` to
  accepted IFM values (`managed` or `unmanaged`).
- Added/updated regression coverage in `tests/test_fmg_patchworks.py`:
  - one-row-per-fragment behavior
  - binary IFM assignment from THLB signals
  - invalid `cc_transition_ifm` rejection.
- Updated user-facing docs:
  - `docs/reference/patchworks-export.rst`
  - `README.md`

## 2026-03-08 - Remove redundant IFM=managed transition assignment
- Updated Patchworks treatment export to avoid redundant transition logic:
  CC tracks no longer emit `assign field="IFM" value="'managed'"` inside managed-only
  select statements.
- Changed default `cc_transition_ifm` to unset (`None`), making transition IFM assignment
  optional.
- Kept explicit non-redundant transitions supported (for example
  `--cc-transition-ifm unmanaged`).
- Updated CLI/docs:
  - `src/femic/cli/main.py`
  - `docs/reference/cli.rst`
  - `docs/reference/patchworks-export.rst`
- Updated regression coverage in `tests/test_fmg_patchworks.py` and refreshed
  XML fixture baselines.

## 2026-03-08 - Upstream yield terminology rename to natural/planted
- Updated upstream bundle table assembly (`src/femic/pipeline/bundle.py`) to use
  canonical curve terminology:
  - `curve_type`: `natural` and `planted`
  - species proportions: `natural_species_prop_<SPP>` and
    `planted_species_prop_<SPP>`
- Added canonical AU columns:
  - `natural_curve_id`
  - `planted_curve_id`
- Preserved backward compatibility by still emitting legacy alias columns:
  - `unmanaged_curve_id`
  - `managed_curve_id`
- Updated AU curve assignment defaults to canonical columns with fallback to
  legacy names when loading older tables.
- Updated FMG adapter compatibility (`src/femic/fmg/adapters.py`) so it accepts
  either canonical (`natural/planted`) or legacy (`unmanaged/managed`) curve
  names and column names.
- Updated Patchworks curve-id normalization (`src/femic/fmg/patchworks.py`) so
  canonical upstream curve types map correctly to Patchworks IFM semantics.
- Updated docs/tests:
  - `README.md`
  - `tests/test_bundle.py`
  - `tests/test_fmg_adapters.py`

## 2026-03-08 - Docs tree cleanup (Sphinx source vs reference assets)
- Moved non-Sphinx reference assets out of `docs/reference/` into top-level
  `reference/` (including `reference/vdyp/`) so `docs/` remains documentation
  source only.
- Added `reference/README.md` to document purpose and boundaries of the new
  reference-asset directory.
- Updated path references that pointed to moved PDFs:
  - `config/tipsy/tsa29.yaml`
  - `ROADMAP.md`
  - `CHANGE_LOG.md`

## 2026-03-08 - Phase 5 docs recovery and guides expansion
- Added a new Sphinx `Guides` information architecture and wired it into
  `docs/index.rst` so pipeline walkthrough content is first-class and separate
  from API/contract reference pages.
- Added curated workflow guides under `docs/guides/` covering:
  - end-to-end pipeline walkthrough,
  - Stage 00 data prep assumptions/checkpoints,
  - Stage 01a strata/VDYP/TIPSY-input workflow,
  - Stage 01b post-TIPSY integration,
  - bundle/export workflow,
  - diagnostics interpretation,
  - troubleshooting/recovery,
  - known limitations and human-in-the-loop boundaries.
- Added notebook provenance artifacts:
  - `docs/guides/legacy-traceability.rst`
  - `docs/guides/legacy_notebook_coverage.csv`
  preserving markdown-cell-level mapping from legacy notebooks into current docs,
  including explicit `mapped` vs `retired` status.
- Added docs contract tests in `tests/test_docs_contract.py` for:
  - required guides/toctree presence,
  - completeness of notebook markdown coverage mapping,
  - high-value CLI option drift checks between Typer help output and
    `docs/reference/cli.rst`.
- Added a README documentation section linking the published site and clarifying
  Guides vs Reference scope.
- Updated `ROADMAP.md` with a new `Phase 5: Documentation Recovery + Expansion`
  checklist and detailed next-step notes; remaining work in this phase is
  deployment validation (`P5.7`) after push/publish.

## 2026-03-08 - Phase 5 publish validation and docs workflow deploy guard
- Verified GitHub Pages deployment for Phase 5 guide expansion on `main`:
  - live landing page now shows both `Guides` and `Reference` navigation blocks;
  - direct guide URLs under `/guides/*.html` return HTTP 200.
- Completed roadmap `P5.7` deployment-validation tasks and recorded direct URL
  checks for all new guide pages.
- Updated docs workflow deploy condition in `.github/workflows/docs-pages.yml`
  so deploy runs for both `push` and manual `workflow_dispatch` on `main`
  (while still excluding pull-request events).

## 2026-03-08 - Phase 6 kickoff: case onboarding templates and guide
- Started `Phase 6: Deployment Readiness and Case Onboarding` in `ROADMAP.md`
  and marked `P6.1` complete.
- Added reusable case onboarding templates:
  - `config/run_profile.case_template.yaml` (TSA + custom-boundary profile scaffold)
  - `config/tipsy/template.case.yaml` (new-case TIPSY config starter)
- Added onboarding guide page:
  - `docs/guides/case-onboarding.rst`
  including required-input and acceptance checklists.
- Wired onboarding page into guides navigation (`docs/guides/index.rst`) and
  linked onboarding assets from `README.md`.
- Extended docs contract checks in `tests/test_docs_contract.py` to assert
  onboarding templates exist and remain part of maintained docs structure.

## 2026-03-08 - Phase 6 P6.2: one-command case preflight validation
- Added a new CLI command: `femic prep validate-case`.
- `prep validate-case` now validates case prerequisites from a run profile before
  long compile runs, including:
  - run-profile parsing/structure validity,
  - boundary-mode integrity (`selection.boundary_path` / `selection.boundary_code`),
  - required case TIPSY config presence/validation,
  - required external source datasets (VRI, VDYP input, TSA boundaries, siteprod),
  - log directory readiness warnings.
- Added explicit remediation-oriented error messages for missing prerequisites.
- Added `--strict-warnings` mode to fail preflight when warnings are present.
- Updated CLI reference docs with `prep validate-case` options:
  - `--run-config`, `--tipsy-config-dir`, `--strict-warnings`.
- Updated onboarding guide to include the new single-command preflight step.
- Added regression tests in `tests/test_case_preflight_cli.py` covering:
  - successful validation,
  - missing TIPSY config failure,
  - boundary-code required failure,
  - strict-warning failure behavior.
- Extended docs contract checks to include `prep validate-case` option drift.

## 2026-03-08
- Added Phase 7 roadmap section for Patchworks runtime integration, Wine execution, and UBC VPN-linked licensing checks.
- Added `reference/Patchworks/` to `.gitignore` so proprietary Patchworks binaries/docs are not published from this repo.
- Added `src/femic/patchworks_runtime.py` with config loading, Wine path translation, license parsing, preflight checks, deterministic Matrix Builder command assembly, and log/manifest capture.
- Added new CLI group `femic patchworks` with:
  - `patchworks preflight` (Wine/Java/jar/input/license checks, optional reachability skip)
  - `patchworks matrix-build` (direct Matrix Builder or interactive AppChooser mode under Wine)
- Added baseline runtime config file `config/patchworks.runtime.yaml` for local execution wiring.
- Added new operator guides:
  - `docs/guides/patchworks-wine-runtime.rst`
  - `docs/guides/ubc-vpn-license-connectivity.rst`
- Updated docs navigation and CLI reference to include Patchworks runtime commands/options.
- Added tests for Patchworks runtime helpers and CLI wiring:
  - `tests/test_patchworks_runtime.py`
  - extended `tests/test_cli_main.py` and `tests/test_docs_contract.py`.
- Updated README with Patchworks runtime command examples and proprietary-runtime boundary note.
- Closed Phase 7 git-protection follow-up by verifying `reference/Patchworks/` is ignored and no proprietary Patchworks bundle files are tracked in the repository index.
- Updated roadmap status so P7.1 is complete; next practical Phase 7 task is live UBC VPN + Wine license-server validation.
- Fixed Patchworks runtime config relative-path resolution so sample config paths work from repo root when config lives under `config/`.
- Added `femic export release` student-facing packaging command, including strict required-artifact validation and versioned release directory output.
- Added release package outputs: `release_manifest.json` (SHA256 file inventory) and `HANDOFF.md` (operator checklist/commands).
- Added tests for release packaging and CLI wiring (`tests/test_release_packaging.py`, `tests/test_cli_main.py`) and expanded docs CLI contract coverage.
- Updated export workflow docs to include release package generation step.
