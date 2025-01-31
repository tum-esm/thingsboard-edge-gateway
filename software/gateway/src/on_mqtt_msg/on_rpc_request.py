import json
import os
import signal
from time import sleep
from typing import Any

from modules.file_writer import GatewayFileWriter
from modules.mqtt import GatewayMqttClient

def rpc_reboot(rpc_msg_id: str, _method: Any, _params: Any):
    """Reboot the device"""
    print("[RPC] Rebooting...")
    send_rpc_response(rpc_msg_id, "OK - Rebooting")
    sleep(3)
    os.system("reboot")

def rpc_shutdown(rpc_msg_id: str, _method: Any, _params: Any):
    print("[RPC] Shutting down...")
    send_rpc_response(rpc_msg_id, "OK - Shutting down")
    sleep(3)
    os.system("shutdown now")

def rpc_exit(rpc_msg_id: str, _method: Any, _params: Any):
    print("[RPC] Exiting...")
    send_rpc_response(rpc_msg_id, "OK - Exiting")
    sleep(3)
    signal.raise_signal(signal.SIGTERM)

def rpc_ping(rpc_msg_id: str, _method: Any, _params: Any):
    print("[RPC] Pong")
    send_rpc_response(rpc_msg_id, "Pong")

def rpc_files_upsert(rpc_msg_id: str, _method: Any, params: Any):
    if type(params) is not dict:
        return send_rpc_method_error(rpc_msg_id, "Upserting file definition failed: params is not a dictionary")

    if "identifier" not in params or "path" not in params:
        return send_rpc_method_error(rpc_msg_id, "Upserting file definition failed: missing 'identifier' or 'path' in params")

    print(f"[RPC] Upserting file definition - {params['identifier']} -> {params['path']}")
    GatewayFileWriter().upsert_file(params["identifier"], params["path"])
    send_rpc_response(rpc_msg_id, f"OK - File definition upserted - {params['identifier']} -> {params['path']}")

def rpc_files_remove(rpc_msg_id: str, _method: Any, params: Any):
    if type(params) is not str:
        return send_rpc_method_error(rpc_msg_id, "Removing file definition failed: params is not a string")

    print(f"[RPC] Removing file definition '{params}'")
    GatewayFileWriter().remove_file(params)
    send_rpc_response(rpc_msg_id, f"OK - File definition removed - '{params}'")

def rpc_files_overwrite(rpc_msg_id: str, _method: Any, params: Any):
    if type(params) is not dict:
        return send_rpc_method_error(rpc_msg_id, "Overwriting file definitions failed: params is not a dict")

    print(f"[RPC] Overwriting file definitions")
    GatewayFileWriter().overwrite_files(params)
    send_rpc_response(rpc_msg_id, "OK - File definitions overwritten")

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
    "files_upsert": {
        "description": "Upsert file definition",
        "exec": rpc_files_upsert
    },
    "files_remove": {
        "description": "Remove file definition",
        "exec": rpc_files_remove
    },
    "files_overwrite": {
        "description": "Overwrite file definitions",
        "exec": rpc_files_overwrite
    }
}


def on_rpc_request(rpc_msg_id: str, method: str, params: Any) -> None:
    """Handle incoming RPC requests"""
    print(f"RPC request: {rpc_msg_id} {method} ({params})")
    GatewayMqttClient().publish_log("INFO", f"RPC request: {method} ({params})")
    if method in RPC_METHODS:
        try:
            RPC_METHODS[method]["exec"](rpc_msg_id, method, params) # type: ignore[operator]
        except Exception as e:
            print(f"Error executing RPC method '{method}': {e}")
            GatewayMqttClient().publish_log("ERROR", f"Error executing RPC method '{method}': {e}")
            send_rpc_response(rpc_msg_id, f"Error executing RPC method '{method}': {e}")
    elif method == "list":
        help_text = ["Available RPC methods:"]
        for method_name, method_data in RPC_METHODS.items():
            help_text.append(f"{method_name}: {method_data['description']}")
        send_rpc_response(rpc_msg_id, help_text)
    else:
        print(f"Unknown RPC method: {method}")
        GatewayMqttClient().publish_log("ERROR", f"Unknown RPC method: {method}")
        send_rpc_response(rpc_msg_id, f"Unknown RPC method: '{method}' - use command 'list' to get a list of available methods")


def send_rpc_response(rpc_msg_id: str, response: Any) -> bool:
    """Send an RPC response"""
    return GatewayMqttClient().publish_message_raw(
        "v1/devices/me/rpc/response/" + rpc_msg_id,
        json.dumps({"message": response})
    )

def send_rpc_method_error(rpc_msg_id, msg):
    print(f"[RPC] {msg}")
    send_rpc_response(rpc_msg_id, f"Error - {msg}")