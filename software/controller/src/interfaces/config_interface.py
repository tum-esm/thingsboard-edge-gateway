import json
import os
import pathlib

from custom_types import config_types

DATA_PATH = os.path.join(os.environ.get("ACROPOLIS_DATA_PATH", "unknown"))

if DATA_PATH == "unknown":
    raise FileNotFoundError(f"Data path {DATA_PATH} does not exist.")
else:
    CONFIG_PATH = os.path.join(DATA_PATH, "config.json")


class ConfigInterface:

    class FileIsMissing(Exception):
        """raised when config.json was not found"""

    class FileIsInvalid(Exception):
        """raised when config.json is not in a valid format"""

    @staticmethod
    def read() -> config_types.Config:
        try:
            with open(CONFIG_PATH, "r") as f:
                return config_types.Config(**json.load(f))
        except FileNotFoundError:
            raise ConfigInterface.FileIsMissing()
        except json.JSONDecodeError:
            raise ConfigInterface.FileIsInvalid(
                "file not in a valid json format")
        except Exception as e:
            raise ConfigInterface.FileIsInvalid(e.args[0])
