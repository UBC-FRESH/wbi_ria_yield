Model Input Bundle and Export Workflow
======================================

Bundle Artifacts
----------------

FEMIC compiles standardized bundle tables under
``data/model_input_bundle/`` including:

- ``au_table``
- ``curve_table``
- ``curve_points_table``

These feed downstream planning-system exporters.

Patchworks Export
-----------------

Use:

.. code-block:: bash

   PYTHONPATH=src python -m femic export patchworks --tsa <code>

Outputs:

- ``forestmodel.xml``
- ``fragments`` shapefile package

Patchworks-specific schema expectations are documented in
``docs/reference/patchworks-export.rst``.

Woodstock Export
----------------

Use:

.. code-block:: bash

   PYTHONPATH=src python -m femic export woodstock --tsa <code>

Outputs CSV compatibility tables for yield/area/action/transition ingestion.

Assumptions
-----------

- Export steps consume validated bundle tables; they do not re-run upstream
  yield compilation.
- Export naming semantics (for example managed/unmanaged IFM in Patchworks)
  follow downstream system contracts, not legacy notebook naming conventions.
