import os
import sqlite3
from os.path import dirname
import dataclasses
from typing import Union

from src import custom_types

PROJECT_DIR = dirname(dirname(dirname(os.path.abspath(__file__))))
ACROPOLIS_COMMUNICATION_DB_PATH = os.environ.get("ACROPOLIS_COMMUNICATION_DB_PATH") or os.path.join(PROJECT_DIR, "data", "acropolis_comm_db.db")

THINGSBOARD_PAYLOADS = Union[custom_types.MQTTCO2Data,
                             custom_types.MQTTCO2CalibrationData,
                             custom_types.MQTTSystemData,
                             custom_types.MQTTWindData,
                             custom_types.MQTTWindSensorInfo,
                             custom_types.MQTTLogMessage]


class MessageQueue:
    """Uses an SQLite database to store messages to be forwarded to the ThingsBoard server by the gateway"""

    def __init__(self) -> None:
        self.con = sqlite3.connect(ACROPOLIS_COMMUNICATION_DB_PATH)
        self.con.execute("""
                CREATE TABLE IF NOT EXISTS queue_out (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type text,
                    message text
                );
            """)

    def enqueue_message(self, timestamp: int,
                        payload: THINGSBOARD_PAYLOADS) -> None:
        new_message = {
            "ts": timestamp,
            "values": dataclasses.asdict(payload),
        }
        with self.con:
            sql_statement: str = "INSERT INTO queue_out (type, message) VALUES(?, ?)"
            self.con.executemany(sql_statement,[("MQTT_message", str(new_message))])
