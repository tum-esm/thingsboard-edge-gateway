"""Controller restart watchdog for the Edge Gateway.

This module implements a lightweight watchdog that ensures the controller Docker
container is running. If the controller is not running, it attempts to restart it
using the last successfully launched controller version.

To avoid rapid restart loops, restarts are rate-limited and use an exponential
backoff strategy. If no previous version is known, the watchdog requests OTA
version information from ThingsBoard and reports a FAILED software state.

Notes
-----
- Controller lifecycle operations are executed via :class:`modules.docker_client.GatewayDockerClient`.
- OTA software state reporting is published via :class:`modules.mqtt.GatewayMqttClient`.
"""

from time import time_ns, sleep
from typing import Optional

from modules.docker_client import GatewayDockerClient
from modules.logging import info, error
from modules.mqtt import GatewayMqttClient

DEFAULT_CONTAINER_RESTART_DELAY_MS: int = 600_000
CONTAINER_RESTART_EXPONENTIAL_BACKOFF_FACTOR: float = 1.6
container_restart_delay_ms: float = DEFAULT_CONTAINER_RESTART_DELAY_MS
last_container_restart_ts: int = 0

def restart_controller_if_needed() -> bool:
    """Restart the controller container if it is not running.

    The watchdog checks whether the controller container is running. If it is not,
    it waits briefly and attempts to restart it using the last launched version.
    Restart attempts are rate-limited and use exponential backoff to avoid repeated
    rapid restarts.

    Returns:
      ``True`` if the watchdog performed an action that should delay or influence
      the main loop (restart attempt, OTA request), otherwise ``False``.
    """
    global container_restart_delay_ms, last_container_restart_ts

    if int(time_ns() / 1_000_000) - last_container_restart_ts > container_restart_delay_ms:
        last_container_restart_ts = int(time_ns() / 1_000_000)
        docker_client = GatewayDockerClient()
        if not docker_client.is_controller_running():
            container_restart_delay_ms *= CONTAINER_RESTART_EXPONENTIAL_BACKOFF_FACTOR
            info("Controller is not running, starting new container in 10s...")
            info("New controller restart exponential backoff: " + str(int(container_restart_delay_ms/1000.0)) + "s")
            sleep(10)
            last_launched_version = docker_client.get_last_launched_controller_version()
            if last_launched_version is not None:
                docker_client.start_controller_safely(last_launched_version)
                return True
            else:
                error("Failed to determine last launched controller version, unable to start new container...")
                GatewayMqttClient().request_attributes({"sharedKeys": "sw_title,sw_url,sw_version"})
                GatewayMqttClient().publish_sw_state("UNKNOWN", "FAILED",
                                                     "No previous version known to launch from, requested version info from ThingsBoard")
                error("Requested controller version from Thingsboard. Delaying main loop by 20s...")
                sleep(20)  # it is unlikely that the version to build will be available immediately
                return True
        elif container_restart_delay_ms > DEFAULT_CONTAINER_RESTART_DELAY_MS:
            info("New controller restart exponential backoff: " + str(int(container_restart_delay_ms / 1000.0)) + "s")
            container_restart_delay_ms = max(
                DEFAULT_CONTAINER_RESTART_DELAY_MS,
                int(container_restart_delay_ms / CONTAINER_RESTART_EXPONENTIAL_BACKOFF_FACTOR)
            )

    return False