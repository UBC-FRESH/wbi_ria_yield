API Reference
=============

Developer-facing API documentation for the public Python module surface.

API contract
------------

The API reference is generated from ``src/femic`` modules using
``sphinx.ext.autodoc`` and ``sphinx.ext.autosummary`` with Google-style
docstrings.

Default policy:

- Include public FEMIC modules under ``src/femic``.
- Exclude resource-only payload modules under ``femic.resources``.
- Exclude private members by default (names prefixed with ``_``).
- Keep narrative workflow guidance in Guides and Sample Models; keep API pages
  focused on callable/module reference behavior.

.. toctree::
   :maxdepth: 2

   modules
