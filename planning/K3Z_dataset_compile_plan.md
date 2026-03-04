# K3Z Dataset Compile Plan

This runbook compiles a FEMIC test case for the North Island Community Forest (K3Z),
using the uploaded tenure polygons as a custom management-unit boundary mask.

## Inputs

- K3Z boundary: `data/bc/cfa/k3z/CFA K3Z Tenure.shp` (3 disjoint polygons)
- Provincial VRI source: `data/bc/vri/2019/VEG_COMP_LYR_R1_POLY.gdb` (or configured equivalent)
- TSA boundaries: `data/bc/tsa/FADM_TSA.gdb` (still required by preflight checks)
- TIPSY config: `config/tipsy/tsak3z.yaml`
- Run profile: `config/run_profile.k3z.yaml`

## Step 1a: Compile pre-TIPSY artifacts + `02_input-k3z.dat`

```bash
FEMIC_NO_CACHE=1 PYTHONPATH=src .venv/bin/python -u -m femic run --run-config config/run_profile.k3z.yaml -v --run-id "k3z_$(date -u +%Y%m%d_%H%M%S)"
```

Expected key outputs:

- `data/tipsy_params_tsak3z.xlsx`
- `data/02_input-tsak3z.dat`
- `data/vdyp_prep-tsak3z.pkl`
- `data/vdyp_curves_smooth-tsak3z.feather`

## Manual handoff: BatchTIPSY

Run BatchTIPSY externally using:

- input: `data/02_input-tsak3z.dat`
- output target filename in this repo: `data/04_output-tsak3z.out`

## Step 1b + bundle assembly (post-TIPSY only)

```bash
PYTHONPATH=src .venv/bin/python -m femic tsa post-tipsy --tsa k3z --run-id "k3z_posttipsy_$(date -u +%Y%m%d_%H%M%S)" -v
```

Expected outputs:

- `data/tipsy_curves_tsak3z.csv`
- `data/tipsy_sppcomp_tsak3z.csv`
- `data/model_input_bundle/au_table.csv`
- `data/model_input_bundle/curve_table.csv`
- `data/model_input_bundle/curve_points_table.csv`

## Validation checks

- Verify strata distribution plot for K3Z looks sensible (`plots/strata-tsak3z.*`).
- Check `tipsy_vdyp_tsak3z-*.png` overlays for gross managed/unmanaged anomalies.
- Confirm run manifest under `vdyp_io/logs/run_manifest-<run_id>.json` includes:
  - `femic_boundary_path`
  - `femic_boundary_code`
