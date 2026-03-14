# TSA29 Dataset Compile Plan (Dual Fork: Patchworks + Woodstock/ws3)

## Objective

Compile and validate a TSA29 instance that serves two downstream targets from a
single FEMIC pipeline run:

1. Patchworks-formatted outputs (teaching/training support).
2. Woodstock-formatted outputs for ws3 model ingestion and simulation smoke
   testing (research-critical path).

## Scope Lock

- Primary success path: Woodstock/ws3 branch must run to a smoke-tested ws3
  simulation without errors and with sane outputs.
- Patchworks branch remains required, but secondary.
- Validation does not stop at "Woodstock files emitted"; it extends to "ws3
  model instance runs".

## Current State

- Standalone instance repo exists: `https://github.com/UBC-FRESH/femic-tsa29-instance`.
- FEMIC parent repo links it as submodule:
  `external/femic-tsa29-instance`.
- Snapshot baseline is published (`v0.1.0`) for immediate student use.
- Full rebuild remains open due to known Linux-side TSA index mismatch in 01a;
  Patchworks-enabled host validation remains required.

## End-to-End Pipeline Contract

### Stage A: Upstream FEMIC compile

Required:

- `femic prep validate-case --run-config config/run_profile.tsa29.yaml --tipsy-config-dir config/tipsy`
- `femic run --run-config config/run_profile.tsa29.yaml`
- `femic tsa post-tipsy --run-config config/run_profile.tsa29.yaml --tsa 29`

Expected core artifacts:

- `data/model_input_bundle/{au_table,curve_table,curve_points_table}.csv`
- run manifests in `vdyp_io/logs/`

### Stage B: Pipeline fork outputs

#### Branch B1 (Patchworks)

Required:

- `femic patchworks preflight --config config/patchworks.runtime.windows.yaml`
- `femic patchworks build-blocks --config config/patchworks.runtime.windows.yaml --with-topology`
- `femic patchworks matrix-build --config config/patchworks.runtime.windows.yaml`

Expected artifacts:

- `output/patchworks_tsa29_validated/forestmodel.xml`
- fragment bundle (`fragments.*`, or externalized thin-instance equivalent +
  checksums)
- matrix builder manifest in `vdyp_io/logs/`

#### Branch B2 (Woodstock -> ws3)

Required:

- `femic export woodstock --bundle-dir data/model_input_bundle --output-dir output/woodstock_tsa29`

Expected artifacts:

- complete Woodstock-formatted dataset under `output/woodstock_tsa29/`
- export manifest and checksums

## ws3 Integration and Smoke-Test Contract

### ws3 target repository

- `https://github.com/UBC-FRESH/ws3`

### Required smoke-test path

1. Create or reuse a TSA29 ws3 model instance scaffold.
2. Link FEMIC Woodstock outputs into ws3 input ports.
3. Run a minimal ws3 simulation.
4. Capture run log and summary outputs.

### Smoke-test acceptance criteria

- ws3 run exits successfully (no parser/runtime errors).
- input mappings resolve (no missing Woodstock tables/keys).
- at least one planning result table/report is emitted.
- sanity checks pass (non-empty schedules/volumes/areas; no all-zero collapse
  unless explicitly expected and documented).

### Evidence artifacts

- `evidence/ws3_smoke_report.latest.json`
- `evidence/ws3_smoke_logs/` (or referenced external log path with checksums)
- mapping manifest documenting FEMIC Woodstock outputs -> ws3 inputs.

## Risks and controls

1. FEMIC upstream compile regression (current 01a TSA index issue):
- Control: preserve snapshot baseline for immediate use; track full rebuild
  blocker and fix before phase closure.

2. Woodstock export appears valid but ws3 fails:
- Control: ws3 smoke test is mandatory gate, not optional.

3. Drift between Patchworks and Woodstock branches:
- Control: add shared invariant checks at fork point and branch-specific
  contract checks.

## Completion criteria

Phase closes only when all are true:

- Snapshot baseline remains student-usable.
- Full compile + Patchworks branch validation is green in supported runtime.
- Woodstock export is generated from same compile and validated.
- ws3 smoke-test run is green with recorded evidence and sane output summary.
