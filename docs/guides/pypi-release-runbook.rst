PyPI Release Runbook
====================

This runbook defines the phase-18 release path for FEMIC:

1. Package checks and deterministic wheel verification.
2. TestPyPI publication and install smoke.
3. Production PyPI publication using the exact same artifact set.
4. Release traceability updates in roadmap/changelog.

Pre-release prerequisites
-------------------------

- A clean git working tree.
- Passing quality gates:

  - ``ruff format src tests``
  - ``ruff check src tests``
  - ``mypy src``
  - ``pytest``
  - ``pre-commit run --all-files``
  - ``sphinx-build -b html docs _build/html -W``

- Packaging tools installed:

  .. code-block:: bash

     python -m pip install --upgrade build twine

Packaging and deterministic wheel checks
----------------------------------------

Run the project helper:

.. code-block:: bash

   scripts/release_package_checks.sh

The helper enforces:

- deterministic build epoch (``SOURCE_DATE_EPOCH``),
- ``python -m build``,
- ``twine check dist/*``,
- wheel install/init smoke,
- wheel reproducibility across consecutive builds.

Current known limitation
------------------------

The wheel is reproducible when ``SOURCE_DATE_EPOCH`` is fixed.
The ``sdist`` archive may still vary byte-wise across repeated local builds due
to upstream setuptools archive timestamp behavior.
Release flow therefore treats the wheel as the deterministic artifact and uses
the same built ``dist/*`` files for TestPyPI and PyPI publication.

TestPyPI publication and smoke
------------------------------

Before first publish, configure trusted publishing on TestPyPI:

1. TestPyPI project: ``femic``.
2. Publisher type: GitHub Actions.
3. Repository owner/name: ``UBC-FRESH/femic``.
4. Workflow filename: ``publish-testpypi.yml``.
5. Environment name: ``testpypi``.

Upload artifacts:

.. code-block:: bash

   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD="$TEST_PYPI_API_TOKEN"
   python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

Install smoke in a clean environment:

.. code-block:: bash

   python -m venv /tmp/femic-testpypi-smoke
   /tmp/femic-testpypi-smoke/bin/pip install --upgrade pip
   /tmp/femic-testpypi-smoke/bin/pip install \
     --index-url https://test.pypi.org/simple \
     --extra-index-url https://pypi.org/simple \
     femic==0.1.0
   /tmp/femic-testpypi-smoke/bin/femic --help

Production PyPI publication
---------------------------

Before first production publish, configure trusted publishing on PyPI:

1. PyPI project: ``femic``.
2. Publisher type: GitHub Actions.
3. Repository owner/name: ``UBC-FRESH/femic``.
4. Workflow filename: ``publish-pypi.yml``.
5. Environment name: ``pypi``.

Publish the same artifact set used in TestPyPI validation:

.. code-block:: bash

   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD="$PYPI_API_TOKEN"
   python -m twine upload dist/*

Post-release traceability checklist
-----------------------------------

After successful PyPI publication:

1. Create and push the matching git tag (for example ``v0.1.0``).
2. Record artifact hashes from ``sha256sum dist/*`` in ``CHANGE_LOG.md``.
3. Mark completed phase-18 checklist items in ``ROADMAP.md`` and update
   ``Detailed Next Steps Notes`` with validation outcomes.
4. Keep install instructions in ``README.md`` aligned with the published
   version.

Trusted publishing troubleshooting
----------------------------------

If GitHub Actions fails with ``invalid-publisher`` during publish:

- confirm the workflow filename and environment name exactly match the
  trusted-publisher entry on TestPyPI/PyPI,
- confirm repository owner/name is ``UBC-FRESH/femic``,
- confirm the publish job runs from ``refs/heads/main`` (or an allowed ref),
- re-run the workflow after saving trusted-publisher settings.
