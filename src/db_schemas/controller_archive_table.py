"""Database schema: controller archive table.

This module defines the SQL statements used to create and index the SQLite table
that stores archived controller messages.

The table is intended for local backups. Messages can later be republished or discarded
via RPC commands (see the user guide page on Remote Procedure Calls).

Schema
------
Table name:
  ``controller_archive``

Columns:
  - ``id`` (INTEGER PRIMARY KEY AUTOINCREMENT): Surrogate key.
  - ``timestamp_ms`` (INTEGER): Unix timestamp in milliseconds.
  - ``message`` (TEXT): Serialized controller message payload.

Index
-----
An index on ``timestamp_ms`` is created to accelerate time-range queries.

Notes
-----
- The SQL strings are provided as constants to be executed by the gateway's
  SQLite initialization/migration logic.
- The statements are idempotent via ``IF NOT EXISTS``.
"""

# SQL statement to create the controller message archive table.
CREATE_CONTROLLER_ARCHIVE_TABLE_QUERY: str = """
CREATE TABLE IF NOT EXISTS controller_archive (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp_ms INTEGER,
    message TEXT
);
"""

 # SQL statement to create an index for efficient time-range lookups.
CREATE_CONTROLLER_ARCHIVE_INDEX_QUERY: str = """
CREATE INDEX IF NOT EXISTS controller_archive_ts_index on controller_archive (timestamp_ms);
"""