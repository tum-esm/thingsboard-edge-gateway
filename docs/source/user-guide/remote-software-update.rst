Remote Software Update
======================

The remote software update feature allows you to push a new version of the Edge Gateway controller software to the device using ThingsBoard's OTA update mechanism. This is particularly useful for deploying bug fixes, performance improvements, or new features without requiring physical access to the device.

OTA Update Packages reference version tags or commit hases from the controller's GitHub repository. When a new OTA package is created and associated with the relevant device or device profile, the Edge Gateway devices will receive these updates, download the new code and deploy them locally using docker. 

The big strength of the split between the Edge Gateway and the controller is that the Edge Gateway can stays unaffected by software updates to the controller. This means that even if there are issues with the new controller version, the Edge Gateway can continue to operate and report data back to ThingsBoard, allowing you to monitor the situation and roll back to a previous version if needed.

Create a OTA Update Package
---------------------------

- Go to Advanced features/OTA Updates in the ThingsBoard Web UI
- Create new entry
- Fill Title to identify version 
- Version matching the Github version tag or commit hash of the controller release (e.g. v1.0.0)
- Chose Device profiles matching the edge gateway devices
- Package Type: Software
- Use external URL: fill "-"

.. image:: ../_static/images/new_ota_package.png
   :alt: OTA package creation workflow
   :width: 80%
   :align: center


Update Device Software Version
------------------------------

- Go to Entities/Devices in the ThingsBoard Web UI
- Select the target device
- Go to first tab "Details" and click "Edit"
- Selected "Assigned Software" and chose the OTA package created in the previous step from the dropdown list
- Click "OK" to apply the changes

.. image:: ../_static/images/update_device_software_version.png
   :alt: Update device software version workflow
   :width: 80%
   :align: center

After applying the update, the Edge Gateway will automatically stop the current controller, download the new software version, deploy it locally using docker and restart the `Edge Controller` to run the new version. The device will report its current status  back to ThingsBoard utilizing the update states available through ThingsBoard's OTA update mechanism. You can monitor the update progress and status in the ThingsBoard Update Dashboard using the ``sw_state``attribute.

For more details see the official ThingsBoard documentation on OTA updates: https://thingsboard.io/docs/user-guide/ota-updates/

Updating to previous versions
-----------------------------

The remote software update mechanism also allows you to roll back to a previous version of the controller software if needed. To do this, select the OTA package referencing the desired previous version tag or commit hash and assign it to the device as described in the steps above. The Edge Gateway will then the previously created docker image of the selected version and restart the controller to run that version.

In case the docker image of the selected version is not available locally, the Edge Gateway will attempt to download the software from GitHub and create a new docker image. This allows you to easily switch between different versions of the controller software as needed and reroll back to a previous version if any issues arise with the latest release.

