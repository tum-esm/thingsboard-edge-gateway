import json
import sqlite3
import time


def write_health_check_message(con, timestamp_ms):
    sql_statement: str = "INSERT OR REPLACE INTO health_check (id, timestamp_ms) VALUES(?, ?);"
    con.execute(sql_statement, (1, timestamp_ms))
    con.execute("PRAGMA wal_checkpoint(PASSIVE);")

def enqueue_message(con, type: str, payload: dict) -> None:
    new_message = {
        "ts": int(time.time_ns() /
                  1_000_000),  # ThingsBoard expects milliseconds
        "values": payload,
    }
    try:
        with con:
            sql_statement: str = "INSERT INTO messages (type, message) VALUES(?, ?);"
            con.execute(sql_statement,
                             (type, json.dumps(new_message)))
            con.execute("PRAGMA wal_checkpoint(PASSIVE);")

        time.sleep(1 / 1000)  # sleep for 1ms to avoid duplicate timestamps
    except Exception:
        exit(0)

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

