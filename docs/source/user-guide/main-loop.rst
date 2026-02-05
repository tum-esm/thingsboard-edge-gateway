Main Loop
=========

This page explains how the ThingsBoard Edge Gateway operates once it is running,
from startup through normal operation and shutdown.

Overview
--------

After startup, the Edge Gateway runs continuously and coordinates all interaction
between the local controller, ThingsBoard, and local persistence components.

The main loop is responsible for:

- Maintaining a persistent connection to ThingsBoard
- Forwarding telemetry, logs, and status information
- Receiving and dispatching remote commands
- Supervising the controller process
- Ensuring local data durability during network interruptions

The loop is designed to run continuously and autonomously without user
interaction.

Startup Phase
-------------

Before entering the steady-state main loop, the Edge Gateway performs a short
initialization phase:

- Command-line arguments are parsed
- Device identity and credentials are verified or provisioned
- Local databases used for buffering and archiving are opened
- The connection to ThingsBoard is established

Once initialization completes successfully, the gateway transitions into normal
operation.

Steady-State Operation
----------------------

During normal operation, the main loop continuously performs the following tasks:

- Publishes telemetry and log messages received from the controller
- Receives shared attribute updates and RPC commands from ThingsBoard
- Triggers remote file synchronization and OTA updates when requested
- Monitors the health of the controller process
- Flushes buffered data when connectivity is available

All of these activities are coordinated within the main loop to ensure predictable
and deterministic behavior.

Failure Handling and Resilience
-------------------------------

The main loop is designed to be resilient to common failure scenarios:

- Temporary network outages
- Controller restarts or crashes
- Short-lived local I/O errors

If connectivity to ThingsBoard is lost, telemetry and log messages are buffered
locally and transmitted once the connection is restored.

If the controller becomes unresponsive or exits unexpectedly, the gateway
supervises its restart without terminating the main loop itself.

Shutdown Behavior
-----------------

The Edge Gateway responds gracefully to shutdown signals:

- Active connections are closed cleanly
- Local databases are flushed and closed
- The controller is stopped if running

A forced shutdown is only triggered if graceful termination fails within a defined
timeout.

What the Main Loop Does *Not* Do
--------------------------------

For clarity, the main loop intentionally does **not**:

- Reboot the host system
- Modify managed files autonomously
- Execute arbitrary commands without explicit RPC requests
- Update its own runtime software via OTA

These actions are either explicitly triggered by remote commands or handled by
other subsystems.

Operational Notes
-----------------

- The main loop runs continuously as long as the Edge Gateway process is active.
- Most user-facing features (RPCs, file management, OTA updates) are coordinated
  through this loop.
- In normal operation, no manual intervention is required once the gateway has
  started successfully.