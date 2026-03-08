Stage 01b: Post-TIPSY Integration and Comparison
================================================

Scope
-----

Stage 01b ingests BatchTIPSY output, aligns managed-track curves with VDYP
natural-track curves, and writes downstream bundle artifacts.

Required Input
--------------

- ``04_output-<unit>.out`` generated externally from BatchTIPSY.
- Corresponding Stage 01a outputs (AUs, VDYP curves, handoff metadata).

Core Responsibilities
---------------------

- Parse TIPSY output tables into model-ready curve points.
- Align/compare managed and natural curves by AU.
- Generate per-AU comparison plots for QA and tuning.
- Publish updated bundle tables for export stages.

Interpretation Guide
--------------------

- Expect coherent relative behavior between natural and managed trajectories
  according to scenario assumptions.
- Identify AUs where managed curves are implausibly weak/strong and route them
  to parameter tuning or managed-curve transform workflows.

Exit Criteria
-------------

- Non-empty managed and natural curve sets for all intended AUs.
- QA plots generated without parse/fit failures.
- Bundle tables ready for Patchworks/Woodstock export.

Primary Legacy Notebook Coverage
--------------------------------

Derived from ``01b_run-tsa.ipynb`` plus parent orchestration notes in
``00_data-prep.ipynb``.
