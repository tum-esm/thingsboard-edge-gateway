Concepts
========

System Architecture
-------------------


Shared Attributes
-----------------

Shared Attributes are used to remotely push file content to the Edge Gateway. To manage file locations and encoding, the FILES attribute is used. It needs to be initially created and populated with file metadata. After that, file content can be pushed using separate attributes. 

(1) Initialize FILES attribute

The FILES attribute is a JSON object that contains metadata for each file to be managed. It includes the file path, encoding type (text/json/base64), and optional parameters like write version, restart_controller_on_change.

Example: Managing Controller Configuration and the OS Crontab File

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

When a new entry is created in the FILES attribute and a matching FILE_CONTENT_<file_key> attribute is found, the Edge Gateway will create or update the specified file accordingly. A client attribute FILE_READ_<file_key> will be created to report the updated file content back to the ThingsBoard server.
When no FILE_CONTENT_<file_key> attribute is found, the file will be handled as read-only and it's content is just mirrored back to the ThingsBoard server using client attributes.

(2) Populate FILE_CONTENT_<file_key> attributes

Use Case: Create a controller configuration file

Sometimes it is beneficial to create or update configuration files for the edge controller a new entry "FILE_CONTENT_controller_config" is created. The content file is then populated with JSON encoded configuration data. A new client attribute "FILE_READ_controller_config" will be created to report the current content of the configuration file.

.. code-block:: json

    {
        "setting1": "value1",
        "setting2": "value2"
    }


Use Case: Create a system crontab file

Update OS files to change the system behavior of the locally deployed Raspberry Pi. A new entry "FILE_CONTENT_crontab" is created to add new system behavior after reboots. The content is base64 encoded to allow line breaks and special characters.

.. code-block:: text

    U0hFTEw9L2Jpbi9iYXNoClBBVEg9L3Vzci9sb2NhbC9zYmluOi91c3IvbG9jYWwvYmluOi91c3Ivc2JpbjovdXNyL2Jpbjovc2JpbjovYmluCkhPTUU9L3Jvb3QKCiMgRG9ja2VyCkBkYWlseSBkb2NrZXIgc3lzdGVtIHBydW5lIC1hIC0tZm9yY2UgLS1maWx0ZXIgInVudGlsPTg3NjBoIgoKIyBEZWxldGUgb2xkIGxvZyBmaWxlcyAob2xkZXIgdGhhbiAxMDAgZGF5cykKQGRhaWx5IC91c3IvYmluL2ZpbmQgL2hvbWUvcGkvY29udHJvbGxlci9sb2dzLyAtdHlwZSBmIC1tdGltZSArMTAwIC1kZWxldGUK


Client attributes
-----------------

Client attributes are used to report the status of file operations back to the ThingsBoard server. For each file defined in the FILES attribute, a corresponding client attribute named FILE_READ_<file_key> is created. This attribute contains a mirror for the latest local file content. After the creation of new files or updating existing ones, the Edge Gateway calculates a hash and updates the client atteibute *FILE_HASES*. 

File hases and synchronization
------------------------------

The *FILE_HASHES* attribute is used to keep all remotely managed files in sync. The edge gateway regularily calculates the hash of each local file defined in the FILES attribute and compares it with the hash values stored in the FILE_HASES attribute. Whenever a mismatch is detected, it triggers an update by requesting the latest content from the corresponding FILE_CONTENT_<file_key> attribute. When the shared attribute is not found or empty, no action is taken.

Example: FILE_HASES attribute

.. code-block:: json

    {
        "crontab":{"hash":"5eaad668b8e694ec58f0873830110d5f","write_version":2},
        "controller_config":{"hash":"9368caefc2b90f334671fb96e41ecbe1","write_version":3}
    }


