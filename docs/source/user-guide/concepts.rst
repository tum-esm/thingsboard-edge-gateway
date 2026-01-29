Concepts
========

System Architecture
-------------------


Shared Attributes
-----------------

Shared Attributeds are used to remotely push file content to the Edge Gateway. To manage file locations and encoding, the FILES attribute is used. It needs to be initially created and populated with file metadata. After that, file content can be pushed using separate attributes. 

(1) Initialize FILES attribute

The FILES attribute is a JSON object that contains metadata for each file to be managed. It includes the file path, encoding type, and optional parameters like write version, restart_controller_on_change.

.. code-block:: json
    
    {
        "crontab": {
            "path": "/var/spool/cron/crontabs/root",
            "encoding": "base64",
            "write_version": 1
        },
        "controller_config": {
            "path": "$DATA_PATH/config.json",
            "encoding": "json",
            "write_version": 1,
            "restart_controller_on_change": true
        },
    }


The path parameter defines the target location on the Edge Gateway filesystem. It can be a relative or absolute path. Locally defined environment variables can be used in the path, e.g. $DATA_PATH. 
The encoding parameter defines how the file content will be encoded when pushed. Encoding it into base64 enables to include lines breaks or special characters. 
Write version is an optional parameter that can be used to manage file updates while the system is not connected. This ensures that the latest version is applied once the connection is restored.
The restart_controller_on_change is an optional boolean parameter that indicates whether the Edge Gateway controller should be restarted after the file is updated.

- Link to API documentation for encoding and other parameters in this context

(2) Define file content attributes


Example: Controller Configuration File

- Allows to remotely create or update new files for the controller to use
- Create new entry "FILE_CONTENT_controller_config" (Type: JSON) in Device Attributes: Shared attributes 
- Populate the entry with json encoded content of the file

.. code-block:: json

    {
        "setting1": "value1",
        "setting2": "value2"
    }


Example: System Crontab File

- Allows to remotely create or update the RaspbianOS system files like crontab
- Create new entry "FILE_CONTENT_crontab" (Type: String) in Device Attributes: Shared attributes: 
- Populate the entry with base64 encoded content of the file

.. code-block:: text

    U0hFTEw9L2Jpbi9iYXNoClBBVEg9L3Vzci9sb2NhbC9zYmluOi91c3IvbG9jYWwvYmluOi91c3Ivc2JpbjovdXNyL2Jpbjovc2JpbjovYmluCkhPTUU9L3Jvb3QKCiMgRG9ja2VyCkBkYWlseSBkb2NrZXIgc3lzdGVtIHBydW5lIC1hIC0tZm9yY2UgLS1maWx0ZXIgInVudGlsPTg3NjBoIgoKIyBEZWxldGUgb2xkIGxvZyBmaWxlcyAob2xkZXIgdGhhbiAxMDAgZGF5cykKQGRhaWx5IC91c3IvYmluL2ZpbmQgL2hvbWUvcGkvY29udHJvbGxlci9sb2dzLyAtdHlwZSBmIC1tdGltZSArMTAwIC1kZWxldGUK
