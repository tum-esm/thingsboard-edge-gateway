from datetime import datetime
import json
import os
from typing import Any, Optional
import pytest
from os.path import dirname, abspath, join, isfile
from src import custom_types
import sqlite3

PROJECT_DIR = dirname(dirname(abspath(__file__)))


def _save_file(original_path: str, temporary_path: str,
               test_content: Optional[str]) -> None:
    if isfile(temporary_path):
        os.remove(temporary_path)

    try:
        os.rename(original_path, temporary_path)
    except FileNotFoundError:
        pass

    if test_content is None:
        if isfile(original_path):
            os.remove(original_path)
    else:
        with open(original_path, "w") as f:
            f.write(test_content)


def _restore_file(original_path: str, temporary_path: str) -> None:
    tmp_content = None
    if isfile(original_path):
        with open(original_path, "rb") as f:
            tmp_content = f.read()
        os.remove(original_path)

    try:
        os.rename(temporary_path, original_path)
    except FileNotFoundError:
        pass

    if tmp_content is not None:
        with open(temporary_path, "wb") as f:
            f.write(tmp_content)


@pytest.fixture(scope="function")
def sample_config() -> Any:
    """use the config template as a temporary config file"""
    CONFIG_FILE = join(PROJECT_DIR, "config", "config.json")
    TMP_CONFIG_FILE = join(PROJECT_DIR, "config", "config.tmp.json")

    with open(join(PROJECT_DIR, "config", "config.template.json")) as f:
        sample_config = custom_types.Config(**json.load(f))

    _save_file(
        CONFIG_FILE,
        TMP_CONFIG_FILE,
        json.dumps(sample_config.dict(), indent=4),
    )

    yield sample_config

    _restore_file(CONFIG_FILE, TMP_CONFIG_FILE)


@pytest.fixture(scope="function")
def log_files() -> Any:
    """
    1. store actual log files in a temporary location
    2. set up a new, empty log file just for the test
    3. restore the original log file after the test
    """

    LOG_FILE = join(PROJECT_DIR, "logs", "archive",
                    datetime.now().strftime("%Y-%m-%d.log"))
    TMP_LOG_FILE = join(PROJECT_DIR, "logs", "archive",
                        datetime.now().strftime("%Y-%m-%d.tmp.log"))

    _save_file(LOG_FILE, TMP_LOG_FILE, "")

    yield

    _restore_file(LOG_FILE, TMP_LOG_FILE)

    with open(TMP_LOG_FILE) as f:
        logs_after_test = f.read()
    print("*** LOGS AFTER TEST:")
    print(logs_after_test, end="")
    print("***")
