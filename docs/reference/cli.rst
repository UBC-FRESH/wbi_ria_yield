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

TIPSY
-----

.. code-block:: text

   python -m femic tipsy [OPTIONS] COMMAND [ARGS]...

Subcommands

- ``validate``: ``python -m femic tipsy validate [OPTIONS]``

``tipsy validate`` options

- ``--config-dir PATH`` (default: ``config/tipsy``)
- ``--tsa TEXT`` (repeatable)
