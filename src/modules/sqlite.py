"""SQLite database utilities for the Edge Gateway.

This module provides a lightweight SQLite wrapper used throughout the Edge Gateway
for local persistence. It is designed to be robust against transient failures,
support concurrent access via locking, and automatically recover from corrupted
or unavailable database files.

Typical use cases include buffering telemetry, logs, and controller messages when
network connectivity is unavailable.

Design goals
------------
- Safe concurrent access using a write lock.
- Automatic retry and recovery on database errors.
- Minimal abstraction over the standard ``sqlite3`` module.

Notes
-----
- Write-ahead logging (WAL) is enabled to improve concurrency.
- Databases are reset automatically if they become unusable.
"""

import os
import sqlite3
from enum import Enum
from time import sleep
from typing import Any
from threading import Lock


from utils.misc import fatal_error
from modules.logging import info


class SqliteTables(Enum):
    """Enumeration of SQLite table names used by the Edge Gateway."""
    CONTROLLER_MESSAGES = "messages"
    HEALTH_CHECK = "health_check"
    PENDING_MQTT_MESSAGES = "pending_mqtt_messages"


class SqliteConnection:
    """Thread-safe SQLite connection wrapper with automatic recovery.

    This class wraps a single SQLite connection and provides helper methods for
    executing queries, checking table state, and recovering from database errors by
    resetting the database file if necessary.

    The connection is configured for concurrent access using WAL mode and a write
    lock to serialize write operations.
    """
    def __init__(self, path : str, nr_retries : int = 3, dont_retry : bool = False) -> None:
        """Create a new SQLite connection.

        Args:
          path: Path to the SQLite database file.
          nr_retries: Number of retries before giving up.
          dont_retry: If ``True``, fail immediately without retries.
        """
        self.path = path
        self.db_unavailable = True
        self.write_lock = Lock()
        try:
            self.conn = sqlite3.connect(path, cached_statements=0, isolation_level=None, autocommit=True, check_same_thread=False)
            self.conn.execute("PRAGMA journal_mode=WAL;")       # enable write-ahead logging
            self.conn.execute("PRAGMA busy_timeout = 5000;")    # 5 seconds timeout for when the db is locked
            self.conn.execute("PRAGMA auto_vacuum  = FULL;")    # shrink the db file size when possible
            self.db_unavailable = False
        except Exception as e:
            if dont_retry:
                print(f'[SQLITE][FATAL][NO_RETRY] Failed to connect to sqlite db at "{self.path}": {e}')
                return
            if nr_retries <= 0:
                fatal_error(
                    f'[SQLITE][FATAL] Failed to connect to sqlite db at "{self.path}": {e}'
                )
            self.reset_db_conn(e, nr_retries - 1, "INIT")

    def does_table_exist(self, table) -> bool:
        """Check whether a table exists in the database.

        Args:
          table: Table name.

        Returns:
          ``True`` if the table exists, otherwise ``False``.
        """
        return len(
            self.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
            )) > 0

    def is_table_empty(self, table) -> bool:
        """Check whether a table contains any rows.

        Args:
          table: Table name.

        Returns:
          ``True`` if the table exists and contains no rows.
        """
        return self.execute(f"SELECT COUNT(*) FROM {table}")[0][0] == 0

    def do_table_values_exist(self, table):
        """Check whether a table exists and contains at least one row."""
        return self.does_table_exist(table) and not self.is_table_empty(table)

    def check(self) -> None:
        """Return the list of tables present in the database."""
        return self.execute(
            "SELECT name FROM sqlite_master WHERE type='table';")

    def execute(self, query, params=()) -> Any:
        """Execute an SQL query with optional parameters.

        Args:
          query: SQL query string.
          params: Optional query parameters.

        Returns:
          Query result as returned by ``fetchall()``, or ``None`` if the database is unavailable.
        """
        if self.db_unavailable:
            return None
        with self.write_lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute(query, params)
                fetch = cursor.fetchall()
            except Exception as e:
                if "no such table" in str(e):
                    return [()]
                sleep(3)
                self.reset_db_conn(e, 3, query)
                return self.execute(query, params)
            return fetch

    def close(self) -> None:
        """Close the underlying SQLite connection."""
        self.conn.close()

    def reset_db_conn(self, error_msg, nr_retries=3, query="unknown") -> None:
        """Reset the SQLite database after an error.

        Deletes the database file and reinitializes the connection.

        Args:
          error_msg: Original exception or error message.
          nr_retries: Remaining retry count.
          query: Query that triggered the error.
        """
        self.db_unavailable = True
        info(f"[SQLITE]: SQLite error at '{self.path}': '{str(error_msg)}' - query: '{query}'")
        info(f"[SQLITE]: resetting sqlite db at '{self.path}'")
        try:
            self.close()
            os.remove(self.path)
        except Exception as e:
            fatal_error(f'Failed to reset sqlite db at "{self.path}": {e}')

        try:
            self.__init__(self.path, nr_retries - 1)  # type: ignore[misc]
        except Exception as e:
            fatal_error(f'Failed to reset sqlite db at "{self.path}": {e}')
