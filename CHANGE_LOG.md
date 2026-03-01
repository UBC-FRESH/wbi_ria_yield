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
