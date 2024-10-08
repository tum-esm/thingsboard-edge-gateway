import pytest
from ..pytest_utils import expect_log_file_contents
from os.path import dirname, abspath
import sys

PROJECT_DIR = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(PROJECT_DIR)

from src import utils


@pytest.mark.remote_update
@pytest.mark.github_action
def test_logger_without_sending(log_files: None) -> None:
    _test_logger()


@pytest.mark.remote_update
@pytest.mark.github_action
def test_very_long_exception_cutting(log_files: None) -> None:

    logger = utils.Logger(origin="pytests")

    message = utils.get_random_string(length=300)
    details = "\n".join([
        utils.get_random_string(length=80) for i in range(250)
    ])  # 20.249 characters long

    expected_log_file_content = (
        f"pytests                 - ERROR         - {message}\n" +
        "--- details: -----------------\n" + f"{details}\n" +
        "------------------------------\n")
    expected_mqtt_message = (
        f"pytests - {message[: (256 - 31)]} ... CUT (310 -> 256)" + " " +
        f"{details[: (16384 - 25)]} ... CUT (20249 -> 16384)")

    expect_log_file_contents(
        forbidden_content_blocks=[expected_log_file_content])

    logger.error(message=message, details=details)

    expect_log_file_contents(
        required_content_blocks=[expected_log_file_content])


def _test_logger(log_files: None) -> None:

    generated_log_lines = [
        "pytests                 - DEBUG         - some message a",
        "pytests                 - INFO          - some message b",
        "pytests                 - WARNING       - some message c",
        "pytests                 - ERROR         - some message d",
        "pytests                 - EXCEPTION     - ZeroDivisionError: division by zero",
        "pytests                 - EXCEPTION     - customlabel, ZeroDivisionError: division by zero",
    ]

    expect_log_file_contents(forbidden_content_blocks=generated_log_lines)

    # -------------------------------------------------------------------------
    # check whether logs lines were written correctly

    logger = utils.Logger(origin="pytests")
    logger.debug("some message a")
    logger.info("some message b", forward=True)
    logger.warning("some message c", forward=True)
    logger.error("some message d")
    try:
        30 / 0
    except Exception as e:
        logger.exception(e)
        logger.exception(e, label="customlabel", forward=True)

    expect_log_file_contents(required_content_blocks=generated_log_lines)
