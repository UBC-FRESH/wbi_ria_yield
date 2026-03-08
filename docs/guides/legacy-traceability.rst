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
