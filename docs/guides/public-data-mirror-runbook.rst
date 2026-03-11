Public Data Mirror Runbook
==========================

This runbook covers the FEMIC DataLad mirror workflow for datasets that are
public but not consistently directly downloadable.

Use this guide together with:

- ``metadata/required_datasets.yaml`` (authoritative inventory)
- ``metadata/datalad_mirror_seed.csv`` (current mirror candidate list)

Scope
-----

The mirror currently targets datasets where source access is unstable or
decommissioned (for example archived HectaresBC ``misc.thlb.tif``).

Maintainer Workflow (Create/Publish Mirror Repo)
------------------------------------------------

1. Create a public GitHub repo for mirrored assets (for example
   ``UBC-FRESH/femic-public-data``).
2. Initialize a DataLad dataset in a local checkout:

   .. code-block:: bash

      datalad create -c text2git femic-public-data
      cd femic-public-data

3. Copy/acquire datasets listed in ``metadata/datalad_mirror_seed.csv`` into
   matching relative paths under the dataset root.
4. Compute and record checksums for mirrored artifacts in
   ``metadata/required_datasets.yaml``.
5. Configure Arbutus S3 special remote and publish:

   .. code-block:: bash

      datalad create-sibling-github --name github --existing reconfigure
      git remote add github git@github.com:UBC-FRESH/femic-public-data.git
      datalad push --to github
      datalad create-sibling-ria --name arbutus-ria <ria-url>
      datalad push --to arbutus-ria

6. Verify fresh clone and selective retrieval works:

   .. code-block:: bash

      cd ..
      datalad clone git@github.com:UBC-FRESH/femic-public-data.git mirror-smoke
      cd mirror-smoke
      datalad get data/misc.thlb.tif

Collaborator Workflow (Clone/Get/Update)
----------------------------------------

The mirror repo is linked into FEMIC at
``external/femic-public-data``. Collaborators should use:

.. code-block:: bash

   git submodule update --init --recursive
   datalad get external/femic-public-data/data/misc.thlb.tif

To refresh metadata and retrieve updated artifacts:

.. code-block:: bash

   git submodule update --remote external/femic-public-data
   datalad update --merge external/femic-public-data
   datalad get -r external/femic-public-data/data

Acceptance Checks
-----------------

- ``metadata/required_datasets.yaml`` and mirror repo paths agree.
- Every mirrored dataset has a populated ``checksum.value``.
- Fresh-clone smoke test can retrieve ``misc.thlb.tif`` via ``datalad get``.
