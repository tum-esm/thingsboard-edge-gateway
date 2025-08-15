import json

from modules.file_writer import GatewayFileWriter
from modules.logging import info, error
from typing import Any
import utils
from utils.misc import file_exists

FILE_CONTENT_PREFIX = "FILE_CONTENT_"

def on_msg_check_for_file_content_update(msg_payload: Any) -> bool:
    payload = utils.misc.get_maybe(msg_payload, "shared") or msg_payload
    file_id = None
    for key in payload:
        if key.startswith(FILE_CONTENT_PREFIX):
            file_id = key.replace(FILE_CONTENT_PREFIX, "")
            break
    if file_id is None:
        return False

    files_definitions = GatewayFileWriter().get_files()
    if file_id not in files_definitions:
        error(f"File definition for {file_id} not found")
        return False
    file_definition = files_definitions[file_id]

    file_content = utils.misc.get_maybe(payload, FILE_CONTENT_PREFIX + file_id)
    if file_content is None:
        error("Invalid file content update received")
        return False
    if isinstance(file_content, dict):
        file_content = json.dumps(file_content)

    # check if file exists
    file_path = file_definition["path"]
    if not file_exists(file_path):
        if file_definition["content_encoding"]:
            if file_definition["create_if_not_exist"]:
                info(f"File {file_id} does not exist at path: {file_path}, creating it")
                try:
                    GatewayFileWriter().write_file_content_to_client_attribute(file_id, file_content)
                    file_content_hash = GatewayFileWriter().get_file_hash(file_path)
                    GatewayFileWriter().write_file_hash_to_client_attribute(file_id, file_content_hash)
                except Exception as e:
                    error(f"Failed to create file {file_id} at path {file_path}: {e}")
                    return False
            else:
                error(f"File {file_id} does not exist at path: {file_path} and 'create_if_not_exist' is set to false")
                return False
        else:
            error(f"File {file_id} does not exist at path: {file_path} and 'content_encoding' is not set")
            GatewayFileWriter().write_file_content_to_client_attribute(file_id, "")
            return False

    return True