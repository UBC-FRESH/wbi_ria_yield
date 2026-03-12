# Rebuild Runbook (Instance Placeholder)

Use this file as the operator-facing rebuild procedure for this instance.

## Required Inputs
- `config/run_profile.<case>.yaml`
- `config/rebuild.spec.yaml`
- `config/rebuild.allowlist.yaml`
- Any case-specific runtime prerequisites (for example Patchworks licensing/runtime).

## Standard Rebuild Commands
```bash
femic instance validate-spec --spec config/rebuild.spec.yaml
femic instance rebuild \
  --spec config/rebuild.spec.yaml \
  --baseline config/rebuild.baseline.json \
  --allowlist config/rebuild.allowlist.yaml
```

## Evidence to Archive
- `vdyp_io/logs/instance_rebuild_report-<run_id>.json`
- Referenced manifests/logs listed under `artifact_references`.

## Evidence Refresh Step (Release Prep)
```bash
femic instance refresh-reference-evidence --reference-root .
```
After refresh, verify:
- `evidence/reference_rebuild_report.latest.json` exists,
- `status` is `ok`,
- `regression_gate` booleans are all false.

## Local Notes
- Document case-specific overrides, expected warnings, and accepted deltas here.
