Controller Repository
=====================

The Controller Repository contains the device-side hardware interface managed by the gateway.
It is designed as a standalone, versioned component that is built and deployed independently.


Architecture Overview
---------------------

The controller repository:

- Is a dedicated Git repository (not part of the gateway).
- Has its own versioning and release cycle.
- Is fetched and built by the gateway via the OTA update mechanisms.
- Is executed inside an isolated Docker container.
- Communicates with the gateway exclusively via a local SQLite database.

The gateway is responsible for:

- Building the controller Docker image.
- Starting and supervising the container.
- Monitoring controller health.
- Restarting the container in case of failure.

The controller is responsible for:

- Implementing device-specific logic (sensors, actuators, control flows).
- Writing outbound MQTT messages to the local SQLite message queue (measurements, logs).
- Maintaining a periodic health check.

Repository Structure
--------------------

A minimal controller repository must contain:

- ``Dockerfile`` (in repository root)
- Controller source code
- SQLite communication implementation
- Dependency definition (e.g. ``requirements.txt``)

A typical structure:

::

    controller-repo/
    ├── Dockerfile
    ├── requirements.txt
    ├── main.py
    ├── db.py
    ├── config/
    └── modules/


The gateway automatically builds the Docker image from the root ``Dockerfile``.

Linking the Controller Repository
----------------------------------

The controller repository is linked to the gateway using the environment variable:

::

    TEG_CONTROLLER_GIT_PATH

This variable must point to the controller Git repository.

Setup details are described in: :doc:`Environment Variables </getting-started/setup>`

SQLite Communication Interface
------------------------------

The controller and gateway communicate via a shared SQLite database.

The controller must:

1. Enqueue outbound MQTT messages into the ``messages`` table.
2. Periodically update the ``health_check`` table.

Database schema definitions are documented in: :ref:`header-database-schemas` 

A reference implementation is available in:

``demo/example_controller/db.py``

Outbound Message Queue
^^^^^^^^^^^^^^^^^^^^^^^

Messages must be inserted into the ``messages`` table with:

- ``type`` (telemetry, attributes, rpc, etc.)
- ``message`` (JSON payload)

The gateway consumes and forwards these messages to ThingsBoard via MQTT.

Health Check Mechanism
^^^^^^^^^^^^^^^^^^^^^^^

The controller must periodically write a timestamp (milliseconds since epoch) to:

``health_check(id=1, timestamp_ms=<now>)``

The gateway monitors this timestamp to detect stalled or crashed controllers.

Failure Handling
----------------

Controllers must fail fast and exit the main process if an unrecoverable error occurs.

The gateway will automatically restart the container via a potential backoff. 

Controllers must not:

- Attempt self-restarts
- Implement their own process supervision
- Modify the database schema

Main Loop Requirements
----------------------

A typical controller main loop should:

1. Initialize configuration.
2. Connect to the SQLite database.
3. Initialize sensors/actuators.
4. Enter execution loop.
5. Perform periodic tasks.
6. Write health check in every iteration.

Example pattern:

::

    while True:
        read_sensors()
        process_logic()
        enqueue_messages()
        write_health_check()
        sleep(interval)


Optional Components
-------------------

Base Classes
^^^^^^^^^^^^

Reusable base classes for sensors and actuators are recommended to:

- Standardize device interfaces
- Reduce boilerplate
- Improve testability

Example implementations are provided in:

``demo/example_controller/sensor`` and ``demo/example_controller/actuator``

Remote Configuration
^^^^^^^^^^^^^^^^^^^^

Controllers can use the gateway Remote File Management to receive configuration files (e.g. ``config.json``).

Typical workflow:

- File is managed via ThingsBoard UI.
- Gateway syncs file to controller container.
- Controller reads configuration at startup.
- Configurable: Configuration changes trigger restart.

Example Controller
------------------

A minimal working controller is available at:

``demo/example_controller/``

It includes:

- SQLite communication module
- Example sensor and actuator base classes
- Minimal main loop
- Dockerfile
- Requirements file

You may use this as a starting template for new implementations.
