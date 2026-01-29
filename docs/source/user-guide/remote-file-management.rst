Remote File Management
======================

The Edge Gateway supports remote file management via ThingsBoard shared attributes. This mechanism allows configuration and system files on the gateway to be created, updated, monitored, and synchronized in a controlled and traceable way. The approach is designed to be robust against intermittent connectivity and to support both read-only mirroring and active configuration management.


Shared Attributes
-----------------

Shared attributes are used to push file metadata and file content from ThingsBoard to the Edge Gateway. The central element is the ``FILES`` attribute, which defines which files are managed and how they should be handled. Actual file content is transferred separately using dedicated attributes.


Initialize the ``FILES`` Attribute
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``FILES`` attribute is a JSON object containing metadata entries for each managed file. Each entry defines the target path on the Edge Gateway, the encoding used for file transfer, and optional behavior flags.

Supported metadata fields:

- ``path``  
  Target location on the Edge Gateway filesystem. Can be absolute or relative. Locally defined environment variables such as ``$DATA_PATH`` are expanded at runtime.

- ``encoding``  
  Encoding used when transferring file content. Supported values are ``text``, ``json``, and ``base64``. Base64 is recommended for files containing line breaks or special characters.

- ``write_version`` (optional)  
  Monotonically increasing version number used to ensure that the latest file version is applied after temporary disconnections.

- ``restart_controller_on_change`` (optional)  
  Boolean flag indicating whether the Edge Gateway controller should be restarted after a successful file update.

Example: Managing a controller configuration file and the system crontab

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
        }
    }

When a new entry is added to the ``FILES`` attribute, the Edge Gateway evaluates whether a corresponding ``FILE_CONTENT_<file_key>`` attribute exists.

- If file content is available, the file is created or updated accordingly.
- If no file content attribute exists, the file is treated as read-only and its current content is mirrored back to ThingsBoard.

In both cases, the Edge Gateway creates a client attribute named ``FILE_READ_<file_key>`` containing the latest local file content.


Populate ``FILE_CONTENT_<file_key>`` Attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

File content is pushed using a dedicated shared attribute named ``FILE_CONTENT_<file_key>``. The encoding must match the encoding defined in the corresponding ``FILES`` entry.

Use case: Create or update a controller configuration file
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

To manage the controller configuration, a shared attribute ``FILE_CONTENT_controller_config`` is created and populated with JSON-encoded configuration data.

.. code-block:: json

    {
        "setting1": "value1",
        "setting2": "value2"
    }

After applying the update, the Edge Gateway mirrors the current file content into the client attribute ``FILE_READ_controller_config``.


Use case: Update the system crontab
"""""""""""""""""""""""""""""""""""

System-level files such as the OS crontab can be managed in the same way. In this case, content is base64-encoded to preserve formatting and special characters.

.. code-block:: text

    U0hFTEw9L2Jpbi9iYXNoClBBVEg9L3Vzci9sb2NhbC9zYmluOi91c3IvbG9jYWwvYmluOi91c3Ivc2JpbjovdXNyL2Jpbjovc2JpbjovYmluCkhPTUU9L3Jvb3QKCiMgRG9ja2VyCkBkYWlseSBkb2NrZXIgc3lzdGVtIHBydW5lIC1hIC0tZm9yY2UgLS1maWx0ZXIgInVudGlsPTg3NjBoIgoKIyBEZWxldGUgb2xkIGxvZyBmaWxlcyAob2xkZXIgdGhhbiAxMDAgZGF5cykKQGRhaWx5IC91c3IvYmluL2ZpbmQgL2hvbWUvcGkvY29udHJvbGxlci9sb2dzLyAtdHlwZSBmIC1tdGltZSArMTAwIC1kZWxldGUK


Client Attributes
-----------------

Client attributes are used to report file state and synchronization status back to ThingsBoard.

For each file defined in the ``FILES`` attribute:

- A client attribute ``FILE_READ_<file_key>`` mirrors the latest local file content.
- A global client attribute ``FILE_HASHES`` is updated after file creation or modification.


File Hashes and Synchronization
-------------------------------

The ``FILE_HASHES`` attribute is used to ensure consistency between ThingsBoard and the Edge Gateway.

The Edge Gateway periodically computes a hash for each managed local file and compares it against the corresponding entry in ``FILE_HASHES``. Each entry includes both the hash and the associated ``write_version``.

If a mismatch is detected:

- The Edge Gateway requests the latest content from ``FILE_CONTENT_<file_key>``.
- If the shared attribute is missing or empty, no action is taken.

Example: ``FILE_HASHES`` client attribute

.. code-block:: json

    {
        "crontab": {
            "hash": "5eaad668b8e694ec58f0873830110d5f",
            "write_version": 2
        },
        "controller_config": {
            "hash": "9368caefc2b90f334671fb96e41ecbe1",
            "write_version": 3
        }
    }
