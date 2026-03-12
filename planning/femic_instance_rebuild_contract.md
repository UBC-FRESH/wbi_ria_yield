# FEMIC Instance Rebuild Contract (v1)

## Purpose

Define the minimum reproducibility contract for all FEMIC deployment instances.
This contract is the authority for:

- required inputs/config/runtime prerequisites,
- authoritative rebuild sequence,
- post-rebuild invariants,
- failure classes and remediation messaging.

Machine-readable source of truth:
`planning/femic_instance_rebuild_contract.v1.yaml`.

## 1. Required Inputs and Prerequisites (`P13.1a`)

### Required input artifact families

- boundary geometry / TSA selection inputs used by run profile,
- inventory checkpoints and bundle inputs required by the selected workflow,
- Patchworks runtime config and model-side inputs for matrix builds.

### Required config files

- run profile (`config/run_profile.<case>.yaml`),
- TIPSY config set (`config/tipsy/tsa<code>.yaml`),
- Patchworks runtime config (`config/patchworks.runtime*.yaml`) when applicable.

### Required runtime prerequisites

- Python environment with FEMIC installed and CLI available,
- geospatial runtime readiness (`fiona` import, GDAL visibility, shapefile I/O),
- Patchworks runtime prerequisites when using Patchworks steps
  (SPSHOME registration signal, Java launcher/runtime path, license env wiring).

## 2. Authoritative Rebuild Sequence (`P13.1b`)

Execution order (authoritative baseline):

1. validate instance case config (`femic prep validate-case`)
2. validate geospatial runtime (`femic prep geospatial-preflight`)
3. run upstream FEMIC compile (`femic run --run-config ...`)
4. complete manual TIPSY boundary step (if required by case)
5. run post-TIPSY bundle (`femic tsa post-tipsy --run-config ... --tsa ...`)
6. run Patchworks preflight/build commands as needed:
   - `femic patchworks preflight ...`
   - `femic patchworks build-blocks ...`
   - `femic patchworks matrix-build ...`
7. capture manifests/logs/reports as rebuild evidence.

Each step must declare:

- mutable artifacts,
- expected outputs,
- expected run/report IDs.

## 3. Required Post-Rebuild Invariants (`P13.1c`)

Minimum invariant classes:

- accounts/targets sanity (non-empty required families),
- managed-area sanity (case-defined expected bounds),
- block join/topology consistency checks,
- seral-stage account presence and non-regression checks,
- baseline structural diff checks for known-critical track artifacts.

Invariant results must be recorded as:

- pass/warn/fail status,
- measured value(s),
- threshold/baseline used for comparison,
- remediation hint.

## 4. Failure Classes and Remediation Messaging (`P13.1d`)

### Hard failure (`fatal`)

Condition:

- missing required inputs/config/runtime prerequisites,
- command execution non-zero for mandatory rebuild steps,
- invariant regression marked `fatal`.

Required message fields:

- failure class (`fatal`),
- failing step ID,
- concise cause,
- explicit remediation action,
- rerun command hint.

### Warning (`warn`)

Condition:

- optional artifact missing,
- non-fatal drift from expected metrics,
- informational preflight concern with safe fallback.

Required message fields:

- failure class (`warn`),
- affected scope/artifact,
- impact statement,
- recommended follow-up action.

## 5. Versioning and Governance

- Contract version is semver-like (`v1` currently).
- Any schema/semantic change to this contract requires:
  - roadmap entry update,
  - changelog update,
  - contract test updates in `tests/test_docs_contract.py`.

