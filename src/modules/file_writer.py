"""Remote file read/write utilities for the Edge Gateway.

This module implements the client-side logic required for the *Remote File
Management* feature. It is responsible for reading local files, computing file
hashes, detecting changes, and synchronizing file contents and metadata with
ThingsBoard via client attributes.

The :class:`GatewayFileWriter` acts as a singleton and maintains in-memory state
about managed files and their last known hashes to enable efficient change
detection.

Responsibilities
----------------
- Read local files in binary or encoded form (text, JSON, base64).
- Compute and track file hashes for change detection.
- Mirror file contents back to ThingsBoard using ``FILE_READ_<file_key>`` attributes.
- Support path expansion using gateway environment variables (e.g. ``$DATA_PATH``).

Notes
-----
- File definitions and expected encodings are provided via shared attributes
  (see the *Remote File Management* user guide).
- This module does not apply file updates itself; it only handles reading,
  hashing, and reporting.
"""

import json
from hashlib import md5
from typing import Optional, Any

from modules.mqtt import GatewayMqttClient
from modules.logging import debug, info, error
from utils.paths import CONTROLLER_DATA_PATH

singleton_instance: Optional["GatewayFileWriter"] = None


def write_file_content_to_client_attribute(file_identifier: str, file_content: str) -> None:
    """Publish file contents to a ThingsBoard client attribute.

    Args:
      file_identifier: Logical file key as defined in the ``FILES`` attribute.
      file_content: File content encoded according to the file definition.
    """
    GatewayMqttClient().publish_message_raw("v1/devices/me/attributes", json.dumps({("FILE_READ_" + file_identifier): file_content}))


class GatewayFileWriter:
    """Handle local file reading and hash tracking for remote file management.

    This class maintains the current file definitions, the last known file hashes,
    and provides helper methods to read files and detect changes. It is implemented
    as a singleton to ensure consistent state across the gateway process.
    """
    files: Optional[dict] = None
    hashes: dict[str, str] = {}
    tb_hashes: Optional[dict] = None

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

    def expand_file_path(self, file_path: Optional[str]) -> Optional[str]:
        """Expand environment variables in a file path.

        Replaces occurrences of ``$DATA_PATH`` and legacy placeholders with the resolved
        controller data path.

        Args:
          file_path: Raw file path from the FILES definition.

        Returns:
          Expanded absolute file path, or ``None`` if input is ``None``.
        """
        if file_path is None:
            return None

        return ((file_path.replace("%DATA_PATH%", CONTROLLER_DATA_PATH)
            .replace("$DATA_PATH$", CONTROLLER_DATA_PATH))
            .replace("$DATA_PATH", CONTROLLER_DATA_PATH))


    def set_files(self, files: dict) -> None:
        """Set the current file definitions.

        Args:
          files: Dictionary defining managed files as provided by the ``FILES`` attribute.
        """
        self.files = files

    def set_tb_hashes(self, hashes: dict) -> None:
        """Set the file hashes received from ThingsBoard.

        Args:
          hashes: Hash dictionary from the ``FILE_HASHES`` client attribute.
        """
        self.tb_hashes = hashes

    # Read raw file contents into bytes array
    def read_file_raw(self, file_path: str) -> bytes | None:
        """Read a file from disk as raw bytes and update its cached hash.

        Args:
          file_path: Absolute path to the file.

        Returns:
          File contents as bytes, or ``None`` if the file does not exist.
        """
        try:
            with open(file_path, "rb") as f:
                file_content = f.read()
                file_hash = md5(file_content).hexdigest()
                if file_path not in self.hashes:
                    self.hashes[file_path] = file_hash
                return file_content
        except FileNotFoundError:
            return None

    # Read file contents into string
    def read_file(self, file_path: str, file_encoding: str) -> str | None:
        """Read a file and return its contents encoded as a string.

        Args:
          file_path: Absolute path to the file.
          file_encoding: Encoding type (``text``, ``json``, or ``base64``).

        Returns:
          Encoded file content as a string, or ``None`` if the file does not exist.
        """
        file_content = self.read_file_raw(file_path)
        if file_content is None:
            return None

        if file_encoding == "text" or file_encoding == "json":
            return file_content.decode("utf-8")
        elif file_encoding == "base64":
            import base64
            return base64.b64encode(file_content).decode("utf-8")
        else:
            error(f"Unknown file encoding: {file_encoding}, defaulting to text")
            return file_content.decode("utf-8")

    def calc_file_hash(self, path: str) -> str:
        """Calculate the MD5 hash of a file.

        Args:
          path: Absolute path to the file.

        Returns:
          MD5 hash string, or ``E_NOFILE`` if the file does not exist.
        """
        file_content = self.read_file_raw(path)
        if file_content is None:
            return "E_NOFILE"
        return md5(file_content).hexdigest()

    def did_file_change(self, path: str) -> bool:
        """Check whether a file has changed since the last read.

        Args:
          path: Absolute path to the file.

        Returns:
          ``True`` if the file content has changed, otherwise ``False``.
        """
        file_hash = self.calc_file_hash(path)
        if path not in self.hashes:
            self.hashes[path] = file_hash
            return False
        if file_hash != self.hashes[path]:
            self.hashes[path] = file_hash
            return True
        return False

    def get_files(self) -> dict:
        """Return the current file definitions.

        Returns:
          Dictionary of managed file definitions.

        Raises:
          Exception: If file definitions have not been initialized.
        """
        if self.files is None:
            raise Exception("Files definition is not available")
        return self.files

    def get_tb_file_hashes(self) -> Optional[dict]:
        """Return the file hashes received from ThingsBoard.

        Returns:
          Hash dictionary or ``None`` if not available.
        """
        return self.tb_hashes
