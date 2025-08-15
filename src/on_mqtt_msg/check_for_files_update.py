import json
from modules.logging import info, error
from typing import Any
import utils
from modules.file_writer import GatewayFileWriter
from modules.mqtt import GatewayMqttClient

from src.utils.misc import file_exists

content_encodings = ["base64", "text"]

def on_msg_check_for_files_update(msg_payload: Any) -> bool:
    files = utils.misc.get_maybe(msg_payload, "shared", "FILES")
    if not isinstance(files, list):
        return False

    info("Files hashes received!")
    try:
        for file_id in files:
            if not isinstance(files[file_id], dict):
                error("Invalid files update received")
                return False

            if not isinstance(files[file_id]["path"], str):
                error("Invalid files update received, missing 'path' property")
                return False

            if isinstance(files[file_id]["content_encoding"], str) and not content_encodings.__contains__(files[file_id]["content_encoding"]):
                error("Invalid files update received, unsupported 'content_encoding' property: " + files[file_id]["content_encoding"])
                return False

            if files[file_id]["create_if_not_exist"] and not isinstance(files[file_id]["create_if_not_exist"], bool):
                error("Invalid files update received, 'create_if_not_exist' property must be a boolean")
                return False

            if files[file_id]["restart_controller_on_change"] and not isinstance(files[file_id]["restart_controller_on_change"], bool):
                error("Invalid files update received, 'restart_controller_on_change' property must be a boolean")
                return False

        GatewayFileWriter().set_files(files)
        GatewayMqttClient().request_attributes({"clientKeys": f"FILE_CONTENT_HASHES"})

    except json.JSONDecodeError:
        error("Failed to parse files definition")
    except Exception as e:
        error(f"Failed to update files definition: {e}")

    return True