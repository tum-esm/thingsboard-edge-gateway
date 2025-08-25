import json
import os
from modules.logging import info, error
from modules.file_writer import GatewayFileWriter
from typing import Any
import utils
from modules.mqtt import GatewayMqttClient
from utils.misc import get_maybe

FILE_HASHES_TB_KEY = "FILE_HASHES"
def on_msg_check_for_file_hash_update(msg_payload: Any) -> bool:
    file_hashes = utils.misc.get_maybe(msg_payload, "client", FILE_HASHES_TB_KEY)

    if file_hashes is None:
        return False

    if not isinstance(file_hashes, dict):
        error("Invalid file hashes update received")
        return False

    info("File hashes definitions received!")

    file_defs = GatewayFileWriter().get_files()
    new_hashes = {}

    for file_id in file_defs:
        file_path = get_maybe(file_defs, file_id, "path")
        is_readonly = is_file_readonly(file_defs[file_id])

        # check if the file exists and if it doesn't, if it should be created
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            if not is_readonly and get_maybe(file_defs, file_id, "create_if_not_exist") in [None, True, "True"]:
                # if the file does not exist and should be created, request its content
                info(f"File {file_path} does not exist, requesting content update for {file_id}")
                GatewayMqttClient().request_attributes({"sharedKeys": f"FILE_CONTENT_" + file_id})
        else:
            # if the file exists, check its hash
            current_file_hash = GatewayFileWriter().calc_file_hash(file_path)
            new_hashes[file_id] = {
                "hash": current_file_hash,
            }

            file_changed = file_id not in file_hashes or get_maybe(file_hashes,file_id,"hash") != current_file_hash
            if file_changed:
                info(f"File {file_path} has changed, updating id '{file_id}'")
                GatewayMqttClient().publish_message_raw("v1/devices/me/attributes", json.dumps({
                    ("FILE_READ_" + file_id): GatewayFileWriter().read_file(file_path)
                }))
                if not is_readonly:
                    # file is not readonly, request which content should be written to it
                    info(f"Requesting file content update for '{file_id}'")
                    GatewayMqttClient().request_attributes({"sharedKeys": f"FILE_CONTENT_" + file_id})

            # check if write version has changed
            if get_maybe(file_defs, file_id, "write_version") not in [None, ""]:
                write_version_changed = get_maybe(file_defs, file_id, "write_version") != get_maybe(file_hashes, file_id, "write_version")
                if write_version_changed and not is_readonly:
                    info(f"File {file_path} write version changed, requesting content update for {file_id}")
                    GatewayMqttClient().request_attributes({"sharedKeys": f"FILE_CONTENT_" + file_id})

    GatewayMqttClient().publish_message_raw("v1/devices/me/attributes", json.dumps({
        FILE_HASHES_TB_KEY: new_hashes
    }))
    return True

def is_file_readonly(file_def: dict) -> bool:
    """
    Check if the file is readonly based on its content encoding.
    """
    return file_def.get("content_encoding") in [None, "readonly"]