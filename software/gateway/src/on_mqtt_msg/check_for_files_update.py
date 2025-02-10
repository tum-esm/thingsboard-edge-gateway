import json
from modules.logging import info, error
from typing import Any
import utils
from modules.file_writer import GatewayFileWriter


def on_msg_check_for_files_update(msg_payload: Any) -> bool:
    new_files_definition = utils.misc.get_maybe(msg_payload, "client", "files")
    if new_files_definition is None:
        return False

    info("Files update received!")
    try:
        GatewayFileWriter().set_files(new_files_definition)
    except json.JSONDecodeError:
        error("Failed to parse files definition")
    except Exception as e:
        error(f"Failed to update files definition: {e}")

    return True