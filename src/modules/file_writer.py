import json
from hashlib import md5
from typing import Optional, Any

from modules.mqtt import GatewayMqttClient
from modules.logging import debug, info, error

singleton_instance : Optional["GatewayFileWriter"] = None

class GatewayFileWriter:
    files = None
    hashes = {}

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
        self.update_all_files_content_client_attributes()

    def initialize_files(self) -> None:
        if self.files is not None:
            raise Exception("Files definition is already available")
        self.files = {}
        self.write_files_definition_to_client_attribute()

    def upsert_file(self, file_identifier: str, file_path: str) -> None:
        if self.files is None:
            self.initialize_files()
        self.files[file_identifier] = file_path
        self.write_file_content_to_client_attribute(file_identifier, self.read_file(file_path)[0])
        self.write_files_definition_to_client_attribute()

    def remove_file(self, file_identifier: str) -> None:
        if self.files is None:
            self.initialize_files()
        if file_identifier not in self.files:
            raise Exception(f"File with identifier '{file_identifier}' not found")
        del self.files[file_identifier]
        self.write_file_content_to_client_attribute(file_identifier, "")
        self.write_files_definition_to_client_attribute()

    def update_all_files_content_client_attributes(self) -> None:
        if self.files is None:
            raise Exception("Files definition is not available")
        for file_identifier in self.files:
            info(f"Updating file content for file: {file_identifier}")
            file_content, is_updated = self.read_file(self.files[file_identifier])
            if is_updated:
                self.write_file_content_to_client_attribute(file_identifier, file_content)

    def write_files_definition_to_client_attribute(self) -> None:
        GatewayMqttClient().publish_message_raw("v1/devices/me/attributes", json.dumps({"files": self.files}))

    def write_file_content_to_client_attribute(self, file_identifier: str, file_content: str) -> None:
        GatewayMqttClient().publish_message_raw("v1/devices/me/attributes", json.dumps({("file_" + file_identifier): file_content}))

    # Read file contents into string, returns a tuple of (file_contents, is_updated)
    def read_file(self, file_path: str) -> (str, bool):
        try:
            with open(file_path, "r") as f:
                file_contents = f.read()
                contents_hash = md5(file_contents.encode("utf-8")).hexdigest()
                if self.hashes[file_path] == contents_hash:
                    return file_contents, False
                else:
                    self.hashes[file_path] = contents_hash
                    return file_contents, True
        except FileNotFoundError:
            error(f"No file found at path: {file_path}")

    def append_file_line(self, identifier, line):
        if self.files is None:
            raise Exception("Files definition is not available")
        if identifier not in self.files:
            raise Exception(f"File with identifier '{identifier}' not found")
        with open(self.files[identifier], "a") as f:
            f.write("\n" + line)

        self.write_file_content_to_client_attribute(identifier, self.read_file(self.files[identifier])[0])

    def remove_file_line(self, identifier, line):
        if self.files is None:
            raise Exception("Files definition is not available")
        if identifier not in self.files:
            raise Exception(f"File with identifier '{identifier}' not found")
        with open(self.files[identifier], "r") as f:
            lines = f.readlines()
        with open(self.files[identifier], "w") as f:
            for l in lines:
                if l.strip() != line:
                    f.write(l)
        self.write_file_content_to_client_attribute(identifier, self.read_file(self.files[identifier])[0])

    def overwrite_file_content(self, identifier, content):
        if self.files is None:
            raise Exception("Files definition is not available")
        if identifier not in self.files:
            raise Exception(f"File with identifier '{identifier}' not found")
        with open(self.files[identifier], "w") as f:
            f.write(content)
        self.write_file_content_to_client_attribute(identifier, self.read_file(self.files[identifier])[0])