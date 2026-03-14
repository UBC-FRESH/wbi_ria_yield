TSA29 Example Instance (Pointer)
================================

Purpose
-------

FEMIC keeps this page as a short pointer for TSA29. Canonical student-facing
documentation lives in the standalone TSA29 instance repository.

Canonical Student Docs
----------------------

- Public repository: ``https://github.com/UBC-FRESH/femic-tsa29-instance``
- Linked submodule path in FEMIC: ``external/femic-tsa29-instance``

Use the standalone docs as source of truth for:

- snapshot-first setup and expected artifacts,
- TSA29 data/provenance and land-base assumptions,
- rebuild and evidence workflow,
- troubleshooting and figure appendix.

Submodule Sync Commands
-----------------------

From the FEMIC workspace top-level directory:

.. code-block:: bash

   git submodule update --init --recursive
   git submodule update --remote external/femic-tsa29-instance

FEMIC-Local Integration Notes
-----------------------------

- TSA29 runtime root in this repository:
  ``external/femic-tsa29-instance``
- Rebuild contract files:
  ``external/femic-tsa29-instance/config/rebuild.spec.yaml`` and
  ``external/femic-tsa29-instance/config/rebuild.allowlist.yaml``
- Rebuild runbook:
  ``external/femic-tsa29-instance/runbooks/REBUILD_RUNBOOK.md``
