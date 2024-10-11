import os
import sqlite3
from os.path import dirname
import dataclasses
from typing import Union

from src import custom_types

PROJECT_DIR = dirname(dirname(dirname(os.path.abspath(__file__))))
ACTIVE_QUEUE_FILE = os.path.join(PROJECT_DIR, "data", "SQLite-Live-Queue.db")

THINGSBOARD_PAYLOADS = Union[custom_types.MQTTCO2Data,
                             custom_types.MQTTCO2CalibrationData,
                             custom_types.MQTTSystemData,
                             custom_types.MQTTWindData,
                             custom_types.MQTTWindSensorInfo,
                             custom_types.MQTTLogMessage]


class MessageQueue:

    def __init__(self) -> None:
        self.con = sqlite3.connect(ACTIVE_QUEUE_FILE)

        self.con.execute("""
                CREATE TABLE IF NOT EXISTS queue_out (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type text,
                    message text
                );
            """)

    def enqueue_message(self, timestamp: int,
                        payload: MEASUREMENT_PAYLOADS) -> None:

        new_message = {
            "ts": timestamp,
            "values": dataclasses.asdict(payload),
        }

        with self.con:
            sql_statement: str = "INSERT INTO queue_out (type, message) VALUES(?, ?)"
            self.con.executemany(sql_statement,
                                 [("MQTT_message", str(new_message))])
