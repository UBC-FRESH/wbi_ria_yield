K3Z Patchworks Model
====================

Purpose and Scope
-----------------

``models/k3z_patchworks_model`` is the in-repo teaching prototype Patchworks
model for K3Z. It is intended for:

- student onboarding to Patchworks model anatomy,
- reproducible Matrix Builder rebuilds from FEMIC outputs,
- scenario setup using a known, inspectable baseline.

This is not a black-box package. The goal is that students can inspect every
major input/output and understand what should or should not be edited directly.

Authoritative Location and Provenance
-------------------------------------

- Source of truth: ``models/k3z_patchworks_model``
- Runtime config for Windows collaborators:
  ``config/patchworks.runtime.windows.yaml``
- Layout target: mirrors the Patchworks sample-model folder pattern
  (same top-level model directories).
- Detailed metadata lineage: ``docs/sample-models/k3z-metadata-lineage.rst``
  and ``models/k3z_patchworks_model/metadata/lineage_registry.yaml``.

Model Anatomy
-------------

Top-level model directories and their role:

- ``analysis/``: Patchworks PIN entrypoint and GUI/report wiring.
- ``blocks/``: block boundary and topology inputs for PIN.
- ``data/``: Matrix Builder tabular/geometry input shapefile.
- ``scripts/``: BeanShell logic sourced by PIN and data-prep scripts.
- ``tracks/``: Matrix Builder outputs consumed by PIN.
- ``yield/``: ForestModel definition and seral-stage config.
- ``roads/``, ``imagery/``, ``misc/``, ``scenarios/``: reserved model folders;
  currently mostly placeholders in this prototype.

Key files within that structure:

- ``analysis/base.pin`` (horizon, inputs, map layers, target init)
- ``blocks/blocks.shp`` and ``blocks/topology_blocks_200r.csv``
- ``data/fragments.*``
- ``scripts/dataPrep/prepareBlocks.bsh``
- ``scripts/targets/flowTargets.bsh`` and ``scripts/targets/seralStages.bsh``
- ``tracks/blocks.csv``, ``tracks/features.csv``, ``tracks/strata.csv``,
  ``tracks/protoaccounts.csv``, ``tracks/accounts.csv``
- ``yield/forestmodel.xml`` and ``yield/seral_stages.yaml``

Current baseline snapshot from tracked artifacts:

- ``tracks/blocks.csv`` rows: 218
- ``tracks/strata.csv`` AU count: 14 (managed-only baseline)
- ``tracks/accounts.csv`` account count: 125
- seral inventory accounts: 5 ``feature.Seral.*``
- seral treatment-consequence accounts: 70
  ``product.Seral.area.<stage>.<au>.CC``

Build and Rebuild Workflow
--------------------------

All commands below are run from repository root.

1. Validate Patchworks runtime wiring first:

.. code-block:: powershell

   PYTHONPATH=src python -m femic patchworks preflight --config config/patchworks.runtime.windows.yaml

2. Build/update ``blocks`` artifacts (1:1 stand:block, optional topology):

.. code-block:: powershell

   PYTHONPATH=src python -m femic patchworks build-blocks --config config/patchworks.runtime.windows.yaml --topology-radius 200

Expected artifacts:

- ``models/k3z_patchworks_model/blocks/blocks.shp``
- ``models/k3z_patchworks_model/blocks/topology_blocks_200r.csv`` (when
  ``--with-topology`` is enabled, default true)

3. Rebuild tracks with Matrix Builder:

.. code-block:: powershell

   PYTHONPATH=src python -m femic patchworks matrix-build --config config/patchworks.runtime.windows.yaml --run-id k3z_rebuild_YYYYMMDD

Expected behavior:

- matrix outputs refreshed under ``models/k3z_patchworks_model/tracks``;
- success is artifact-driven (not JVM return code alone);
- FEMIC copies ``tracks/protoaccounts.csv`` to ``tracks/accounts.csv``;
- if ``accounts.csv`` already exists, FEMIC moves it to
  ``tracks/accounts_backup_<timestamp>.csv`` first.

4. Review logs/manifests after rebuild:

- ``vdyp_io/logs/patchworks_matrixbuilder_stdout-<run_id>.log``
- ``vdyp_io/logs/patchworks_matrixbuilder_stderr-<run_id>.log``
- ``vdyp_io/logs/patchworks_matrixbuilder_manifest-<run_id>.json``

Runtime Pathing Notes
---------------------

``config/patchworks.runtime.windows.yaml`` currently uses config-relative paths
for model inputs/outputs:

- ``matrix_builder.fragments_path: ../models/k3z_patchworks_model/data/fragments.dbf``
- ``matrix_builder.output_dir: ../models/k3z_patchworks_model/tracks``
- ``matrix_builder.forestmodel_xml_path: ../models/k3z_patchworks_model/yield/forestmodel.xml``

Because these are relative to the config file location (``config/``), users can
run commands from repository root without editing absolute paths.

If you need to refresh model inputs from exporter output, rebuild ForestModel +
fragments first, then update the model folder:

.. code-block:: powershell

   PYTHONPATH=src python -m femic export patchworks --tsa k3z --seral-stage-config config/seral.k3z.yaml
   Copy-Item output/patchworks/forestmodel.xml models/k3z_patchworks_model/yield/forestmodel.xml -Force
   Copy-Item output/patchworks/fragments/* models/k3z_patchworks_model/data/ -Force

Key Parameters and Assumptions
------------------------------

- Planning horizon in PIN: ``30`` periods x ``10`` years
  (``analysis/base.pin``).
- Current IFM baseline in compiled tracks: managed-only
  (see ``tracks/strata.csv`` ``IFM`` values).
- 1:1 stand:block policy for K3Z teaching model:
  ``BLOCK`` equals stand identity in fragments/blocks prep.
- Topology radius baseline: ``200`` meters.
- CC min age in exported ForestModel: ``CMAI(managed_total_curve) - 20``
  (clamped) with fallback to ``--cc-min-age`` only when needed.
- Seral defaults:
  regenerating 0-5, young 6-25, immature 26-CMAI, mature CMAI+1 to
  min(peak yield age, 200), overmature mature+1 and older.
- NDY flow target window in target script:
  ``periods - 9`` through ``periods``.

Where to change assumptions:

- export/seral assumptions: ``config/seral.k3z.yaml`` and export CLI options.
- target-account logic: ``scripts/targets/flowTargets.bsh``.
- seral account validation logic: ``scripts/targets/seralStages.bsh``.
- Patchworks UI/map/target wiring: ``analysis/base.pin``.

Parameter Risk and Suggested Ranges
-----------------------------------

Use these as practical guardrails for student experimentation:

.. list-table::
   :header-rows: 1

   * - Parameter
     - Suggested range
     - Risk if pushed outside range
   * - IFM managed share (via ``--ifm-target-managed-share``)
     - ``0.6`` to ``0.95`` for teaching scenarios
     - Very low values collapse managed area; very high values remove unmanaged contrast.
   * - IFM threshold (via ``--ifm-threshold``)
     - tuned to observed checkpoint signal distribution
     - Wrong threshold can silently misclassify most stands.
   * - Topology radius (``--topology-radius``)
     - ``100`` to ``400`` metres
     - Too small fragments adjacency graph; too large over-connects blocks.
   * - Seral stage boundaries (YAML)
     - keep monotonic non-overlapping age intervals
     - Invalid boundaries break semantic interpretation and may produce sparse accounts.
   * - CC min age override
     - prefer exporter default (``CMAI-20`` logic)
     - Manual hard-coded values can create unrealistic early/late harvest eligibility.
   * - Horizon in PIN
     - maintain period width consistency with account/target logic
     - Changing horizon without target script updates can distort NDY/even-flow behavior.

Edit Policy: Safe vs Generated
------------------------------

Safe to edit directly:

- ``analysis/base.pin`` (targets, map layers, report wiring),
- ``scripts/targets/*.bsh`` (target initialization logic),
- ``yield/seral_stages.yaml`` and ``config/seral.k3z.yaml``.

Regenerate instead of hand-editing:

- ``tracks/*.csv`` (Matrix Builder outputs),
- ``blocks/blocks.*`` and ``blocks/topology_blocks_200r.csv`` from
  ``femic patchworks build-blocks``,
- ``yield/forestmodel.xml`` from ``femic export patchworks``.

Edit with care (authoritative inputs):

- ``data/fragments.*`` is an upstream model input; treat it as source data and
  rebuild dependent artifacts afterward.

Backup and Recovery Conventions
-------------------------------

- Keep matrix-build manifests and logs under ``vdyp_io/logs`` for every
  rebuild run id.
- Rely on automatic account backup during matrix rebuild:
  existing ``tracks/accounts.csv`` is moved to
  ``tracks/accounts_backup_<timestamp>.csv`` before overwrite.
- Before high-impact model edits (PIN/scripts/XML), create a git checkpoint
  commit so rollback stays one command away.
- If a generated family looks inconsistent, regenerate from upstream inputs
  instead of manual CSV surgery:
  export patchworks -> build blocks -> matrix build.
- For release candidates, treat ``models/k3z_patchworks_model/metadata`` docs
  and registry as required artifacts, not optional notes.

Seral-Stage Account Semantics
-----------------------------

Current semantics are split intentionally:

- forest state/inventory accounts:
  ``feature.Seral.<stage>``
- treatment consequence area accounts:
  ``product.Seral.area.<stage>.<au_id>.CC``

This lets students answer both:

- inventory question: "How much area is in each seral stage?"
- treatment question: "How much CC area was applied by AU and stage?"

The PIN also defines a Seral Stages map layer using ``DitherTheme`` over
``feature.Seral.*`` in ``analysis/base.pin``.

Scenario Comparison Guidance
----------------------------

Use this workflow for classroom interpretation of trajectory changes.

Within-scenario trajectory checks:

1. Track inventory-stage area over time using ``feature.Seral.*`` accounts.
2. Track treatment-consequence area over time using
   ``product.Seral.area.<stage>.<au_id>.CC`` accounts.
3. Compare early vs late horizon periods for harvest pressure shift:
   overmature-focused vs immature/mature-focused CC area.

Cross-scenario comparison checks:

1. Keep model structure fixed (same horizon, PIN wiring, account schema).
2. Change only intended levers (for example IFM tuning or seral boundaries).
3. Compare period-aligned trajectories for:
   - total CC area by stage (sum of ``product.Seral.area.<stage>.*.CC``),
   - AU-level stage mix in treatment consequences,
   - standing inventory stage mix via ``feature.Seral.*``.

Report templates (minimum set):

.. list-table::
   :header-rows: 1

   * - Report question
     - Account source
     - Suggested aggregation
   * - Is harvest shifting into younger forest over time?
     - ``product.Seral.area.<stage>.<au_id>.CC``
     - Sum by stage per period; compare stage shares across time.
   * - Are scenarios preserving more mature/overmature inventory?
     - ``feature.Seral.mature`` and ``feature.Seral.overmature``
     - Period-level totals and percent of total managed area.
   * - Which AUs drive the trajectory change?
     - ``product.Seral.area.<stage>.<au_id>.CC``
     - Pivot by AU and stage; rank delta between scenarios.
   * - Is total harvest pressure stable while stage mix changes?
     - ``product.HarvestedVolume.managed.Total.CC`` plus seral area accounts
     - Compare total harvested volume with stage-specific CC area shares.

Release Readiness Checklist
---------------------------

Use this checklist before distributing a K3Z model revision to students:

1. Rebuild artifacts in order:
   export patchworks -> build blocks -> matrix-build.
2. Confirm expected model inputs exist and are current:
   ``data/fragments.*``, ``yield/forestmodel.xml``, ``blocks/blocks.*``,
   ``blocks/topology_blocks_200r.csv``.
3. Confirm matrix outputs and account sync:
   ``tracks/protoaccounts.csv`` and ``tracks/accounts.csv`` present, with
   any prior account customizations preserved in timestamped backup files.
4. Verify PIN loads cleanly and map/targets initialize without runtime errors.
5. Verify metadata docs are current:
   ``docs/sample-models/k3z.rst``,
   ``docs/sample-models/k3z-metadata-lineage.rst``, and
   ``models/k3z_patchworks_model/metadata/lineage_registry.yaml``.
6. Capture run evidence and update repo records:
   append `ROADMAP.md` Detailed Next Steps note and matching `CHANGE_LOG.md`
   entry for the release build.

Troubleshooting
---------------

Common failure signatures and fixes:

- ``Output directory ... does not exists`` from Matrix Builder:
  ensure ``tracks/`` exists or re-run through FEMIC
  (FEMIC creates output dir before launch).
- PIN parse error at line 1 with ``\ufeff``:
  file was saved with UTF-8 BOM; re-save ``analysis/base.pin`` without BOM.
- ``Null Pointer ... getParentFile()`` in BeanShell sourced scripts:
  avoid script-path introspection assumptions; use PIN-relative paths
  (current target scripts already do this).
- model opens but seral accounts/targets are missing:
  confirm ``tracks/accounts.csv`` contains ``feature.Seral.*`` and that latest
  matrix-build manifest shows ``accounts_sync.status: synced``.
- unexpectedly low managed area:
  inspect IFM assignments in ``tracks/strata.csv`` and revisit export IFM
  controls (``--ifm-source-col``, ``--ifm-threshold``,
  ``--ifm-target-managed-share``).

For run diagnostics, inspect the corresponding manifest JSON under
``vdyp_io/logs`` first, then the run-scoped stdout/stderr logs.
