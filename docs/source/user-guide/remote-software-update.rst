Remote Software Update
======================

The *Remote Software Update* feature allows you to deploy new versions of the Edge Gateway controller software to devices using ThingsBoard's OTA update mechanism. This enables the rollout of bug fixes, performance improvements, and new features without requiring physical access to deployed hardware.

OTA update packages reference version tags or commit hashes from the controller's GitHub repository. Once an OTA package is created and assigned to a device or device profile, Edge Gateway devices automatically receive the update, download the corresponding source code, build a Docker image locally if required, and deploy the new controller version.


Architecture Rationale
----------------------

A key design principle of the Edge Gateway is the strict separation between the gateway runtime and the controller software. This separation ensures that software updates to the controller do not affect the core Edge Gateway functionality.

Even if a newly deployed controller version contains errors or fails to start correctly, the Edge Gateway itself remains operational. It continues to report device status and update progress to ThingsBoard, allowing operators to monitor deployments and safely roll back to a previous, stable controller version when necessary.


Create an OTA Update Package
----------------------------

To deploy a new controller version, an OTA update package must first be created in the ThingsBoard Web UI.

1. Navigate to **Advanced features → OTA Updates**.
2. Create a new OTA update entry.
3. Set the **Title** to identify the controller version.
4. Set **Version** to match the GitHub version tag or commit hash of the controller release (for example ``v1.0.0``).
5. Select the **Device Profiles** corresponding to the Edge Gateway devices.
6. Set **Package type** to *Software*.
7. Enable **Use external URL** and leave the URL field empty (``-``).

.. image:: ../_static/images/new_ota_package.png
   :alt: OTA package creation workflow
   :width: 80%
   :align: center


Assign the OTA Package to a Device
----------------------------------

After creating the OTA package, it must be assigned to the target device.

1. Navigate to **Entities → Devices**.
2. Select the target Edge Gateway device.
3. Open the **Details** tab and click **Edit**.
4. Under **Assigned Software**, select the previously created OTA package from the dropdown list.
5. Click **OK** to apply the changes.

.. image:: ../_static/images/update_device_software_version.png
   :alt: Update device software version workflow
   :width: 80%
   :align: center


Update Execution and Monitoring
-------------------------------

Once the OTA package is assigned, the Edge Gateway performs the update automatically:

- The currently running controller is stopped.
- The new controller version is downloaded.
- A Docker image is created locally if it does not already exist.
- The controller is restarted using the new version.

Throughout the process, the Edge Gateway reports its update state back to ThingsBoard using the standard OTA update attributes. The update progress and final status can be monitored via the ThingsBoard Update Dashboard using the ``sw_state`` attribute.

For additional details on OTA update states and workflows, refer to the official ThingsBoard documentation:
https://thingsboard.io/docs/user-guide/ota-updates/


Rolling Back to Previous Versions
---------------------------------

The remote software update mechanism also supports rolling back to earlier controller versions.

To perform a rollback, assign an OTA package that references the desired previous version tag or commit hash to the device. The Edge Gateway will stop the currently running controller and restart it using the selected version.

If a Docker image for the requested version is already available locally, it is reused. Otherwise, the Edge Gateway automatically downloads the corresponding source code from GitHub and builds a new Docker image.

This approach enables rapid switching between controller versions and provides a reliable recovery path in case issues arise with newly deployed releases.
