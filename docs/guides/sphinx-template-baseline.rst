Sphinx Template Baseline
========================

Canonical Reference
-------------------

FRESH lab docs template baseline is defined from FHOPS:
`https://github.com/UBC-FRESH/fhops` (``docs/conf.py`` and CI docs build behavior).

Required Baseline Components
----------------------------

- Theme: ``sphinx_rtd_theme`` (with fallback allowed only for local missing deps).
- Core extensions:
  ``sphinx.ext.autodoc``, ``sphinx.ext.autosummary``,
  ``sphinx.ext.napoleon``, ``sphinx.ext.viewcode``.
- Autosummary generation enabled.
- Typehint rendering style:
  ``autodoc_typehints = "description"``.
- Theme options:
  ``collapse_navigation: false``, ``navigation_depth: 3``.
- Warning-as-error docs build:
  ``sphinx-build ... -W``.
- GitHub Pages publish workflow with:
  ``pages: write`` and ``id-token: write`` permissions,
  ``actions/upload-pages-artifact@v4``,
  ``actions/deploy-pages@v4``.

Alignment Targets
-----------------

- FEMIC parent docs config/workflow.
- Standalone ``femic-k3z-instance`` docs config/workflow.

K3Z Content-Depth Guardrail
---------------------------

Template alignment must not reduce TSR-style K3Z metadata depth. Required
data-package pages and section contracts remain mandatory.
