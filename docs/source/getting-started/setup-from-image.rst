Setup from Image
================

This section describes how to create an image after the system setup to flash it on multiple systems. This allows to avoid repeating the setup steps on each system. 

Follow installation and setup instructions for a single system first. Skip the provisioning step as this needs to be done for each system individually after flashing the image.

A image can be created from the prepared system and then flashed onto other systems. Then the new systems ca then be renamed and provisioned individually.

Link to installation.rst and setup.rst

Create Backup Image
-------------------

.. code-block:: bash
    diskutil list
    diskutil umountDisk /dev/disk[*]
    dd status=progress bs=4M  if=/dev/disk[*] | gzip > //Users/.../


Insert fresh SD Card into personal computer

Create Fresh System
-------------------

.. code-block:: bash
    diskutil list
    diskutil umountDisk /dev/disk[*]
    gzip -dc //Users/.../acropolis-edge-image.gz | sudo dd of=/dev/disk[*] bs=4M status=progress


Remove SD Card and insert into RaspberryPi.

Change Hostname:

.. code-block:: bash
    sudo raspi-config
    # Navigate to: System Options → Change Hostname
    sudo reboot


Provision Device
----------------

Follow the device provisioning instructions to register the new device with ThingsBoard. 
Link to quickstart.rst / Device Provisioning