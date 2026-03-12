Geospatial Runtime Bootstrap
============================

Why This Matters
----------------

FEMIC geospatial stages rely on Fiona + GDAL. Install failures are common on
fresh environments, especially on Windows, so use the platform-specific ritual
below and verify with FEMIC preflight.

Windows Bootstrap Ritual
------------------------

1. Upgrade packaging tools:

   .. code-block:: bash

      python -m pip install --upgrade pip setuptools wheel

2. Install Fiona from wheels:

   .. code-block:: bash

      python -m pip install fiona

3. If install fails, confirm Python architecture matches available wheels
   (64-bit Python is required for standard Fiona wheels).

Linux Bootstrap Ritual
----------------------

1. Install GDAL system dependencies first:

   .. code-block:: bash

      sudo apt-get update
      sudo apt-get install -y gdal-bin libgdal-dev

2. Install Fiona in your virtual environment:

   .. code-block:: bash

      python -m pip install fiona

Verify Runtime Readiness
------------------------

Run FEMIC geospatial preflight after install:

.. code-block:: bash

   femic prep geospatial-preflight

This checks:

- Fiona import
- GDAL version visibility
- basic shapefile write/read smoke test

Troubleshooting
---------------

- If Fiona imports but shapefile smoke fails:
  verify GDAL shared-library resolution and recreate the virtual environment.
- If GDAL version is not visible:
  reinstall Fiona in a clean environment and rerun preflight.
- You can isolate import-only checks with:

  .. code-block:: bash

     femic prep geospatial-preflight --skip-shapefile-smoke

