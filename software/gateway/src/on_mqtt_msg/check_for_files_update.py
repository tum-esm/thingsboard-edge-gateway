import json
from typing import Any
import utils
from modules.file_writer import GatewayFileWriter


def on_msg_check_for_files_update(msg_payload: Any) -> bool:
    new_files_definition = utils.misc.get_maybe(msg_payload, "client", "files")
    if new_files_definition is None:
        return False

    print("Files update received!")
    try:
        GatewayFileWriter().set_files(new_files_definition)
    except json.JSONDecodeError:
        print("Failed to parse files definition")

    return True