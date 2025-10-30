CREATE_CONTROLLER_MESSAGES_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS {sqlite.SqliteTables.CONTROLLER_MESSAGES.value} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type text,
        message text
    );
"""