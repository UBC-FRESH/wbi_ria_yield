UBC VPN and License Connectivity
================================

Patchworks license checks use ``SPS_LICENSE_SERVER`` in ``<user>@<server>`` form.
For this project the configured value is typically:

.. code-block:: text

   frst424@auth.spatial.ca

Primary Topology
----------------

Use host-level UBC myVPN connectivity and run FEMIC/Patchworks commands from the
same Linux environment while the VPN session is active.

CLI OpenConnect Pattern
-----------------------

Based on the uploaded UBC GNU/Linux myVPN guide:

.. code-block:: bash

   sudo openconnect myvpn.ubc.ca

Then provide credentials at prompt:

- CWL username
- CWL password
- Optional MFA suffix patterns when needed (for example ``@app`` or ``@phone``)

Keep the terminal open while connected.

Diagnostic Steps
----------------

1. Confirm VPN tunnel is active (host networking).
2. Run Patchworks preflight:

   .. code-block:: bash

      PYTHONPATH=src python -m femic patchworks preflight --config config/patchworks.runtime.yaml

3. If reachability fails, verify:

   - DNS resolution for license host
   - TCP reachability to license service port
   - Correct VPN profile/pool and MFA suffix

Failure Signatures
------------------

- ``wine64/wine not found on PATH``:
  install Wine runtime in the execution environment.
- ``Java runtime unavailable inside Wine context``:
  install/configure Windows Java runtime available to Wine.
- ``License host ... unreachable``:
  connect/reconnect UBC VPN and retry preflight.
- ``License value must use '<username>@<server>' format``:
  fix ``patchworks.license_value`` or exported env var content.

Fallback Path
-------------

In-container OpenConnect can be used only where container runtime permits
``/dev/net/tun`` and required capabilities. Host VPN passthrough remains the
recommended default.
