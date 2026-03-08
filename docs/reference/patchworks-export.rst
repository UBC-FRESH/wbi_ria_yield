Patchworks Export Contract
==========================

``femic export patchworks`` writes two artifacts:

- ``forestmodel.xml``
- ``fragments/fragments.shp`` (plus shapefile sidecars)

ForestModel XML requirements
----------------------------

The exporter now enforces these required structure elements before writing XML:

- Root tag: ``ForestModel``
- Root attributes: ``horizon``, ``year``, ``match``
- ``<input>`` node with attributes: ``block``, ``area``, ``age``
- ``<output>`` node
- ``<define field="AU" column="AU">``
- ``<define field="IFM" column="IFM">``
- ``<define field="treatment">``
- A ``unity`` curve with at least one point
- At least one ``<treatment label="CC" ...>``
- Every ``<attribute><curve idref="...">`` must reference an existing ``<curve id="...">``

Fragments shapefile requirements
--------------------------------

The exporter validates these required fields before writing:

- ``BLOCK``: unique integer block ID (non-negative)
- ``AREA_HA``: numeric area in hectares (strictly positive)
- ``F_AGE``: numeric forest age (non-negative)
- ``AU``: numeric analysis-unit ID (non-negative)
- ``IFM``: management mode, one of ``managed`` or ``unmanaged``
- ``TSA``: TSA code label
- ``geometry``: non-null, non-empty geometry

The fragments dataset must also carry a CRS.

CLI usage
---------

Basic usage:

.. code-block:: bash

   PYTHONPATH=src python -m femic export patchworks --tsa k3z

Useful overrides:

- ``--bundle-dir``: alternate bundle source (``au_table.csv``, ``curve_table.csv``, ``curve_points_table.csv``)
- ``--checkpoint``: alternate stand checkpoint feather (must include geometry, TSA, AU, age)
- ``--output-dir``: export destination
- ``--start-year``, ``--horizon-years``, ``--cc-min-age``, ``--cc-max-age``, ``--fragments-crs``
