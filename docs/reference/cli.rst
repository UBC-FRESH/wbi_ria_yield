CLI Reference
=============

Top-Level Command
-----------------

.. code-block:: text

   python -m femic [OPTIONS] COMMAND [ARGS]...

Options
-------

- ``--version``: Show version and exit.
- ``--debug``: Enable rich tracebacks.
- ``--help``: Show help and exit.

Commands
--------

- ``run``
- ``prep``
- ``vdyp``
- ``tsa``
- ``tipsy``
- ``export``
- ``patchworks``
- ``instance``

Run
---

.. code-block:: text

   python -m femic run [OPTIONS]

- ``--data-root PATH`` (default: ``data``)
- ``--output-root PATH`` (default: ``outputs``)
- ``--tsa TEXT`` (repeatable)
- ``--resume``
- ``--dry-run``
- ``--verbose`` / ``-v``
- ``--skip-checks``
- ``--debug-rows INTEGER``
- ``--run-id TEXT``
- ``--log-dir PATH`` (default: ``vdyp_io/logs``)
- ``--run-config PATH`` (YAML/JSON run profile)
- ``--instance-root PATH`` (optional; defaults to CWD or ``FEMIC_INSTANCE_ROOT`` env)

Prep
----

.. code-block:: text

   python -m femic prep [OPTIONS] COMMAND [ARGS]...

Subcommands

- ``run``: ``python -m femic prep run [OPTIONS]``
- ``validate-case``: ``python -m femic prep validate-case [OPTIONS]``
- ``geospatial-preflight``: ``python -m femic prep geospatial-preflight [OPTIONS]``

``prep run`` options

- ``--data-root PATH`` (default: ``data``)
- ``--output-root PATH`` (default: ``outputs``)
- ``--tsa TEXT`` (repeatable)
- ``--resume``
- ``--dry-run``
- ``--verbose`` / ``-v``

``prep validate-case`` options

- ``--run-config PATH`` (default: ``config/run_profile.case_template.yaml``)
- ``--tipsy-config-dir PATH`` (default: ``config/tipsy``)
- ``--strict-warnings``
- ``--instance-root PATH``

``prep geospatial-preflight`` options

- ``--strict-warnings``
- ``--skip-shapefile-smoke``

VDYP
----

.. code-block:: text

   python -m femic vdyp [OPTIONS] COMMAND [ARGS]...

Subcommands

- ``run``: ``python -m femic vdyp run [OPTIONS]``
- ``report``: ``python -m femic vdyp report [OPTIONS]``

``vdyp run`` options

- ``--data-root PATH`` (default: ``data``)
- ``--output-root PATH`` (default: ``outputs``)
- ``--tsa TEXT`` (repeatable)
- ``--resume``
- ``--dry-run``
- ``--verbose`` / ``-v``

``vdyp report`` options

- ``--curve-log PATH`` (default: ``vdyp_io/logs/vdyp_curve_events.jsonl``)
- ``--run-log PATH`` (default: ``vdyp_io/logs/vdyp_runs.jsonl``)
- ``--expected-first-age FLOAT`` (default: ``1.0``)
- ``--expected-first-volume FLOAT`` (default: ``1e-06``)
- ``--tolerance FLOAT`` (default: ``1e-12``)
- ``--mismatch-limit INTEGER`` (default: ``10``)
- ``--max-curve-warnings INTEGER``
- ``--max-first-point-mismatches INTEGER``
- ``--max-curve-parse-errors INTEGER``
- ``--max-run-parse-errors INTEGER``
- ``--min-curve-events INTEGER``
- ``--min-run-events INTEGER``

TSA
---

.. code-block:: text

   python -m femic tsa [OPTIONS] COMMAND [ARGS]...

Subcommands

- ``run``: ``python -m femic tsa run [OPTIONS]``
- ``post-tipsy``: ``python -m femic tsa post-tipsy [OPTIONS]``

``tsa run`` options

- ``--data-root PATH`` (default: ``data``)
- ``--output-root PATH`` (default: ``outputs``)
- ``--tsa TEXT`` (repeatable)
- ``--resume``
- ``--dry-run``
- ``--verbose`` / ``-v``

``tsa post-tipsy`` options

- ``--tsa TEXT`` (repeatable, required)
- ``--verbose`` / ``-v``
- ``--run-id TEXT``
- ``--log-dir PATH`` (default: ``vdyp_io/logs``)
- ``--run-config PATH`` (optional; load TSA and managed-curve mode defaults)
- ``--instance-root PATH``

TIPSY
-----

.. code-block:: text

   python -m femic tipsy [OPTIONS] COMMAND [ARGS]...

Subcommands

- ``validate``: ``python -m femic tipsy validate [OPTIONS]``

``tipsy validate`` options

- ``--config-dir PATH`` (default: ``config/tipsy``)
- ``--tsa TEXT`` (repeatable)
- ``--instance-root PATH``

Export
------

.. code-block:: text

   python -m femic export [OPTIONS] COMMAND [ARGS]...

Subcommands

- ``patchworks``: ``python -m femic export patchworks [OPTIONS]``
- ``woodstock``: ``python -m femic export woodstock [OPTIONS]``
- ``release``: ``python -m femic export release [OPTIONS]``

``export patchworks`` options

- ``--tsa TEXT`` (repeatable, required)
- ``--bundle-dir PATH`` (default: ``data/model_input_bundle``)
- ``--checkpoint PATH`` (default: ``data/ria_vri_vclr1p_checkpoint7.feather``)
- ``--output-dir PATH`` (default: ``output/patchworks``)
- ``--start-year INTEGER`` (default: ``2026``)
- ``--horizon-years INTEGER`` (default: ``300``)
- ``--cc-min-age INTEGER`` (default: ``0``)
- ``--cc-max-age INTEGER`` (default: ``1000``)
- ``--cc-transition-ifm TEXT`` (default: unset; no IFM transition assign)
- ``--fragments-crs TEXT`` (default: ``EPSG:3005``)
- ``--ifm-source-col TEXT`` (optional; explicit checkpoint THLB signal column)
- ``--ifm-threshold FLOAT`` (optional; managed when source value > threshold)
- ``--ifm-target-managed-share FLOAT`` (optional; top-N managed by source value)
- ``--seral-stage-config PATH`` (optional; YAML per-AU seral-stage boundaries)
- ``--instance-root PATH``

``export woodstock`` options

- ``--tsa TEXT`` (repeatable, required)
- ``--bundle-dir PATH`` (default: ``data/model_input_bundle``)
- ``--checkpoint PATH`` (default: ``data/ria_vri_vclr1p_checkpoint7.feather``)
- ``--output-dir PATH`` (default: ``output/woodstock``)
- ``--cc-min-age INTEGER`` (default: ``0``)
- ``--cc-max-age INTEGER`` (default: ``1000``)
- ``--fragments-crs TEXT`` (default: ``EPSG:3005``)
- ``--instance-root PATH``

``export release`` options

- ``--case-id TEXT`` (default: ``case``)
- ``--output-root PATH`` (default: ``releases``)
- ``--bundle-dir PATH`` (default: ``data/model_input_bundle``)
- ``--patchworks-dir PATH`` (default: ``output/patchworks_k3z_validated``)
- ``--woodstock-dir PATH`` (optional)
- ``--logs-dir PATH`` (default: ``vdyp_io/logs``)
- ``--run-id TEXT`` (optional)
- ``--strict / --no-strict`` (default: ``--strict``)
- ``--instance-root PATH``

Patchworks Runtime
------------------

.. code-block:: text

   python -m femic patchworks [OPTIONS] COMMAND [ARGS]...

Subcommands

- ``preflight``: ``python -m femic patchworks preflight [OPTIONS]``
- ``build-blocks``: ``python -m femic patchworks build-blocks [OPTIONS]``
- ``matrix-build``: ``python -m femic patchworks matrix-build [OPTIONS]``

``patchworks preflight`` options

- ``--config PATH`` (default: ``config/patchworks.runtime.yaml``)

``patchworks matrix-build`` options

- ``--config PATH`` (default: ``config/patchworks.runtime.yaml``)
- ``--instance-root PATH``
- ``--log-dir PATH`` (default: ``vdyp_io/logs``)
- ``--run-id TEXT``
- ``--interactive``
- ``--instance-root PATH``

``patchworks build-blocks`` options

- ``--config PATH`` (default: ``config/patchworks.runtime.yaml``)
- ``--model-dir PATH`` (optional; inferred from runtime config when omitted)
- ``--fragments-shp PATH`` (optional; defaults to runtime fragments ``.shp``)
- ``--topology-radius FLOAT`` (default: ``200.0``)
- ``--with-topology / --no-topology`` (default: ``--with-topology``)
- ``--instance-root PATH``

Instance Workspace
------------------

.. code-block:: text

   python -m femic instance [OPTIONS] COMMAND [ARGS]...

Subcommands

- ``init``: ``python -m femic instance init [OPTIONS]``

``instance init`` options

- ``--instance-root PATH`` (optional; defaults to CWD)
- ``--overwrite`` (overwrite existing scaffold template files)
- ``--download-bc-vri / --no-download-bc-vri`` (default: ``--download-bc-vri``)
- ``--yes`` / ``-y`` (assume yes for prompts)
