Getting Started
===============

This section describes how to install and set up both the thingsboard server software (part of the open source `Thingsboard project <https://thingsboard.io/>`_) and the thingsboard-edge-gateway client software (this project).

::hint
System Requirements
-------------------
The documentation has been tested using the `Ubuntu OS <https://ubuntu.com/>`_ on a rented virtual private server (for thingsboard) as well as using the `Raspberry Pi OS <https://www.raspberrypi.com/software/>`_ on a Raspberry Pi device (for the edge gatway).

However, both thingsboard and the edge gateway software can be installed on any Linux based system that supports Docker. Notes specific to setting up the edge gateway on a Raspberry Pi are included.

Minimum system requirements are:


+------------------------+------------------------+------------------------+
| Component              | Thingsboard Server     | Edge Gateway          |
+========================+========================+========================+
| RAM                    | 2GB           | 512MB         |
+------------------------+------------------------+------------------------+
| vCPU/Processor        | 2 cores        | 1 core        |
+------------------------+------------------------+------------------------+
| Disk Space            | 10GB           | 4GB            |
+------------------------+------------------------+------------------------+



.. toctree::
    :caption: Contents:
    :maxdepth: 1

    1_demo
    2_installation
    3_setup
    4_quickstart
    5_setup-from-image
