# TSA29 Instance Contract (Phase 19)

## Purpose

Define the minimum contract for `UBC-FRESH/femic-tsa29-instance` so the
repository is immediately usable for graduate-student work and also serves as a
rebuild-reproducibility test target.

## Repository Layout Contract

Required directories/files:

- `config/`
- `data/`
- `plots/`
- `models/`
- `output/`
- `docs/`
- `vdyp_io/logs/`
- `evidence/`
- `README.md`
- `.gitignore`

Required config files:

- `config/run_profile.tsa29.yaml`
- `config/tipsy/tsa29.yaml`
- `config/rebuild.spec.yaml`
- `config/rebuild.allowlist.yaml`
- `config/patchworks.runtime.windows.yaml`

## Snapshot Payload Contract (ASAP Usable)

Required in-repo baseline artifacts:

- Model input bundle tables:
  - `data/model_input_bundle/au_table.csv`
  - `data/model_input_bundle/curve_table.csv`
  - `data/model_input_bundle/curve_points_table.csv`
- Core model output:
  - `output/patchworks_tsa29_validated/forestmodel.xml`
- Validation bundle tables:
  - `output/patchworks_tsa29_validation/bundle/*.csv`
- Diagnostics/provenance:
  - `vdyp_io/logs/run_manifest-tsa29_*.json`
  - `metadata/lineage_registry.yaml`
  - `metadata/artifact_checksums.sha256`

Thin-instance policy:

- Very large artifacts are externalized and must be documented with expected
  hash references (for example in `metadata/large_artifacts.sha256`).
- Externalized artifacts must include deterministic retrieval instructions in
  the instance docs/runbook.

## Explicit Excludes

- Secrets and credentials.
- Local-only env helper scripts.
- VPN credentials.
- Non-TSA29 bulky assets that are not required for baseline interpretation.

## Rebuild + Evidence Contract

Required:

- A valid rebuild spec (`config/rebuild.spec.yaml`) that can be validated with
  `femic instance validate-spec`.
- A promoted evidence artifact:
  `evidence/reference_rebuild_report.latest.json`.
- Runbook instructions for:
  - `femic instance rebuild ...`
  - `femic instance promote-evidence ...`

## Acceptance Gates

Minimum "no really bad bits" definition:

- Required snapshot artifacts exist at expected paths.
- No missing critical configs or runbook guidance.
- Docs provide setup, expected outputs, troubleshooting, and figure appendix.
- Case preflight contract command is documented and runnable:
  `femic prep validate-case --run-config config/run_profile.tsa29.yaml --tipsy-config-dir config/tipsy`

For full Phase 19 closure:

- Snapshot usability smoke passes.
- Full Patchworks-enabled rebuild evidence is green and recorded.
