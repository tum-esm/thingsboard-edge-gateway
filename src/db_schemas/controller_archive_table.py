CREATE_CONTROLLER_ARCHIVE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS controller_archive (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp_ms INTEGER,
    message TEXT
);
"""

CREATE_CONTROLLER_ARCHIVE_INDEX_QUERY = """
CREATE INDEX IF NOT EXISTS controller_archive_ts_index on controller_archive (timestamp_ms);
"""