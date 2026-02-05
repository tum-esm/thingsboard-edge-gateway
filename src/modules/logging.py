"""Logging utilities for the Edge Gateway.

This module provides lightweight logging helpers used throughout the Edge Gateway
and controller runtime. Log messages are printed to stdout and, when possible,
published to ThingsBoard via MQTT.

If log publication fails (e.g. due to connectivity issues), messages are buffered
locally in an SQLite database and can be forwarded later once connectivity is
restored.

Design goals
------------
- Avoid circular imports by resolving dependencies at runtime.
- Never block or crash the gateway due to logging failures.
- Preserve log messages during temporary connectivity outages.

Notes
-----
- The log level is controlled via the ``LOG_LEVEL`` environment variable.
- Buffered log messages are stored in ``GATEWAY_LOGS_BUFFER_DB_PATH``.
"""
import importlib
import os
import time

# get log level from env var
LOG_LEVEL: str = os.getenv('LOG_LEVEL') or 'INFO'

Sqlite = None
GatewayMqttClient = None
UtilsPaths = None
gateway_logs_buffer_db = None

def log(level: str, message: str):
    """Log a message and attempt to publish it via MQTT.

    The message is always printed to stdout. If the MQTT publication fails, the log
    entry is stored locally in an SQLite buffer database for later processing.

    Args:
      level: Log level (e.g. ``DEBUG``, ``INFO``, ``WARN``, ``ERROR``).
      message: Log message text.
    """
    print(f'[{level}] {message}')
    if level == 'DEBUG' and LOG_LEVEL != 'DEBUG':
        return

    # import GatewayMqttClient at runtime to avoid circular imports
    global GatewayMqttClient
    if GatewayMqttClient is None:
        GatewayMqttClient = importlib.import_module('modules.mqtt').GatewayMqttClient

    # import UtilsPaths at runtime to avoid circular imports
    global UtilsPaths
    if UtilsPaths is None:
        UtilsPaths = importlib.import_module('utils.paths')

    # import sqlite at runtime to avoid circular imports
    global Sqlite
    if Sqlite is None:
        Sqlite = importlib.import_module('modules.sqlite')

    # initialize gateway_logs_buffer_db if not already initialized
    global gateway_logs_buffer_db
    if gateway_logs_buffer_db is None:
        gateway_logs_buffer_db = Sqlite.SqliteConnection(UtilsPaths.GATEWAY_LOGS_BUFFER_DB_PATH, dont_retry=True)
        if gateway_logs_buffer_db.db_unavailable:
            gateway_logs_buffer_db = None

    # attempt to publish log message via MQTT
    publish_failure = False
    try:
        if not GatewayMqttClient().publish_log(level, message):
            publish_failure = True
            print(f'Failed to publish log message via MQTT.')
    except Exception as e:
        publish_failure = True
        print(f'Failed to publish log message via MQTT: {e}')

    # buffer unpublished message in sqlite db to be published later
    if publish_failure and gateway_logs_buffer_db is not None:
        print(f'Buffering unpublished message.')
        gateway_logs_buffer_db.execute("""
            CREATE TABLE IF NOT EXISTS log_buffer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_level text,
                message text,
                timestamp_ms INTEGER
            );
        """)
        gateway_logs_buffer_db.execute(
            "INSERT INTO log_buffer (log_level, message, timestamp_ms) VALUES (?, ?, ?)",
            (level, message, int(time.time_ns() / 1000_000))
        )

def debug(message: str):
    """Log a DEBUG-level message."""
    log('DEBUG', message)

def info(message: str):
    """Log an INFO-level message."""
    log('INFO', message)

def error(message: str):
    """Log an ERROR-level message."""
    log('ERROR', message)

def warn(message: str):
    """Log a WARN-level message."""
    log('WARN', message)