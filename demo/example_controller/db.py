import json
import sqlite3
import time


def write_health_check_message(con, timestamp_ms):
    """
    Write a health check heartbeat message to the database.

    This function updates a single-row table with the latest timestamp
    indicating the last health check heartbeat.

    Parameters:
    - con: SQLite connection object.
    - timestamp_ms: Timestamp in milliseconds since epoch.
    """
    # Use a single-row table to store the latest heartbeat timestamp
    sql_statement: str = "INSERT OR REPLACE INTO health_check (id, timestamp_ms) VALUES(?, ?);"
    con.execute(sql_statement, (1, timestamp_ms))
    # Trigger a passive WAL checkpoint to ensure changes are flushed without blocking
    con.execute("PRAGMA wal_checkpoint(PASSIVE);")

def enqueue_message(con, type: str, payload: dict) -> None:
    """
    Enqueue a telemetry message into the local SQLite queue.

    The message is stored with a timestamp in milliseconds since epoch,
    conforming to ThingsBoard's expected format.

    Parameters:
    - con: SQLite connection object.
    - type: Message type as a string.
    - payload: Dictionary containing the message payload.
    """
    # Create timestamp in milliseconds since epoch for ThingsBoard compatibility
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
            # Trigger a passive WAL checkpoint to ensure changes are flushed without blocking
            con.execute("PRAGMA wal_checkpoint(PASSIVE);")

        # Sleep briefly to avoid duplicate timestamps in rapid message generation
        time.sleep(1 / 1000)  # sleep for 1ms to avoid duplicate timestamps
    except Exception:
        exit(0)

def setup_and_connect_db(db_path):
    """
    Initialize and connect to the SQLite database.

    This function creates necessary tables for message queueing and health
    check heartbeats if they do not exist. It also enables WAL journal mode
    for improved concurrency and robustness.

    Parameters:
    - db_path: Path to the SQLite database file.

    Returns:
    - SQLite connection object with autocommit enabled.
    """
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
    # Enable Write-Ahead Logging mode for better concurrency and durability
    con.execute("PRAGMA journal_mode=WAL;")

    return con
