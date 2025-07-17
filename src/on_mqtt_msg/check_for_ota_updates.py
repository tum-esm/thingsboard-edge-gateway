import utils
from modules import docker_client as dockerc
from typing import Optional, Any

from modules.logging import info


def on_msg_check_for_ota_update(msg_payload: Optional[Any]) -> bool:
    sw_title = utils.misc.get_maybe(msg_payload, "sw_title") or utils.misc.get_maybe(msg_payload, "shared", "sw_title")
    sw_url = utils.misc.get_maybe(msg_payload, "sw_url") or utils.misc.get_maybe(msg_payload, "shared", "sw_url")
    sw_version = utils.misc.get_maybe(msg_payload, "sw_version") or utils.misc.get_maybe(msg_payload, "shared", "sw_version")
    if sw_title is None or sw_url is None or sw_version is None:
        return False

    docker_client = dockerc.GatewayDockerClient()
    if docker_client.is_edge_running():
        current_version = docker_client.get_edge_version()
        if current_version is None or current_version != sw_version:
            info("Software update available: " + sw_title + " from " + (
                        current_version or "UNKNOWN") + " to " + sw_version)
            docker_client.start_controller(sw_version)
        else:
            info("Software is up to date (version '" + current_version + "')")
            docker_client.last_launched_version = current_version
    else:
        info("Launching latest edge-software: " + sw_version + " (" + sw_title + ")")
        docker_client.start_controller(sw_version)
    return True