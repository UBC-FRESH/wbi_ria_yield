# CFA K3Z Dataset Compile Plan

## Objective

Compile and iterate a working FEMIC model-input dataset for the K3Z management unit
(North Island Community Forest), acknowledging that K3Z is a small multi-block unit
(~2500 ha) where million-hectare TSA stratification defaults can fail.

## Context and Current Status

- K3Z run profile exists: `config/run_profile.k3z.yaml`.
- K3Z TIPSY rules exist and are now FSP-informed: `config/tipsy/tsak3z.yaml`.
- End-to-end pipeline is functional with manual BatchTIPSY handoff.
- Stratum-key controls are now wired into FEMIC run profiles:
  - `selection.stratification.bec_grouping` (`zone|subzone|variant|phase`)
  - `selection.stratification.species_combo_count` (top-N by `SPECIES_PCT_1..6`)
  - `selection.stratification.include_tm_species2_for_single`
- Remaining challenge is model coherence quality (some AU TIPSY-vs-VDYP pairs still
  look implausible), not hard pipeline breakage.

## K3Z-Specific Constraints (Why This Case Is Different)

- Small area and low stand counts create sparse strata and unstable curve fits.
- Top-N strata are dominated by one BEC zone (CWH), so zone-level grouping alone is
  too coarse.
- SI split logic designed for large TSAs can over-fragment K3Z into tiny bins.
- BatchTIPSY field mapping is fragile; DAT fixed-column compatibility is critical.

## Preconditions

1. Environment
- Activated venv.
- `PYTHONPATH=src .venv/bin/python -m femic --help` works.

2. Boundary + VRI inputs
- K3Z boundary shapefile available at `data/bc/cfa/k3z/CFA K3Z Tenure.shp`.
- VRI source available and readable.

3. TIPSY manual handoff readiness
- BatchTIPSY column index map is kept constant between runs.
- Generated `data/02_input-tsak3z.dat` must match that map exactly.

## BatchTIPSY Fixed Column Map (Do Not Change Between Runs)

Use the existing wizard settings (from screenshots), including:

- Table Number: `7-12`
- BEC: `14-17`
- Regen Delay: `40-42`
- Density: `47-51`
- PCT1: `61-63`
- Regen Method: `64`
- DBH: `74-77`
- OAF1: `80-83`
- OAF2: `86-89`
- FIZ: `93`
- SPP1: `97-99`
- SI1: `108-111`
- SPP2/PCT2: `129-131` / `136-137`
- SPP3/PCT3: `155-157` / `162-163`
- GW/GA fields as currently configured in the same wizard profile.

## Execution Workflow

1. Run 01a/K3Z compile
- `PYTHONPATH=src .venv/bin/python -m femic run --run-config config/run_profile.k3z.yaml -v --run-id <id>`
- Confirm console line:
  - `stratum key config: bec_grouping=... species_combo_count=... include_tm_species2_for_single=...`
- Confirm regeneration of:
  - `data/02_input-tsak3z.dat`
  - `data/tipsy_params_tsak3z.xlsx`

2. Manual BatchTIPSY
- Input: `data/02_input-tsak3z.dat`
- Output: replace `data/04_output-tsak3z.out`

3. Run downstream (post-TIPSY)
- `PYTHONPATH=src .venv/bin/python -m femic run --run-config config/run_profile.k3z.yaml -v --resume --run-id <id_post>`

4. Review diagnostics
- `plots/strata-tsak3z.png`
- `plots/vdyp_fitdiag_tsak3z-*.png`
- `plots/tipsy_vdyp_tsak3z-*.png`

## Planned Refinement Experiments (Next)

### A. Finer ecological stratification inputs

Goal: move beyond BEC zone-only grouping for K3Z.

- Use VRI fields:
  - `BEC_ZONE_CODE`
  - `BEC_SUBZONE`
  - `BEC_VARIANT`
  - `BEC_PHASE`
  - (potentially site-related fields such as `SITE_POSITION_MESO`, and SI source fields)
- Build candidate stratification keys:
  - `bec_grouping: subzone` (`BEC_ZONE_CODE + BEC_SUBZONE`)
  - `bec_grouping: variant` (`BEC_ZONE_CODE + BEC_SUBZONE + BEC_VARIANT`)
  - `bec_grouping: phase` where sample size allows.

### B. Leading-species combination stratification

Goal: reduce information loss from single leading-species strata.

- Start with `species_combo_count: 2`.
- Evaluate whether `N=3` improves coherence without over-fragmenting sample sizes.
- Enforce a minimum stand count per candidate stratum; backoff to simpler key if below threshold.

### C. Small-sample adaptive fallback policy

- Keep current adaptive SI split behavior.
- Add stricter fallback to merge sparse bins early for K3Z-like units.
- Prefer stable fits over maximal stratification granularity.

## Data/Metadata Discovery Notes

- Fresh VRI 2024 zip currently fails integrity check (incomplete/corrupt):
  `data/bc/vri/VEG_COMP_LYR_R1_POLY_2024.gdb.zip`.
- Existing 2019 VRI GDB is readable and includes key fields needed for planned
  refinements (confirmed):
  - `BEC_ZONE_CODE`, `BEC_SUBZONE`, `BEC_VARIANT`, `BEC_PHASE`
  - `SITE_INDEX`, `EST_SITE_INDEX`, `EST_SITE_INDEX_SPECIES_CD`
  - `SPECIES_CD_1..6`, `SPECIES_PCT_1..6`

## Completion Criteria for K3Z Prototype

- Deterministic rerun path documented and repeatable.
- DAT -> BatchTIPSY -> post-TIPSY loop runs without field-map edits.
- K3Z strata/fit diagnostics regenerate consistently.
- At least one refined stratification scheme (subzone and/or species-combo based)
  produces visibly improved AU-level TIPSY-vs-VDYP coherence.
