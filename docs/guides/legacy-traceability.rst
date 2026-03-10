Legacy Notebook Traceability
============================

This page preserves provenance from legacy notebook narrative content to the
new guides documentation.

Coverage Inventory
------------------

Legacy markdown cells inventoried:

- ``00_data-prep.ipynb``: 51 markdown cells
- ``01a_run-tsa.ipynb``: 25 markdown cells
- ``01b_run-tsa.ipynb``: 2 markdown cells
- Total mapped records: 77

Each record is classified as one of:

- assumptions
- step intent
- interpretation guidance
- failure mode
- operator action

Coverage Matrix Fields
----------------------

- ``notebook`` and ``cell_index``: source notebook provenance
- ``classification``: intent class for the source note
- ``status``: ``mapped`` or ``retired``
- ``target_doc``: destination guide page
- ``pre_phase5_location``: where the content lived before this phase
  (mostly ``gap``)
- ``preview``: truncated source markdown text
- ``notes``: rationale for retired/exception cases

Coverage matrix CSV: ``docs/guides/legacy_notebook_coverage.csv``

.. literalinclude:: legacy_notebook_coverage.csv
   :language: text
   :lines: 1-40

Retired Guidance
----------------

Rows marked ``retired`` capture legacy exploratory notes (for example explicitly
failed historical attempts) that are preserved for context but not recommended
as active workflow.

Notebook Output Cleanup Policy
------------------------------

Legacy notebooks can embed host-local absolute paths (for example user home
paths captured in traceback/output cells). To keep the repository portable and
avoid stale machine-specific leakage:

- Treat notebook outputs as ephemeral by default.
- Before committing notebook edits, clear outputs and execution counts unless an
  output snapshot is intentionally required for provenance.
- If a provenance snapshot is intentionally retained, sanitize host-local path
  fragments when practical and document the reason in ``CHANGE_LOG.md``.
- Keep legacy slug/path history in audit-trail documents only
  (for example ``ROADMAP.md`` and ``CHANGE_LOG.md``), not in active runtime
  config or user-facing workflow instructions.

Recommended cleanup command:

.. code-block:: bash

   jupyter nbconvert --clear-output --inplace 00_data-prep.ipynb 01a_run-tsa.ipynb 01b_run-tsa.ipynb
