CREATE_PENDING_MESSAGES_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS {sqlite.SqliteTables.PENDING_MQTT_MESSAGES.value} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type text,
        message text
    );
"""