Gateway Runtime
===============

This section documents the core runtime components of the ThingsBoard Edge Gateway.
These modules define the application entry point, startup sequence, and initial
device provisioning.

Main Loop
---------

.. automodule:: main
   :members:
   :undoc-members: False

Self-Provisioning
-----------------

This module implements the initial device self-provisioning workflow used to
obtain credentials and establish a trusted connection to ThingsBoard on first
startup.

.. automodule:: self_provisioning
   :members:
   :undoc-members: False