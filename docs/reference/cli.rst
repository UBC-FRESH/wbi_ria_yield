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

Prep
----

.. code-block:: text

   python -m femic prep [OPTIONS] COMMAND [ARGS]...

Subcommands

- ``run``: ``python -m femic prep run [OPTIONS]``

``prep run`` options

- ``--data-root PATH`` (default: ``data``)
- ``--output-root PATH`` (default: ``outputs``)
- ``--tsa TEXT`` (repeatable)
- ``--resume``
- ``--dry-run``
- ``--verbose`` / ``-v``

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

TIPSY
-----

.. code-block:: text

   python -m femic tipsy [OPTIONS] COMMAND [ARGS]...

Subcommands

- ``validate``: ``python -m femic tipsy validate [OPTIONS]``

``tipsy validate`` options

- ``--config-dir PATH`` (default: ``config/tipsy``)
- ``--tsa TEXT`` (repeatable)

Export
------

.. code-block:: text

   python -m femic export [OPTIONS] COMMAND [ARGS]...

Subcommands

- ``patchworks``: ``python -m femic export patchworks [OPTIONS]``
- ``woodstock``: ``python -m femic export woodstock [OPTIONS]``

``export patchworks`` options

- ``--tsa TEXT`` (repeatable, required)
- ``--bundle-dir PATH`` (default: ``data/model_input_bundle``)
- ``--checkpoint PATH`` (default: ``data/ria_vri_vclr1p_checkpoint7.feather``)
- ``--output-dir PATH`` (default: ``output/patchworks``)
- ``--start-year INTEGER`` (default: ``2026``)
- ``--horizon-years INTEGER`` (default: ``300``)
- ``--cc-min-age INTEGER`` (default: ``0``)
- ``--cc-max-age INTEGER`` (default: ``1000``)
- ``--cc-transition-ifm TEXT`` (default: ``managed``)
- ``--fragments-crs TEXT`` (default: ``EPSG:3005``)

``export woodstock`` options

- ``--tsa TEXT`` (repeatable, required)
- ``--bundle-dir PATH`` (default: ``data/model_input_bundle``)
- ``--checkpoint PATH`` (default: ``data/ria_vri_vclr1p_checkpoint7.feather``)
- ``--output-dir PATH`` (default: ``output/woodstock``)
- ``--cc-min-age INTEGER`` (default: ``0``)
- ``--cc-max-age INTEGER`` (default: ``1000``)
- ``--fragments-crs TEXT`` (default: ``EPSG:3005``)
