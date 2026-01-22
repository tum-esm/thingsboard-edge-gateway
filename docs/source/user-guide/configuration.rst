Configuration
=============

Shared Attributes
-----------------

Initialize FILES attribute

- Update FILES entry in Device Attributes: Shared attributes
- Link to API documentation for encoding and other parameters in this context

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

Example: Controller Configuration File

- Create new entry "FILE_CONTENT_controller_config" (Type: JSON) in Device Attributes: Shared attributes 
- Populate the entry with json encoded content of the file

.. code-block:: json

    {
        "setting1": "value1",
        "setting2": "value2"
    }



Example: System Crontab File

- Create new entry "FILE_CONTENT_crontab" (Type: String) in Device Attributes: Shared attributes: 
- Populate the entry with base64 encoded content of the file

.. code-block:: text

    U0hFTEw9L2Jpbi9iYXNoClBBVEg9L3Vzci9sb2NhbC9zYmluOi91c3IvbG9jYWwvYmluOi91c3Ivc2JpbjovdXNyL2Jpbjovc2JpbjovYmluCkhPTUU9L3Jvb3QKCiMgRG9ja2VyCkBkYWlseSBkb2NrZXIgc3lzdGVtIHBydW5lIC1hIC0tZm9yY2UgLS1maWx0ZXIgInVudGlsPTg3NjBoIgoKIyBEZWxldGUgb2xkIGxvZyBmaWxlcyAob2xkZXIgdGhhbiAxMDAgZGF5cykKQGRhaWx5IC91c3IvYmluL2ZpbmQgL2hvbWUvcGkvY29udHJvbGxlci9sb2dzLyAtdHlwZSBmIC1tdGltZSArMTAwIC1kZWxldGUK