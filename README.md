# wbi_ria_yield

[![DOI](https://zenodo.org/badge/430531073.svg)](https://zenodo.org/badge/latestdoi/430531073)

## CLI

Run the legacy pipeline through the FEMIC CLI:

```bash
femic run --tsa 08 --resume
```

`femic run` executes the legacy script in an isolated subprocess and filters known
non-fatal shutdown noise lines from legacy stderr output.
Each run writes a manifest at `vdyp_io/logs/run_manifest-<run_id>.json` and uses
run-scoped VDYP log files (per TSA + run id).
For each TSA, raw VDYP process streams are also captured to:
`vdyp_io/logs/vdyp_stdout-tsa<tsa>-<run_id>.log` and
`vdyp_io/logs/vdyp_stderr-tsa<tsa>-<run_id>.log`.

### Quickstart (End-to-End)

1. Validate base install:

```bash
PYTHONPATH=src python -m femic --help
```

2. Validate TIPSY config handoff files:

```bash
PYTHONPATH=src python -m femic tipsy validate --config-dir config/tipsy --tsa 08
```

3. Run one TSA with resume enabled:

```bash
PYTHONPATH=src python -m femic run --tsa 08 --resume
```

4. Summarize VDYP diagnostics:

```bash
PYTHONPATH=src python -m femic vdyp report
```

5. After manual BatchTIPSY output is uploaded, run downstream stages only (01b + bundle):

```bash
PYTHONPATH=src python -m femic tsa post-tipsy --tsa 29 -v
```

This command writes a run manifest to ``vdyp_io/logs/`` (override with ``--log-dir`` and
``--run-id``).
When `data/ria_vri_vclr1p_checkpoint8.feather` is available, post-TIPSY bundle assembly also
adds species-proportion curves for all top-6 VRI species present in the selected TSA(s):
`unmanaged_species_prop_<SPP>` and `managed_species_prop_<SPP>` (single-point curves at `x=1`).

6. Export Patchworks starter package (ForestModel XML + fragments shapefile):

```bash
PYTHONPATH=src python -m femic export patchworks --tsa k3z
```

By default this command reads bundle tables from `data/model_input_bundle/` and stand
geometry from `data/ria_vri_vclr1p_checkpoint7.feather`, then writes:
- `output/patchworks/forestmodel.xml`
- `output/patchworks/fragments/fragments.shp`

7. Export Woodstock compatibility CSV package:

```bash
PYTHONPATH=src python -m femic export woodstock --tsa k3z
```

This currently writes:
- `output/woodstock/woodstock_yields.csv`
- `output/woodstock/woodstock_areas.csv`
- `output/woodstock/woodstock_actions.csv`
- `output/woodstock/woodstock_transitions.csv`

### Config-Driven Runs

Use a YAML/JSON profile to seed TSA selection and run modes:

```bash
PYTHONPATH=src python -m femic run --run-config config/run_profile.example.yaml
```

Profile schema and precedence are documented at `docs/reference/run-config.rst`.
`--run-config` values are merged with CLI options; explicit CLI values still win
for `--tsa`, `--debug-rows`, and `--run-id`.

Custom management-unit runs are also supported via run profile fields:
`selection.boundary_path`, `selection.boundary_layer`, and
`selection.boundary_code`. Example profile:
`config/run_profile.k3z.yaml` (North Island Community Forest test case).

### Reproducibility Controls

Set deterministic VDYP sampling with:

```bash
export FEMIC_SAMPLING_SEED=42
```

Run manifests include:

- `runtime_versions` (tool/package versions)
- `runtime_parameters` (effective FEMIC env/runtime settings)
- `config_provenance` (`run_config_path`, `run_config_sha256`)
- `outputs` (`output_root`, `version_tag`, `versioned_output_dir`)

For faster debugging, limit the number of VRI rows processed (this disables cached checkpoints
and output reuse):

```bash
femic run --tsa 08 --resume --debug-rows 1000
```

You can override run metadata/log routing:

```bash
femic run --tsa 08 --resume --run-id mytest01 --log-dir vdyp_io/logs
```

If `--tsa` is omitted, defaults are loaded from `config/dev.toml` (`[run].default_tsa_list`).

Note: In debug mode, some strata may lack VDYP curves. These are skipped with a warning.
Rows whose strata do not map to an AU/curve (missing VDYP curves) are dropped with a warning
summary.
Debug mode also skips final TSA stand shapefile export by default; set
`FEMIC_SKIP_STANDS_SHP=0` to force shapefile output while debugging.
`ipyparallel` is disabled by default (`FEMIC_DISABLE_IPP=1`) for stability;
set `FEMIC_DISABLE_IPP=0` to re-enable controller-backed execution.
Row-wise operations default to pandas `.apply(...)`; set `FEMIC_USE_SWIFTER=1`
to opt back into swifter acceleration.

VDYP diagnostics are written to `vdyp_io/logs/` as JSONL files (e.g.,
`vdyp_runs.jsonl`, `vdyp_curve_events.jsonl`) to capture run status and curve-fit
warnings.
Summarize these logs with:

```bash
femic vdyp report
```

For regression checks in CI, apply warning-budget thresholds (command exits non-zero on breach):

```bash
femic vdyp report --max-curve-warnings 2 --max-first-point-mismatches 0 --min-curve-events 5 --min-run-events 6
```

Yield curves are anchored to a quasi-origin point `(1, 1e-6)` so downstream positive-value
filters can remain unchanged while avoiding zero-age intercept issues.

Raw BC datasets are expected under `../data` relative to the repo root (e.g.,
`../data/bc/vri/2019/VEG_COMP_LYR_R1_POLY.gdb`). You can override this by setting
`FEMIC_EXTERNAL_DATA_ROOT` to a different base path.

## TIPSY Handoff Boundary

The TIPSY stage is currently a human-in-the-loop boundary:

1. Expert modeller derives TSA/AU-specific TIPSY parameter logic from TSR data packages.
2. FEMIC generates batch TIPSY input tables from that logic.
3. Batch TIPSY is run manually in Windows GUI.
4. Raw TIPSY output is copied back to Linux for automated downstream stages.

Draft config scaffolding for this handoff now lives in `config/tipsy/`:

- `config/tipsy/README.md`
- `config/tipsy/template.tsa.yaml`
- `config/tipsy/tsa08.yaml` and `config/tipsy/tsa16.yaml` (concrete TSA configs migrated from
  legacy logic)
- `config/tipsy/tsa24.yaml` (BEC-dependent branching migration from legacy logic)
- `config/tipsy/tsa40.yaml` and `config/tipsy/tsa41.yaml` (dynamic species-rank and
  forest-type-driven migrations)

If a TSA config file exists at `config/tipsy/tsaXX.yaml` (or `.yml`), the legacy
run path now prefers that config for TIPSY parameter generation for that TSA.
Override the config directory with `FEMIC_TIPSY_CONFIG_DIR`.
If no config exists for a requested TSA, the run now fails fast unless
`FEMIC_TIPSY_USE_LEGACY=1` is set.

Validate TIPSY config handoff files before running:

```bash
femic tipsy validate --config-dir config/tipsy --tsa 08 --tsa 16
```

Config-driven TIPSY rules now also support deterministic weak-mapping controls:

- `species_code_overrides` (for example `DR: FD`, `SX: SW`)
- `siteprod_si_fallback_by_species` (species-specific SI fallback values when siteprod
  values are missing/invalid)

VDYP fit diagnostics also emit per-stratum L/M/H comparison overlays at:
`plots/vdyp_lmh_tsa<tsa>-<stratum>-<stratum_code>.png`.
