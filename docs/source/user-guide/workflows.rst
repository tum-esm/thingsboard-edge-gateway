Workflows
=========

Device Provisioning
-------------------

Remote Software Update
-----------------------

- Create new version in GitHub controller repository
- Create OTA update entry in ThingsBoard
- Asign OTA update to device(s)

Remote File Creation
--------------------

- Update FILES entry in Device Attributes: Shared attributes

.. code-block:: json

    {
        "controller_config": {
            "path": "$DATA_PATH/config.json",
            "encoding": "json",
            "write_version": 1,
            "restart_controller_on_change": true
        },
    }

- Create new entry "FILE_CONTENT_controller_config" in Device Attributes: Shared attributes 
- Populate the entry with json encoded content of the file

Remote File Update
-------------------

- Update Device Attributes: Shared attributes entry
- Update Write Version

Example: Confuguration File