from modules import sqlite

CREATE_PENDING_MESSAGES_TABLE_QUERY = f"""
    CREATE TABLE IF NOT EXISTS {sqlite.SqliteTables.PENDING_MQTT_MESSAGES.value} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type text,
        message text
    );
"""