# FEMIC Deployment Instance Quickstart

1. Validate CLI install:
   `femic --help`
2. Validate case templates and external paths:
   `femic prep validate-case --run-config config/run_profile.case_template.yaml`
3. Validate geospatial runtime dependencies (Fiona/GDAL):
   `femic prep geospatial-preflight`
4. Copy and customize `config/run_profile.case_template.yaml`.
5. Copy and customize `config/rebuild.spec.yaml` for your case sequence/invariants.
6. Add/edit `config/tipsy/tsa<code>.yaml` from `config/tipsy/template.case.yaml`.
7. Run compile workflow from this instance root.
