import json
from typing import Optional, Any

from modules.mqtt import GatewayMqttClient

singleton_instance : Optional["GatewayFileWriter"] = None

class GatewayFileWriter:
    files = None

    def __init__(self) -> None:
        global singleton_instance
        if singleton_instance is None:
            print("[FILE-WRITER] Initializing GatewayFileWriter")
            super().__init__()
            singleton_instance = self

    # Singleton pattern
    def __new__(cls: Any) -> Any:
        global singleton_instance
        if singleton_instance is not None:
            return singleton_instance
        return super(GatewayFileWriter, cls).__new__(cls)

    def set_files(self, files: dict) -> None:
        self.files = files

    def upsert_file(self, file_identifier: str, file_path: str) -> None:
        self.files[file_identifier] = file_path
        self.update_files_client_attribute()

    def remove_file(self, file_identifier: str) -> None:
        del self.files[file_identifier]
        self.update_files_client_attribute()

    def update_files_client_attribute(self) -> None:
        GatewayMqttClient().publish_message_raw("v1/devices/me/attributes", json.dumps({"files": self.files}))

    # Read file contents into string
    def read_file(self, file_path: str) -> str:
        try:
            with open(file_path, "r") as f:
                file_contents = f.read()
        except FileNotFoundError:
            print(f"No file found at path: {file_path}")
            file_contents = ""
        return file_contents