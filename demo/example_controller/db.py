import sqlite3


def write_health_check_message(con, timestamp_ms):
    con.execute("INSERT INTO health_check (timestamp_ms) VALUES (?)", (timestamp_ms,))


def setup_and_connect_db(db_path):
    con = sqlite3.connect(db_path,
                               isolation_level=None,
                               autocommit=True)
    # Create queue_out for MQTT messages
    con.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type text,
                message text
            );
        """)
    # Create health_check_queue for health check messages
    con.execute("""
        CREATE TABLE IF NOT EXISTS health_check (
            id INTEGER PRIMARY KEY,
            timestamp_ms INTEGER            
        );
    """)
    con.execute("PRAGMA journal_mode=WAL;")

    return con