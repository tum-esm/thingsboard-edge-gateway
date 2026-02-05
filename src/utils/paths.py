"""Filesystem path configuration for the Edge Gateway.

This module centralizes all filesystem paths used by the Edge Gateway and the
controller runtime. Paths are resolved at import time based on environment
variables, with sensible defaults derived from the project directory.

The primary purpose of this module is to provide a single, consistent source of
truth for:
- Gateway and controller data directories
- Controller Git repository and Docker build context paths
- SQLite database locations used for buffering and archiving
- Log storage paths

Environment variables
---------------------
The following environment variables can be used to override default paths:

- ``TEG_DATA_PATH``: Base data directory for the Edge Gateway.
- ``TEG_CONTROLLER_DATA_PATH``: Base data directory for the controller.
- ``TEG_CONTROLLER_LOGS_PATH``: Directory for controller log files.
- ``TEG_CONTROLLER_GIT_PATH``: Path to the controller Git repository.
- ``TEG_CONTROLLER_DOCKERCONTEXT_PATH``: Docker build context for the controller.
- ``TEG_CONTROLLER_DOCKERFILE_PATH``: Path to the controller Dockerfile.

Notes
-----
- Path resolution is performed eagerly at import time.
- Missing critical configuration (e.g. controller Git path) is treated as a fatal
  configuration error and logged immediately.
"""
from os import path, environ
from os.path import dirname, join

from modules.logging import error, debug

# Project and base data paths
PROJECT_DIR: str = dirname(dirname(dirname(path.abspath(__file__)))) # path to "gateway" folder
GATEWAY_DATA_PATH: str = str(environ.get("TEG_DATA_PATH") or PROJECT_DIR)
CONTROLLER_DATA_PATH: str = str(environ.get("TEG_CONTROLLER_DATA_PATH") or GATEWAY_DATA_PATH)

# Controller-related paths
CONTROLLER_LOGS_PATH: str = str(environ.get("TEG_CONTROLLER_LOGS_PATH") or join(CONTROLLER_DATA_PATH, "logs"))
CONTROLLER_GIT_PATH: str = str(environ.get("TEG_CONTROLLER_GIT_PATH") or "UNKNOWN")
CONTROLLER_DOCKERCONTEXT_PATH: str = str(environ.get("TEG_CONTROLLER_DOCKERCONTEXT_PATH") or join(dirname(CONTROLLER_GIT_PATH), "docker"))
CONTROLLER_DOCKERFILE_PATH: str = str(environ.get("TEG_CONTROLLER_DOCKERFILE_PATH") or "./Dockerfile")

# Gateway database paths
GATEWAY_LOGS_BUFFER_DB_NAME: str = "gateway_logs_buffer.db"
GATEWAY_LOGS_BUFFER_DB_PATH: str = join(str(GATEWAY_DATA_PATH), GATEWAY_LOGS_BUFFER_DB_NAME)

GATEWAY_ARCHIVE_DB_NAME: str = "gateway_archive.db"
GATEWAY_ARCHIVE_DB_PATH: str = join(str(GATEWAY_DATA_PATH), GATEWAY_ARCHIVE_DB_NAME)

# Controller communication queue database
COMMUNICATION_QUEUE_DB_NAME: str = "communication_queue.db"
COMMUNICATION_QUEUE_DB_PATH: str = join(str(CONTROLLER_DATA_PATH), COMMUNICATION_QUEUE_DB_NAME)

if CONTROLLER_GIT_PATH == "UNKNOWN":
    error("[FATAL_ERROR] Env var TEG_CONTROLLER_GIT_PATH not set!")

debug(f'PROJECT_DIR: {PROJECT_DIR}')
debug(f'GATEWAY_DATA_PATH: {GATEWAY_DATA_PATH}')
debug(f'CONTROLLER_LOGS_PATH: {CONTROLLER_LOGS_PATH}')
debug(f'CONTROLLER_GIT_PATH: {CONTROLLER_GIT_PATH}')

debug(f'GATEWAY_LOGS_BUFFER_DB_PATH: {GATEWAY_LOGS_BUFFER_DB_PATH}')
debug(f'GATEWAY_ARCHIVE_DB_PATH: {GATEWAY_ARCHIVE_DB_PATH}')
debug(f'COMMUNICATION_QUEUE_DB_PATH: {COMMUNICATION_QUEUE_DB_PATH}')