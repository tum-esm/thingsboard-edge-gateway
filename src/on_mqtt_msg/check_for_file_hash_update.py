import json
from modules.logging import info, error
from typing import Any
import utils
from modules.file_writer import GatewayFileWriter
from modules.mqtt import GatewayMqttClient


FILE_HASH_PREFIX = "FILE_HASH_"

def on_msg_check_for_file_hash_update(msg_payload: Any) -> bool:
    payload = utils.misc.get_maybe(msg_payload, "client") or msg_payload
    file_id = None
    for key in payload:
        if key.startswith(FILE_HASH_PREFIX):
            file_id = key.replace(FILE_HASH_PREFIX, "")
            break
    if file_id is None:
        return False

    update_json = utils.misc.get_maybe(payload, FILE_HASH_PREFIX + file_id)

    if update_json is None or not isinstance(update_json, dict):
        error("Invalid file hash update received")
        return False

    file_path = utils.misc.get_maybe(update_json, "path")
    file_hash = utils.misc.get_maybe(update_json, "hash")
    # check path property
    if not file_path:
        error("Invalid file hash update received, missing 'path' property")
        return False
    # check hash property
    if not file_hash:
        error("Invalid file hash update received, missing 'hash' property")
        return False

    info("File hash received! Def ID: " + file_id)
    try:
        current_hash = GatewayFileWriter().get_file_hash(file_path)
        if current_hash != file_hash:
            info(f"File {file_id} has changed, updating...")
            GatewayMqttClient().publish_message_raw("v1/devices/me/attributes/request/1", f'{"sharedKeys":"FILE_DEF_{file_id}"}')
    except Exception as e:
        error(f"Failed to process file hash update: {e}")

    return True