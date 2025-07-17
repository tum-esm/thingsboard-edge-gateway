import json
import os
import signal
from time import sleep
from typing import Any, Optional

import utils.paths
from modules import sqlite
from modules.docker_client import GatewayDockerClient
from modules.file_writer import GatewayFileWriter
from modules.mqtt import GatewayMqttClient

from modules.logging import info, error, debug


def rpc_reboot(rpc_msg_id: str, _method: Any, _params: Any):
    """Reboot the device"""
    info("[RPC] Rebooting...")
    send_rpc_response(rpc_msg_id, "OK - Rebooting")
    sleep(3)
    os.system("reboot")
    sleep(3)

def rpc_shutdown(rpc_msg_id: str, _method: Any, _params: Any):
    info("[RPC] Shutting down...")
    send_rpc_response(rpc_msg_id, "OK - Shutting down")
    sleep(3)
    os.system("shutdown now")

def rpc_exit(rpc_msg_id: str, _method: Any, _params: Any):
    info("[RPC] Exiting...")
    send_rpc_response(rpc_msg_id, "OK - Exiting")
    sleep(3)
    signal.raise_signal(signal.SIGTERM)

def rpc_restart_controller(rpc_msg_id: str, _method: Any, _params: Any):
    info("[RPC] Restarting controller...")
    send_rpc_response(rpc_msg_id, "OK - Restarting Controller")
    sleep(3)
    GatewayDockerClient().stop_edge()

def rpc_ping(rpc_msg_id: str, _method: Any, _params: Any):
    info("[RPC] Pong")
    send_rpc_response(rpc_msg_id, "Pong")

def rpc_files_upsert(rpc_msg_id: str, _method: Any, params: Any):
    if type(params) is not dict:
        return send_rpc_method_error(rpc_msg_id, "Upserting file definition failed: params is not a dictionary")

    if "identifier" not in params or "path" not in params:
        return send_rpc_method_error(rpc_msg_id, "Upserting file definition failed: missing 'identifier' or 'path' in params")

    info(f"[RPC] Upserting file definition - {params['identifier']} -> {params['path']}")
    GatewayFileWriter().upsert_file(params["identifier"], params["path"])
    send_rpc_response(rpc_msg_id, f"OK - File definition upserted - {params['identifier']} -> {params['path']}")

def rpc_files_remove(rpc_msg_id: str, _method: Any, params: Any):
    if type(params) is not str:
        return send_rpc_method_error(rpc_msg_id, "Removing file definition failed: params is not a string")

    info(f"[RPC] Removing file definition '{params}'")
    GatewayFileWriter().remove_file(params)
    send_rpc_response(rpc_msg_id, f"OK - File definition removed - '{params}'")

def rpc_files_init(rpc_msg_id: str, _method: Any, _params: Any):
    info(f"[RPC] Initializing file definitions")
    GatewayFileWriter().initialize_files()
    send_rpc_response(rpc_msg_id, "OK - File definitions initialized")

def rpc_file_append_line(rpc_msg_id: str, _method: Any, params: Any):
    if type(params) is not dict:
        return send_rpc_method_error(rpc_msg_id, "Appending file line failed: params is not a dictionary")

    if "identifier" not in params or "line" not in params:
        return send_rpc_method_error(rpc_msg_id, "Appending file line failed: missing 'identifier' or 'line' in params")
    if type(params["identifier"]) is not str or type(params["line"]) is not str:
        return send_rpc_method_error(rpc_msg_id, "Appending file line failed: 'identifier' and 'line' must be strings")

    info(f"[RPC] Appending file line - '{params['identifier']}' += '{params['line']}'")
    GatewayFileWriter().append_file_line(params["identifier"], params["line"])
    send_rpc_response(rpc_msg_id, f"OK - File line appended - '{params['identifier']}' += '{params['line']}'")

def rpc_file_remove_line(rpc_msg_id: str, _method: Any, params: Any):
    if type(params) is not dict:
        return send_rpc_method_error(rpc_msg_id, "Removing file line failed: params is not a dictionary")

    if "identifier" not in params or "line" not in params:
        return send_rpc_method_error(rpc_msg_id, "Removing file line failed: missing 'identifier' or 'line' in params")
    if type(params["identifier"]) is not str or type(params["line"]) is not str:
        return send_rpc_method_error(rpc_msg_id, "Removing file line failed: 'identifier' and 'line' must be strings")

    info(f"[RPC] Removing file line - '{params['identifier']}' -= '{params['line']}'")
    GatewayFileWriter().remove_file_line(params["identifier"], params["line"])
    send_rpc_response(rpc_msg_id, f"OK - File line removed - '{params['identifier']}' -= '{params['line']}'")

def rpc_file_overwrite_content(rpc_msg_id: str, _method: Any, params: Any):
    if type(params) is not dict:
        return send_rpc_method_error(rpc_msg_id, "Overwriting file content failed: params is not a dictionary")

    if "identifier" not in params or "content" not in params:
        return send_rpc_method_error(rpc_msg_id, "Overwriting file content failed: missing 'identifier' or 'content' in params")
    if type(params["identifier"]) is not str or type(params["content"]) is not str:
        return send_rpc_method_error(rpc_msg_id, "Overwriting file content failed: 'identifier' and 'content' must be strings")

    info(f"[RPC] Overwriting file content - '{params['identifier']}' = '{params['content']}'")
    GatewayFileWriter().overwrite_file_content(params["identifier"], params["content"])
    send_rpc_response(rpc_msg_id, f"OK - File content overwritten - '{params['identifier']}' = '{params['content']}'")


def verify_start_end_timestamp_params(params: Any) -> Optional[str]:
    if type(params) is not dict:
        return "params is not a dictionary"
    if "start_timestamp_ms" not in params or "end_timestamp_ms" not in params:
        return "missing 'start_timestamp_ms' or 'end_timestamp_ms' in params"
    if type(params["start_timestamp_ms"]) is not int or type(params["end_timestamp_ms"]) is not int:
        return "'start_timestamp_ms' and 'end_timestamp_ms' must be integers"
    start_timestamp_ms = params["start_timestamp_ms"]
    end_timestamp_ms = params["end_timestamp_ms"]
    if start_timestamp_ms >= end_timestamp_ms:
        return "'start_timestamp_ms' must be less than 'end_timestamp_ms'"
    return None


def rpc_archive_republish_messages(rpc_msg_id: str, _method: Any, params: Any):
    params_verify_err = verify_start_end_timestamp_params(params)
    if params_verify_err is not None:
        return send_rpc_method_error(rpc_msg_id, f"Republishing archived messages failed: {params_verify_err}")

    start_timestamp_ms = params["start_timestamp_ms"]
    end_timestamp_ms = params["end_timestamp_ms"]
    if start_timestamp_ms <= 1735719469_000 or end_timestamp_ms >= 2524637869_000:
        return send_rpc_method_error(rpc_msg_id, "Republishing archived messages failed: 'start_timestamp_ms' and 'end_timestamp_ms' must be within the range of 1735719469_000 and 2524637869_000")

    archive_sqlite_db = sqlite.SqliteConnection(utils.paths.GATEWAY_ARCHIVE_DB_PATH)
    if archive_sqlite_db.db_unavailable:
        return send_rpc_method_error(rpc_msg_id, "Republishing archived messages failed: archive database unavailable")

    info(f"[RPC] Republishing messages - {start_timestamp_ms} -> {end_timestamp_ms}")
    message_count = 0
    while start_timestamp_ms < end_timestamp_ms:
        messages = archive_sqlite_db.execute("""SELECT id, timestamp_ms, message 
            FROM controller_archive 
            WHERE timestamp_ms > ? AND timestamp_ms < ? 
            ORDER BY timestamp_ms ASC LIMIT 200""",
            (start_timestamp_ms, end_timestamp_ms)
        )
        for message in messages:
            message_count += 1
            debug(f"Republishing message with timestamp {message[1]}")
            GatewayMqttClient().publish_telemetry(json.dumps({"ts": message[1], "values": json.loads(message[2])}))
            start_timestamp_ms = message[1]
        if len(messages) < 200:
            break
    archive_sqlite_db.close()
    send_rpc_response(rpc_msg_id, f"OK - {message_count} messages republished - {start_timestamp_ms} -> {end_timestamp_ms}")

def rpc_archive_discard_messages(rpc_msg_id: str, _method: Any, params: Any):
    params_verify_err = verify_start_end_timestamp_params(params)
    if params_verify_err is not None:
        return send_rpc_method_error(rpc_msg_id, f"Discarding archived messages failed: {params_verify_err}")

    start_timestamp_ms = params["start_timestamp_ms"]
    end_timestamp_ms = params["end_timestamp_ms"]
    if end_timestamp_ms >= 2524637869_000:
        return send_rpc_method_error(rpc_msg_id, "Discarding archived messages failed: 'end_timestamp_ms' must be < 2524637869_000")

    archive_sqlite_db = sqlite.SqliteConnection(utils.paths.GATEWAY_ARCHIVE_DB_PATH)
    if archive_sqlite_db.db_unavailable:
        return send_rpc_method_error(rpc_msg_id, "Discarding archived messages failed: archive database unavailable")

    info(f"[RPC] Discarding archived messages - {start_timestamp_ms} -> {end_timestamp_ms}")
    message_count = archive_sqlite_db.execute("DELETE FROM controller_archive WHERE timestamp_ms > ? AND timestamp_ms < ?",
                                              (start_timestamp_ms, end_timestamp_ms))
    archive_sqlite_db.close()
    send_rpc_response(rpc_msg_id, f"OK - {message_count} messages discarded - {start_timestamp_ms} -> {end_timestamp_ms}")


RPC_METHODS = {
    "reboot": {
        "description": "Reboot the device",
        "exec": rpc_reboot
    },
    "shutdown": {
        "description": "Shutdown the device",
        "exec": rpc_shutdown
    },
    "exit": {
        "description": "Exits the gateway process (triggers gateway restart)",
        "exec": rpc_exit
    },
    "ping": {
        "description": "Ping the device (returns 'pong' reply)",
        "exec": rpc_ping
    },
    "restart_controller": {
        "description": "Restart the controller docker container",
        "exec": rpc_restart_controller
    },
    "files_upsert": {
        "description": "Upsert file definition ({identifier: str, path: str})",
        "exec": rpc_files_upsert
    },
    "files_remove": {
        "description": "Remove file definition ({identifier: str})",
        "exec": rpc_files_remove
    },
    "files_init": {
        "description": "Initialize file definitions",
        "exec": rpc_files_init
    },
    "file_append_line": {
        "description": "Append line to file ({identifier: str, line: str})",
        "exec": rpc_file_append_line
    },
    "file_remove_line": {
        "description": "Remove line from file ({identifier: str, line: str})",
        "exec": rpc_file_remove_line
    },
    "file_overwrite_content": {
        "description": "Overwrite file content ({identifier: str, content: str})",
        "exec": rpc_file_overwrite_content
    },
    "archive_republish_messages": {
        "description": "Republish messages from archive ({start_timestamp_ms: int, end_timestamp_ms: int})",
        "exec": rpc_archive_republish_messages
    },
    "archive_discard_messages": {
        "description": "Discard messages from archive ({start_timestamp_ms: int, end_timestamp_ms: int})",
        "exec": rpc_archive_discard_messages
    },
}


def on_rpc_request(rpc_msg_id: str, method: str, params: Any) -> None:
    """Handle incoming RPC requests"""
    info(f"RPC request: {rpc_msg_id} {method} ({params})")
    if method in RPC_METHODS:
        try:
            RPC_METHODS[method]["exec"](rpc_msg_id, method, params) # type: ignore[operator]
        except Exception as e:
            error(f"Error executing RPC method '{method}': {e}")
            GatewayMqttClient().publish_log("ERROR", f"Error executing RPC method '{method}': {e}")
            send_rpc_response(rpc_msg_id, f"Error executing RPC method '{method}': {e}")
    elif method == "list":
        help_text = ["Available RPC methods:"]
        for method_name, method_data in RPC_METHODS.items():
            help_text.append(f"{method_name}: {method_data['description']}")
        send_rpc_response(rpc_msg_id, help_text)
    else:
        error(f"Unknown RPC method: {method}")
        GatewayMqttClient().publish_log("ERROR", f"Unknown RPC method: {method}")
        send_rpc_response(rpc_msg_id, f"Unknown RPC method: '{method}' - use command 'list' to get a list of available methods")


def send_rpc_response(rpc_msg_id: str, response: Any) -> bool:
    """Send an RPC response"""
    return GatewayMqttClient().publish_message_raw(
        "v1/devices/me/rpc/response/" + rpc_msg_id,
        json.dumps({"message": response})
    )

def send_rpc_method_error(rpc_msg_id, msg):
    error(f"[RPC] {msg}")
    send_rpc_response(rpc_msg_id, f"Error - {msg}")