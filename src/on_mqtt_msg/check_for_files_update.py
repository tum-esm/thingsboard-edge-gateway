import json
from modules.logging import info, error
from typing import Any
import utils
from modules.file_writer import GatewayFileWriter
from modules.mqtt import GatewayMqttClient


def on_msg_check_for_files_update(msg_payload: Any) -> bool:
    files = utils.misc.get_maybe(msg_payload, "shared", "files")
    if not isinstance(files, list):
        return False

    info("Files hashes received!")
    try:
        for file_id in files:
            if not isinstance(file_id, str):
                error("Invalid files update received")
                return False

            GatewayMqttClient().request_attributes({"sharedKeys": f"FILE_DEF_{file_id}"})

    except json.JSONDecodeError:
        error("Failed to parse files definition")
    except Exception as e:
        error(f"Failed to update files definition: {e}")

    return True