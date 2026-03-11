# FEMIC Public Data Mirror Bootstrap (P10.6b)

This note is maintainer-focused and captures the first publish flow for a
dedicated DataLad dataset repository (target: `UBC-FRESH/femic-public-data`).

Current local bootstrap state (2026-03-11):

- Local dataset repo exists at `/home/gep/projects/femic-public-data`.
- FEMIC links it as submodule at `external/femic-public-data`.
- Published dataset repo: `https://github.com/UBC-FRESH/femic-public-data`.
- Arbutus special-remote upload verified for mirrored seed artifacts (including `misc.thlb.tif` and `VEG_COMP_LYR_R1_POLY.gdb/a00000009.gdbtable`).

Known-good command sequence source:

- `tmp/datalad-kb-page.md` (FRESH lab DataLad KB copy).
- `tmp/lab-data-workflow-workshop` symlink target:
  `/home/gep/projects/lab-data-workflow-workshop`.
- Most relevant workshop references:
  - `arbutus_s3/datalad_s3_setup.md`
  - `scripts/create_github_sibling.sh`
  - `workflows/common_errors.md`

## Inputs

- `metadata/required_datasets.yaml` (authoritative source inventory)
- `metadata/datalad_mirror_seed.csv` (current include=true dataset list)
- Arbutus S3 credentials for special remote setup
- Local credential template:
  `config/credentials/arbutus_env.template.sh`

## Bootstrap Steps

1. Create the GitHub repository (`femic-public-data`) under `UBC-FRESH`.
2. Initialize local DataLad dataset:
   ```bash
   datalad create -c text2git femic-public-data
   cd femic-public-data
   ```
3. Create destination paths matching `canonical_instance_path`.
4. Place mirrored artifacts at those paths and run:
   ```bash
   datalad save -m "Add initial FEMIC mirrored public datasets"
   ```
5. Configure and test remotes:
   - Arbutus S3 special remote via `git annex initremote`
   - GitHub sibling with `--publish-depends arbutus-s3`
6. Push dataset metadata and annexed content to both remotes.
7. Validate cold-clone retrieval:
   ```bash
   datalad clone git@github.com:UBC-FRESH/femic-public-data.git smoke
   cd smoke
   datalad get data/misc.thlb.tif
   ```

## Required Completion Artifacts

- Published dataset repo URL.
- Arbutus S3 special remote config recorded in repo docs.
- Checksum values backfilled in `metadata/required_datasets.yaml`.
- Follow-on FEMIC task: add repo as submodule (`P10.6c`).
