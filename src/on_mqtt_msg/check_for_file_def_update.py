import base64
import json
from binascii import Error

from modules.logging import info, error
from typing import Any
import utils
from modules.file_writer import GatewayFileWriter
from modules.mqtt import GatewayMqttClient

FILE_DEFINITION_PREFIX = "FILE_DEF_"

def on_msg_check_for_file_definition_update(msg_payload: Any) -> bool:
    payload = utils.misc.get_maybe(msg_payload, "shared") or msg_payload
    file_id = None
    for key in payload:
        if key.startswith(FILE_DEFINITION_PREFIX):
            file_id = key.replace(FILE_DEFINITION_PREFIX, "")
            break
    if file_id is None:
        return False

    update_json = utils.misc.get_maybe(payload, FILE_DEFINITION_PREFIX + file_id)
    if not isinstance(update_json, dict):
        error("Invalid file definition received")
        return False

    file_path = utils.misc.get_maybe(update_json, "path")
    # check path property
    if not file_path:
        error("Invalid file hash update received, missing 'path' property")
        return False

    info("File definition received! Def ID: " + file_id)
    try:
        if isinstance(update_json["content"], str):
            if not isinstance(update_json["content_encoding"], str):
                error("Invalid file definition received, missing 'content_encoding' property")
                return False
            if update_json["content_encoding"] == "base64":
                try:
                    content = base64.b64decode(update_json["content"])
                except Error as e:
                    error(f"Failed to decode base64 content for file definition {file_id}: {e}")
                    return False
            return False

        error(" TODO: Implement file definition update logic")
        # TODO
    except json.JSONDecodeError:
        error("Failed to parse file definition")
    except Exception as e:
        error(f"Failed to update file definition: {e}")

    return True