import signal
import sys
import traceback
from time import sleep
from typing import Any

from modules.mqtt import GatewayMqttClient


def get_maybe(dictionary, *properties) -> Any:
    for prop in properties:
        if dictionary is None:
            return None
        dictionary = dictionary.get(prop)
    return dictionary

def fatal_error(msg) -> None:
    # Set a timer to force exit if graceful shutdown fails
    signal.setitimer(signal.ITIMER_REAL, 20)

    # Add stacktrace to error message
    error = str(msg)
    error += "\n" + traceback.format_exc()

    GatewayMqttClient().publish_log('ERROR', f'FATAL ERROR: {error}')
    print("FATAL ERROR:")
    print(error)
    sys.stdout.flush()
    sleep(1)

    # Trigger the graceful shutdown handler
    signal.raise_signal( signal.SIGINT )
    sleep(20)
    sys.exit(1)