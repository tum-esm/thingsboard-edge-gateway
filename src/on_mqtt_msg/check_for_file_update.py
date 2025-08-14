import json
from modules.logging import info, error
from typing import Any
import utils
from modules.file_writer import GatewayFileWriter
from modules.mqtt import GatewayMqttClient


def on_msg_check_for_file_hashes_update(msg_payload: Any) -> bool:
    payload = utils.misc.get_maybe(msg_payload, "shared") or msg_payload
    file_def_id = None
    for key in payload:
        if key.startswith("FILE_"):
            file_def_id = key.replace("FILE_", "")
            break
    if file_def_id is None:
        return False

    file_def = utils.misc.get_maybe(payload, "FILE_" + file_def_id)

    if file_def is None or not isinstance(file_def, dict):
        error("Invalid file definition received")
        return False

    # check path property
    if "path" not in file_def or not isinstance(file_def["path"], str):
        error("Invalid file definition received, missing 'path' property")
        return False


    info("File definition received! Def ID: " + file_def_id)
    try:
        for file_id in files_hashes:
            if not isinstance(file_id, str) or not isinstance(files_hashes[file_id], dict):
                error("Invalid file hash format received")
                return False
            if not isinstance(files_hashes[file_id]["hash"], str):
                error("Invalid file hash format received")
                return False
            if not isinstance(files_hashes[file_id]["path"], str):
                error("Invalid file hash format received")
                return False

            current_hash = GatewayFileWriter().get_file_hash(files_hashes[file_id]["path"])
            if current_hash != files_hashes[file_id]["hash"]:
                info(f"File {files_hashes[file_id]["path"]} has changed, updating...")
                GatewayMqttClient().publish_message_raw("v1/devices/me/attributes/request/1", f'{"sharedKeys":"FILE_{file_id}"}')

    except json.JSONDecodeError:
        error("Failed to parse files definition")
    except Exception as e:
        error(f"Failed to update files definition: {e}")

    return True