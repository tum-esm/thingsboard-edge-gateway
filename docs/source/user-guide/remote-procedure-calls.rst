Remote Procedure Calls
======================

The Edge Gateway supports *Remote Procedure Calls (RPC)* via ThingsBoard's built-in RPC mechanism. RPCs allow external applications, automation scripts, or ThingsBoard dashboards to invoke predefined commands on the Edge Gateway controller and receive immediate feedback.

This mechanism is primarily intended for operational control, diagnostics, and maintenance tasks that must be executed on-demand without direct access to the device.


Overview
--------

ThingsBoard provides an RPC widget that acts as an interactive console within dashboards. Using this widget, users can send RPC requests to a specific Edge Gateway device and inspect the returned responses in real time.

RPCs are executed by the Edge Gateway controller and are restricted to a predefined set of supported commands to ensure safe and controlled operation.

For a general introduction to ThingsBoard RPCs, refer to the official documentation:
https://thingsboard.io/docs/user-guide/rpc/


.. image:: ../_static/images/rpc-widget.png
   :alt: ThingsBoard Dashboard RPC widget
   :width: 80%
   :align: center


Built-in RPC Command: ``list``
------------------------------

The Edge Gateway controller exposes a built-in RPC command named ``list``. This command returns a human-readable list of all RPC commands currently supported by the controller, including a short description of each command and its expected parameters.

This command is useful for quickly verifying controller capabilities and for debugging RPC availability after software updates.

Example response:

.. code-block:: json

    {
      "message": [
        "Available RPC methods:",
        "reboot: Reboot the device",
        "shutdown: Shutdown the device",
        "exit: Exits the gateway process (triggers gateway restart)",
        "ping: Ping the device (returns 'pong' reply)",
        "init_files: Initialize file-related client attributes (FILE_HASHES, FILE_READ_*)",
        "restart_controller: Restart the controller docker container",
        "run_command: Run arbitrary command ({command: list [str], timeout_s: int [default 30s]}) - use with caution!",
        "archive_republish_messages: Republish messages from archive ({start_timestamp_ms: int, end_timestamp_ms: int})",
        "archive_discard_messages: Discard messages from archive ({start_timestamp_ms: int, end_timestamp_ms: int})"
      ]
    }


Supported RPC Commands
----------------------

The following RPC commands are currently supported by the Edge Gateway controller. Command availability may depend on the deployed controller version.


``ping``
^^^^^^^^

Performs a simple connectivity check.

**Description**
  Returns a static ``pong`` response if the controller is reachable and responsive.

**Parameters**
  None

**Typical use cases**
  - Verify basic connectivity
  - Confirm controller responsiveness


``reboot``
^^^^^^^^^^

Reboots the Edge Gateway host system.

**Description**
  Performs a full system reboot of the device.

**Parameters**
  None

**Notes**
  - This command interrupts all running services.
  - Use with care on production systems.


``shutdown``
^^^^^^^^^^^^

Shuts down the Edge Gateway host system.

**Description**
  Powers off the device gracefully.

**Parameters**
  None

**Notes**
  - Physical access is required to restart the device afterward.


``exit``
^^^^^^^^

Terminates the Edge Gateway process.

**Description**
  Stops the gateway process, which triggers an automatic restart by Docker.

**Parameters**
  None

**Notes**
  - Performs a clean restart of the gateway process
  - Allows to apply gateway-level configuration or software changes.


``restart_controller``
^^^^^^^^^^^^^^^^^^^^^^

Restarts the Edge Gateway controller container.

**Description**
  Stops and restarts the controller Docker container without affecting the gateway runtime.

**Parameters**
  None

**Typical use cases**
  - Manually apply controller configuration changes
  - Recover from transient controller errors


``init_files``
^^^^^^^^^^^^^^

Initializes file-related client attributes required for remote file management.

**Description**
  Creates and initializes the client attributes required for the *Remote File Management* feature, most notably ``FILE_HASHES`` and all ``FILE_READ_<file_key>`` attributes.  
  This RPC allows the file management initialization process to be triggered manually. Under normal conditions, it is executed automatically after a successful device provisioning.

**Parameters**
  None

**Typical use cases**
  - Manually trigger file management initialization
  - Recover from incomplete or failed provisioning
  - Initialize file management on pre-configured or cloned devices


``run_command``
^^^^^^^^^^^^^^^

Executes an arbitrary command on the Edge Gateway host.

**Description**
  Executes a shell command on the device and returns the command output.

**Parameters**
  - ``command`` (list of strings, required): Command and arguments
  - ``timeout_s`` (integer, optional): Command timeout in seconds (default: 30)

**Notes**
  - This command is performed within the gateway runtime environment, not within the controller container.
  - The command is executed with the same permissions as the gateway process, which may have security implications.
  - Use with extreme caution, as it can lead to service interruptions or security risks if misused. 


``archive_republish_messages``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Republishes archived telemetry messages.

**Description**
  Republishes previously archived telemetry messages within a specified time range. This allows locally stored messages that were lost in transmission to be reprocessed and sent to ThingsBoard.

**Parameters**
  - ``start_timestamp_ms`` (integer): Start of the time range (Unix timestamp in milliseconds)
  - ``end_timestamp_ms`` (integer): End of the time range (Unix timestamp in milliseconds)


``archive_discard_messages``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Discards archived telemetry messages.

**Description**
  Permanently deletes archived telemetry messages within a specified time range. This allows to free up local storage space by removing messages that are no longer needed or have already been successfully transmitted to ThingsBoard.

**Parameters**
  - ``start_timestamp_ms`` (integer): Start of the time range (Unix timestamp in milliseconds)
  - ``end_timestamp_ms`` (integer): End of the time range (Unix timestamp in milliseconds)


Security Considerations
-----------------------

RPC commands provide powerful control over Edge Gateway devices. It is strongly recommended to:

- Restrict RPC access to trusted users and dashboards only
- Avoid exposing sensitive commands such as ``run_command`` to non-administrative users
- Use ThingsBoard role-based access control to limit operational impact

Improper use of RPC commands may lead to service interruptions or security risks.