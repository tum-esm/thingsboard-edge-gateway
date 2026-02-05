"""Miscellaneous helper utilities for the Edge Gateway.

This module provides small, reusable helper functions that are used across
multiple subsystems of the Edge Gateway. The functions are intentionally simple,
stateless (where possible), and defensive to avoid propagating errors in critical
runtime paths.

The utilities in this module focus on:
- Safe access to nested data structures.
- Defensive type extraction from loosely structured inputs.
- Graceful shutdown handling on fatal errors.
- Basic filesystem existence checks.

Notes
-----
- Functions in this module are designed to never raise unexpected exceptions.
- Logging is used instead of raising where failure must not crash the gateway.
"""

import signal
import sys
import traceback
from time import sleep
from typing import Any

from modules.logging import error

def get_maybe(dictionary, *properties) -> Any:
    """Safely retrieve a nested value from a dictionary.

    This helper traverses a dictionary using a sequence of keys and returns ``None``
    if any intermediate key is missing or if the input is ``None``.

    Args:
      dictionary: Source dictionary (may be ``None``).
      *properties: Sequence of keys to traverse.

    Returns:
      The resolved value or ``None`` if not found.
    """
    for prop in properties:
        if dictionary is None:
            return None
        dictionary = dictionary.get(prop)
    return dictionary

def get_instance_maybe(inst_type, *properties) -> Any:
    """Return the first value matching a given type.

    Iterates over the provided values and returns the first element that is an
    instance of the requested type.

    Args:
      inst_type: Expected type.
      *properties: Values to inspect.

    Returns:
      First matching instance or ``None``.
    """
    for prop in properties:
        if prop is not None and isinstance(prop, inst_type):
            return prop
    return None


def fatal_error(msg) -> None:
    """Log a fatal error and terminate the gateway gracefully.

    The function logs the error together with a stack trace, waits briefly to allow
    logs to be flushed, and then triggers a graceful shutdown using SIGINT followed
    by process termination.

    Args:
      msg: Error message or exception object.
    """
    # Add stacktrace to error message
    error_msg = str(msg)
    error_msg += "\n" + traceback.format_exc()

    error(f'FATAL ERROR: {error_msg} - exiting in 20s')
    sys.stdout.flush()

    # sleep 20s
    sleep(20)

    # Trigger the graceful shutdown handler
    signal.raise_signal( signal.SIGINT )
    sleep(15)
    sys.exit(1)

def file_exists(path: str) -> bool:
    """Check whether a file exists at the given path.

    Args:
      path: File path to check.

    Returns:
      ``True`` if the file exists and is readable, otherwise ``False``.
    """
    try:
        with open(path, 'r'):
            return True
    except FileNotFoundError:
        return False
    except Exception as e:
        error(f"Error checking if file exists at {path}: {e}")
        return False