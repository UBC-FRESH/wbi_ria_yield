Known Limitations and Human-in-the-Loop Boundaries
===================================================

TIPSY Boundary
--------------

- BatchTIPSY remains an external GUI/manual boundary.
- FEMIC can prepare deterministic handoff files and parse returned outputs,
  but cannot replace operator-run BatchTIPSY execution in current workflow.

Data Vendor/Format Constraints
------------------------------

- Some BC datasets are delivered in formats that require special extraction
  or conversion tooling.
- Dataset vintages can change fields and behavior; source validation is required
  before swapping vintages in production workflows.

Modeling Limitations
--------------------

- Small-area units can break stratification assumptions tuned for large TSAs.
- SI signal may appear weak without careful split/merge and fit controls.
- Species-wise managed trajectories may require explicit tuning when vendor
  outputs are inconsistent with scenario intent.

Documentation Scope Boundary
----------------------------

- Published Sphinx docs are user/developer guides and reference contracts.
- Large proprietary PDFs and ad hoc source material are stored under
  ``reference/`` and are not republished through Sphinx pages.
