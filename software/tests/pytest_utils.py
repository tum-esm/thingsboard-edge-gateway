from datetime import datetime
import os
from os.path import dirname, abspath, join
import time
from typing import Callable

PROJECT_DIR = dirname(dirname(abspath(__file__)))
LOG_FILE = join(PROJECT_DIR, "logs", "archive",
                datetime.now().strftime("%Y-%m-%d.log"))


def wait_for_condition(
    is_successful: Callable[[], bool],
    timeout_message: str,
    timeout_seconds: float = 5,
) -> None:
    start_time = time.time()
    while True:
        if is_successful():
            break
        if (time.time() - start_time) > timeout_seconds:
            raise TimeoutError(timeout_message)
        time.sleep(0.25)
