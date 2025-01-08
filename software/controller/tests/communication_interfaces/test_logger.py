import pytest
from ..pytest_utils import expect_log_file_contents
from os.path import dirname, abspath
import sys
import random
import string

PROJECT_DIR = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(PROJECT_DIR)

from src import utils, interfaces


def get_random_string(length: int, forbidden: list[str] = []) -> str:
    """a random string from lowercase letter, the strings from
    the list passed as `forbidden` will not be generated"""
    while True:
        output: str = "".join(random.choices(string.ascii_lowercase, k=length))
        if output not in forbidden:
            break
    return output


@pytest.mark.remote_update
@pytest.mark.github_action
def test_logger_with_enqueue(log_files: None) -> None:
    _test_logger()


@pytest.mark.remote_update
@pytest.mark.github_action
def test_very_long_exception_cutting(log_files: None) -> None:

    logger = interfaces.Logger(origin="pytests")

    message = utils.get_random_string(length=300)
    details = "\n".join([
        utils.get_random_string(length=80) for i in range(250)
    ])  # 20.249 characters long

    # long message and details string will test internal assertion checks
    logger.error(message=message, details=details)


def _test_logger() -> None:

    generated_log_lines = [
        "pytests                 - DEBUG         - some message a",
        "pytests                 - INFO          - some message b",
        "pytests                 - WARNING       - some message c",
        "pytests                 - ERROR         - some message d",
        "pytests                 - EXCEPTION     - ZeroDivisionError: division by zero",
        "pytests                 - EXCEPTION     - customlabel, ZeroDivisionError: division by zero",
    ]

    # verify log lines to not exist yet
    expect_log_file_contents(forbidden_content_blocks=generated_log_lines)

    # -------------------------------------------------------------------------
    # check whether logs lines are written correctly

    logger = interfaces.Logger(origin="pytests")
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
