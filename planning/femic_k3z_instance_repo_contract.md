# FEMIC K3Z Example Instance Repository Contract

## Scope

- Repository: `https://github.com/UBC-FRESH/femic-k3z-instance`
- Visibility: public
- Purpose: standalone, snapshot-style K3Z example instance for onboarding and teaching.
- Linkback into FEMIC: git submodule at `external/femic-k3z-instance`.

## Include Rules

The repository mirrors a runnable instance root with these tracked families:

- `config/`
  - `run_profile.k3z.yaml`
  - `seral.k3z.yaml`
  - `tipsy/tsak3z.yaml`
- `data/bc/cfa/k3z/*` (including K3Z source PDFs)
- `data/model_input_bundle/*`
- `data/02_input-tsak3z.dat`
- `data/04_output-tsak3z.out`
- `data/tipsy_*tsak3z*`
- `data/vdyp_*tsak3z*`
- `plots/*tsak3z*` plus `plots/strata-tsak3z.*`
- `models/k3z_patchworks_model/*`
- `output/patchworks_k3z_validated/*`
- root docs/control files: `README.md`, `.gitignore`

## Exclude Rules

- Non-K3Z provincial base datasets.
- Secrets/credentials/local env files.
- Machine-local transient artifacts.

## Provenance Fields

Every snapshot release must record:

- FEMIC source repository URL.
- FEMIC source commit hash used to assemble snapshot.
- Snapshot release tag in K3Z repo (for example `v0.1.0`).
- Brief note of regeneration/validation context (run IDs or manifest references).

## Update Cadence

- Publish snapshot-style updates tied to FEMIC run/release milestones.
- Prefer immutable tags for teaching baselines.

## Storage Policy

- Current payload is plain git.
- If payload growth becomes problematic, migrate large binary families to Git LFS or DataLad annexing.

## Operator Workflow

- Initialize submodules from FEMIC root:
  - `git submodule update --init --recursive`
- Update K3Z submodule to latest remote commit:
  - `git submodule update --remote external/femic-k3z-instance`

## Acceptance Baseline (v0.1.0)

- Initial public baseline tag: `v0.1.0`
- Branch `main` head commit:
  - `e3285ad6462ea8996c86e14312e6fae89949111e`
