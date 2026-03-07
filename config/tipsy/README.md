# TIPSY Configuration Handoff (Draft)

This directory is for **expert-authored, TSA-specific TIPSY configuration** that FEMIC can use to
build batch TIPSY input tables.

## Why this exists

TIPSY is a manual GUI boundary in the current production workflow:

1. Expert downloads TSR documentation/data package for each TSA.
2. Expert derives AU-wise TIPSY logic and maps TSR AUs to FEMIC AUs.
3. FEMIC builds batch TIPSY input from expert-provided config.
4. User runs batch TIPSY manually on Windows and uploads raw outputs.
5. FEMIC resumes fully automated downstream processing.

This config layer is meant to replace hard-coded TSA dict logic in `01a_run-tsa.py`.

## Variability seen in legacy TSA examples

The five legacy TSA-specific dict implementations (`08`, `16`, `24`, `40`, `41`) show substantial
variation:

- Union of referenced TIPSY fields across all five TSAs: `32`
- Fields referenced by TSA:
  - `08`: `16`
  - `16`: `32`
  - `24`: `32`
  - `40`: `12`
  - `41`: `22`

So the schema must support:

- multiple rule styles per TSA (species-only, BEC+species, forest-type branches, etc.)
- partial field overrides
- differing field completeness across TSAs
- explicit provenance/comments for expert interpretation choices

## Proposed config structure (high level)

Each TSA file should contain:

- metadata: source TSR references, author, date, notes
- AU matching logic: how FEMIC AU candidates map to TSR-derived parameter rules
- rule set: condition blocks and resulting TIPSY parameter assignments
- defaults/fallbacks: optional shared values and explicit failure behavior

See `config/tipsy/template.tsa.yaml` for a concrete draft shape.

## SI transform tuning

Config assignments can now tune TIPSY SI values per side (`e`/`f`) using:

- `SI_c1`
- `SI_c2`

FEMIC computes baseline SI from VDYP and then applies:

`SI_final = SI_c1 * SI_baseline + SI_c2`

Legacy additive `SI_offset` is still supported for backward compatibility and is applied
additively after the linear transform.
