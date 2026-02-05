"""Database schema: controller messages table.

This module defines the SQL statement used to create the SQLite table that stores
controller messages before they are processed or forwarded by the Edge Gateway.

The table acts as a lightweight message buffer and is typically used for short-
lived persistence of controller-originated messages.

Schema
------
Table name:
  Value of ``sqlite.SqliteTables.CONTROLLER_MESSAGES``

Columns:
  - ``id`` (INTEGER PRIMARY KEY AUTOINCREMENT): Surrogate key.
  - ``type`` (TEXT): Message type or category.
  - ``message`` (TEXT): Serialized message payload.

Notes
-----
- The SQL statement is provided as a constant and executed by the gateway's
  database initialization logic.
- Table creation is idempotent via ``IF NOT EXISTS``.
"""

from modules import sqlite

# SQL statement to create the controller messages table.
CREATE_CONTROLLER_MESSAGES_TABLE_QUERY: str = """
    CREATE TABLE IF NOT EXISTS {sqlite.SqliteTables.CONTROLLER_MESSAGES.value} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type text,
        message text
    );
"""