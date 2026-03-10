Deployment Instance Setup
=========================

FEMIC now supports deployment-instance-first execution. The Python package is
generic; case-specific configs, local data paths, and generated artifacts live
in your instance workspace.

Create an Instance
------------------

From an empty directory:

.. code-block:: bash

   femic instance init

By default this scaffolds:

- ``config/`` and ``config/tipsy/`` templates
- ``data/`` and ``data/downloads/``
- ``output/``
- ``vdyp_io/logs/``
- workspace ``.gitignore`` and ``QUICKSTART.md``

BC VRI Auto-Download
--------------------

``femic instance init`` prompts (default ``Y``) to download standard BC-wide
VRI datasets into ``data/downloads/`` and extract them into
``data/bc/vri/2024/``:

- ``VEG_COMP_LYR_R1_POLY_2024.gdb.zip``
- ``VEG_COMP_VDYP7_INPUT_POLY_AND_LAYER_2024.gdb.zip``

You can skip this step:

.. code-block:: bash

   femic instance init --no-download-bc-vri

Or run non-interactive bootstrap:

.. code-block:: bash

   femic instance init --yes

Instance Root Resolution
------------------------

Operational commands accept ``--instance-root`` and otherwise resolve paths by:

1. ``--instance-root``
2. ``FEMIC_INSTANCE_ROOT`` environment variable
3. current working directory

This allows running FEMIC from any location while keeping all deployment files
scoped to one workspace root.
