import signal
from typing import Any


def set_alarm(timeout: int, label: str) -> None:
    """Set an alarm that will raise a `TimeoutError` after `timeout` seconds"""

    def alarm_handler(*_args: Any) -> None:
        raise TimeoutError(
            f"{label} took too long (timed out after {timeout} seconds)")

    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(timeout)
