# FEMIC Public Data Mirror Bootstrap (P10.6b)

This note is maintainer-focused and captures the first publish flow for a
dedicated DataLad dataset repository (target: `UBC-FRESH/femic-public-data`).

## Inputs

- `metadata/required_datasets.yaml` (authoritative source inventory)
- `metadata/datalad_mirror_seed.csv` (current include=true dataset list)
- Arbutus S3 credentials for special remote setup

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
   - GitHub sibling (`datalad create-sibling-github ...`)
   - Arbutus special remote (`datalad create-sibling-ria ...`)
6. Push dataset metadata and annexed content to both remotes.
7. Validate cold-clone retrieval:
   ```bash
   datalad clone git@github.com:UBC-FRESH/femic-public-data.git smoke
   cd smoke
   datalad get data/misc.thlb.tif
   ```

## Required Completion Artifacts

- Published dataset repo URL.
- Arbutus special remote config recorded in repo docs.
- Checksum values backfilled in `metadata/required_datasets.yaml`.
- Follow-on FEMIC task: add repo as submodule (`P10.6c`).
