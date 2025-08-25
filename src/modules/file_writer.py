import json
from hashlib import md5
from typing import Optional, Any

from modules.mqtt import GatewayMqttClient
from modules.logging import debug, info, error

singleton_instance : Optional["GatewayFileWriter"] = None


def write_file_content_to_client_attribute(file_identifier: str, file_content: str) -> None:
    GatewayMqttClient().publish_message_raw("v1/devices/me/attributes", json.dumps({("FILE_READ_" + file_identifier): file_content}))


class GatewayFileWriter:
    files = None
    hashes = {}
    tb_hashes = {}

    def __init__(self) -> None:
        global singleton_instance
        if singleton_instance is None:
            debug("[FILE-WRITER] Initializing GatewayFileWriter")
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

    def set_tb_hashes(self, hashes: dict) -> None:
        self.tb_hashes = hashes

    # Read file contents into string, returns a tuple of (file_contents, is_updated)
    def read_file(self, file_path: str) -> str:
        try:
            with open(file_path, "r") as f:
                file_content = f.read()
                if file_path not in self.hashes:
                    self.hashes[file_path] = md5(file_content.encode("utf-8")).hexdigest()
        except FileNotFoundError:
            error(f"No file found at path: {file_path}")

    def overwrite_file_content(self, identifier, content):
        if self.files is None:
            raise Exception("Files definition is not available")
        if identifier not in self.files:
            raise Exception(f"File with identifier '{identifier}' not found")
        with open(self.files[identifier], "w") as f:
            f.write(content)
        write_file_content_to_client_attribute(identifier, self.read_file(self.files[identifier]))

    def calc_file_hash(self, path: str):
        file_content = self.read_file(path)
        return md5(file_content.encode("utf-8")).hexdigest()

    def did_file_change(self, path: str):
        file_hash = self.calc_file_hash(path)
        if path not in self.hashes:
            self.hashes[path] = file_hash
            return False
        if file_hash != self.hashes[path]:
            self.hashes[path] = file_hash
            return True
        return False

    def get_files(self):
        if self.files is None:
            raise Exception("Files definition is not available")
        return self.files

    def get_tb_file_hashes(self):
        return self.tb_hashes
