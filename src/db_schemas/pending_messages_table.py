"""Database schema: pending MQTT messages table.

This module defines the SQL statement used to create the SQLite table that stores
pending MQTT messages managed by the Edge Gateway.

The table is used as a temporary persistence layer for outbound MQTT messages
that could not yet be delivered, for example due to connectivity issues. Messages
are removed once they are successfully published.

Schema
------
Table name:
  Value of ``sqlite.SqliteTables.PENDING_MQTT_MESSAGES``

Columns:
  - ``id`` (INTEGER PRIMARY KEY AUTOINCREMENT): Surrogate key.
  - ``type`` (TEXT): Message type or category.
  - ``message`` (TEXT): Serialized MQTT message payload.

Notes
-----
- The SQL statement is executed during gateway database initialization.
- Table creation is idempotent via ``IF NOT EXISTS``.
- This table is distinct from the controller archive and intended for short-lived buffering only.
"""

from modules import sqlite

# SQL statement to create the pending MQTT messages table.
CREATE_PENDING_MESSAGES_TABLE_QUERY: str = f"""
    CREATE TABLE IF NOT EXISTS {sqlite.SqliteTables.PENDING_MQTT_MESSAGES.value} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type text,
        message text
    );
"""