Stage 00: Data Prep and Inventory Conditioning
==============================================

Scope
-----

Stage 00 prepares stand-level inputs used by all downstream TSA-specific runs.
It covers boundary masking, VRI cleanup, site productivity enrichment,
species-volume compilation, and intermediate checkpoints.

Inputs
------

- TSA or custom boundary geometry
- VRI polygon/layer datasets
- Optional site productivity raster data (species-wise)
- Existing checkpoint feathers when resume paths are enabled

Core Processing Responsibilities
--------------------------------

- Normalize missing categorical/numeric inventory values to deterministic sentinels.
- Compute stratification fields (including lexmatch helpers and forest type classes).
- Build species-wise volume columns from VRI top species fields.
- Compile THLB signals for managed/unmanaged eligibility semantics.
- Persist intermediate checkpoints for restartable execution.

Checkpoint Semantics
--------------------

- Checkpoints are for runtime efficiency and recovery; they are not a substitute
  for source-of-truth raw data.
- Resume behavior must never silently reuse stale artifacts when debug-mode
  constraints (for example ``--debug-rows``) change the effective data population.

Assumptions
-----------

- Stand records represent productive forest land after filtering logic.
- External BC datasets may vary by vintage; field names and join keys must be
  validated explicitly when changing source vintages.
- Raster-overlay logic can be expensive and should be treated as a controlled,
  cache-aware step.

Outputs Consumed by Stage 01a
-----------------------------

- Stand dataframe checkpoints with stratification + species attributes
- VDYP-ready polygon/layer extracts
- Supporting lookup tables for AU assignment and curve linkage

Primary Legacy Notebook Coverage
--------------------------------

See the traceability matrix page for exact mapping of Stage 00 guidance back to
markdown cells in ``00_data-prep.ipynb``.
