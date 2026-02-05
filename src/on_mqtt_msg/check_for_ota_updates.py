"""Handle OTA software update notifications received via MQTT.

This module processes ThingsBoard OTA-related attribute updates (``sw_title``,
``sw_version`` and legacy ``sf_*`` keys) and triggers controller software updates
on the Edge Gateway when a new version is available.

It represents the *decision and orchestration* stage of the OTA workflow:
- Detect whether a software update is available.
- Compare the requested version against the currently running controller.
- Trigger a safe controller restart/update via the Docker client.
- Record the last successfully launched controller version.

Notes
-----
- The actual Docker image build and container lifecycle are handled by
  :class:`modules.docker_client.GatewayDockerClient`.
- OTA state reporting (``sw_state``) is published by the Docker client during the
  update lifecycle.
"""

import utils
from modules import docker_client as dockerc
from typing import Optional, Any

from modules.logging import info
from utils.misc import get_maybe


def on_msg_check_for_ota_update(msg_payload: Optional[Any]) -> bool:
    """Process an incoming OTA update notification.

    Args:
      msg_payload: MQTT message payload containing OTA-related attributes.

    Returns:
      ``True`` if the message was handled as an OTA update notification,
      ``False`` otherwise.
    """
    # Extract software title and version (supports legacy sf_* keys)
    sw_title = get_maybe(msg_payload, "sw_title") or get_maybe(msg_payload, "shared", "sw_title") or get_maybe(msg_payload, "sf_title") or get_maybe(msg_payload, "shared", "sf_title")
    sw_version = get_maybe(msg_payload, "sw_version") or get_maybe(msg_payload, "shared", "sw_version") or get_maybe(msg_payload, "sf_version") or get_maybe(msg_payload, "shared", "sf_version")
    if sw_version is None:
        return False

    docker_client = dockerc.GatewayDockerClient()
    # Compare requested version against the currently running controller
    if docker_client.is_controller_running():
        current_version = docker_client.get_controller_version()
        if current_version is None or current_version != sw_version:
            info("Software update available: " + (sw_title or "?") + " from " + (
                        current_version or "UNKNOWN") + " to " + sw_version)
            # Trigger controller update or launch via Docker client
            docker_client.start_controller_safely(sw_version)
        else:
            info("Software is up to date (version '" + current_version + "')")
            docker_client.set_last_launched_controller_version(current_version)
    else:
        info("Launching latest edge-software: " + sw_version + " (" + (sw_title or "?") + ")")
        # Trigger controller update or launch via Docker client
        docker_client.start_controller_safely(sw_version)
    return True