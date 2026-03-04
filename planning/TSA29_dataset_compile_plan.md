# TSA 29 Dataset Compile Plan

## Objective

Compile a fresh model-input dataset for TSA `29` using the FEMIC CLI, with
auditable manifests/logs and deterministic sampling controls.

## Current Readiness

- Core pipeline roadmap phases are closed (Phase 1/2/3 in `ROADMAP.md` are checked).
- CLI/run-profile/manifest/reproducibility features are in place.
- Critical TSA-29 gate remains:
  `config/tipsy/tsa29.yaml` does not exist yet and must be created before a
  production run.

## Preconditions

1. Runtime/tooling
- Activated project venv.
- `PYTHONPATH=src python -m femic --help` succeeds.
- `wine` available on `PATH` (or run with cache-only expectations plus `--resume`).

2. Data/layout
- Required data files exist under repo `data/` (or configured external root).
- `vdyp_io/VDYP_CFG` and `VDYP7/VDYP7/VDYP7Console.exe` exist.

3. TIPSY config handoff
- Add `config/tipsy/tsa29.yaml` using existing TSA configs as template.
- Validate before run:
  `PYTHONPATH=src python -m femic tipsy validate --config-dir config/tipsy --tsa 29`

## Step-by-Step Execution

1. Create TSA 29 run profile (recommended)
- Copy `config/run_profile.example.yaml` to `config/run_profile.tsa29.yaml`.
- Set:
  - `selection.tsa: ["29"]`
  - desired `modes` values (`resume`, `verbose`, `skip_checks`, `debug_rows`)
  - `run.run_id` (for traceability), `run.log_dir` if non-default.

2. Optional deterministic seed
- Export a fixed seed for reproducible bootstrap sampling:
  `export FEMIC_SAMPLING_SEED=42`

3. Dry-run sanity check
- `PYTHONPATH=src python -m femic run --run-config config/run_profile.tsa29.yaml --dry-run`

4. Execute compile
- `PYTHONPATH=src python -m femic run --run-config config/run_profile.tsa29.yaml`

5. Post-run diagnostics
- `PYTHONPATH=src python -m femic vdyp report`
- Optional thresholded gate:
  `PYTHONPATH=src python -m femic vdyp report --max-curve-warnings 5 --max-first-point-mismatches 0`

## Outputs To Verify

1. Run manifest
- `vdyp_io/logs/run_manifest-<run_id>.json`
- Confirm:
  - `status: "ok"`
  - `config_provenance.run_config_path` / `run_config_sha256`
  - `runtime_parameters` populated
  - `outputs.version_tag` and `outputs.versioned_output_dir`

2. Run-scoped logs
- `vdyp_io/logs/vdyp_runs-tsa29-<run_id>.jsonl`
- `vdyp_io/logs/vdyp_curve_events-tsa29-<run_id>.jsonl`
- `vdyp_io/logs/vdyp_stdout-tsa29-<run_id>.log`
- `vdyp_io/logs/vdyp_stderr-tsa29-<run_id>.log`

3. Model input bundle artifacts
- Under `data/model_input_bundle/`:
  - `au_table.feather`
  - `curve_table.feather`
  - `curve_points_table.feather`

## Risk/Failure Checklist

1. Missing TSA29 TIPSY config
- Symptom: fail-fast around TIPSY config discovery/validation.
- Action: create/fix `config/tipsy/tsa29.yaml`, rerun `tipsy validate`.

2. External data root mismatch
- Symptom: missing source data warnings/errors.
- Action: set `FEMIC_EXTERNAL_DATA_ROOT` to the correct base path.

3. VDYP tool availability
- Symptom: preflight errors for `wine`/VDYP executable/config.
- Action: fix environment, then rerun.

## Suggested Run Modes

1. First-pass debug
- Use `debug_rows` in profile (e.g., 500-2000) to validate end-to-end wiring.

2. Full production compile
- Remove `debug_rows`, keep `resume: true`, keep fixed `run_id` naming convention
  (for example `tsa29_YYYYMMDD`).

## Completion Criteria

- TSA29 run completes with exit code 0.
- Manifest status is `ok` and provenance/runtime fields are populated.
- VDYP report succeeds without unexpected parse-error spikes.
- Bundle outputs and run-scoped logs for TSA29 are present.
