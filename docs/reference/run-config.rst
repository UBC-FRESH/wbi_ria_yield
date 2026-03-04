Run Config Profile
==================

``femic run`` accepts ``--run-config`` pointing to a YAML or JSON profile.
Profile values seed CLI defaults for TSA selection and mode flags.

Schema
------

.. code-block:: yaml

   selection:
     tsa: ["08", "16"]      # optional list[str]
     strata: ["SBSdk"]      # optional list[str], currently informational only
     boundary_path: "data/bc/cfa/k3z/CFA K3Z Tenure.shp"  # optional custom boundary path
     boundary_layer: null   # optional layer name/index for multi-layer GIS sources
     boundary_code: "k3z"   # optional label used as FEMIC TSA code for boundary mode
   modes:
     resume: true           # optional bool
     dry_run: false         # optional bool
     verbose: false         # optional bool
     skip_checks: false     # optional bool
     debug_rows: 250        # optional int
   run:
     run_id: "dev-profile"  # optional str
     log_dir: "vdyp_io/profile_logs"  # optional str path

Precedence
----------

- CLI values override config values for ``--tsa`` and ``--debug-rows`` when explicitly provided.
- Boolean flags use additive behavior (CLI or config can enable).
- ``--run-id`` overrides ``run.run_id`` when provided.
- ``--log-dir`` overrides config unless left at the default ``vdyp_io/logs``.
- Boundary fields are profile-driven only (no dedicated CLI flags yet). When
  ``selection.boundary_path`` is set, legacy extraction runs in custom-boundary mode
  and bypasses checkpoint reuse.

Example
-------

A template profile is included at ``config/run_profile.example.yaml``.
When provided, run manifests also record ``run_config_path`` and
``run_config_sha256`` provenance metadata plus output version annotations.
For deterministic VDYP bootstrap sampling, set ``FEMIC_SAMPLING_SEED`` to an
integer value.
Run manifests include a ``runtime_parameters`` section to capture the effective
FEMIC execution settings used for each run.
