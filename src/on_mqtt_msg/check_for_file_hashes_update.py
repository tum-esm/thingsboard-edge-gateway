import json
from modules.logging import info, error
from typing import Any
import utils
from modules.file_writer import GatewayFileWriter
from modules.mqtt import GatewayMqttClient


def on_msg_check_for_file_hash_update(msg_payload: Any) -> bool:
    file_hashes = utils.misc.get_maybe(msg_payload, "shared", "FILE_CONTENT_HASHES")

    if not isinstance(file_hashes, dict):
        error("Invalid file hashes update received")
        return False

    for file_id in file_hashes:
        file_path = utils.misc.get_maybe(file_hashes, file_id, "path")
        file_hash = utils.misc.get_maybe(file_hashes, file_id, "hash")

        # check path property
        if not isinstance(file_path, str):
            error("Invalid file hash update received, missing 'path' property")
            return False
        # check hash property
        if not isinstance(file_hash, str):
            error("Invalid file hash update received, missing 'hash' property")
            return False

    # for file_id in GatewayFileWriter().get_files():

    return True