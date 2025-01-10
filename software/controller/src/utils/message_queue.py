import os
import sqlite3
from os.path import dirname
import dataclasses
from typing import Union

from .. import custom_types
from src.custom_types import mqtt_playload_types

PROJECT_DIR = dirname(dirname(os.path.abspath(__file__)))
ACROPOLIS_DATA_PATH = os.environ.get(
    "ACROPOLIS_DATA_PATH") or os.path.join(
        dirname(PROJECT_DIR), "data")

THINGSBOARD_PAYLOADS = Union[mqtt_playload_types.MQTTCO2Data,
                             mqtt_playload_types.MQTTCO2CalibrationData,
                             mqtt_playload_types.MQTTSystemData,
                             mqtt_playload_types.MQTTWindData,
                             mqtt_playload_types.MQTTWindSensorInfo,
                             mqtt_playload_types.MQTTLogMessage]


class MessageQueue:
    """Uses an SQLite database to store messages to be forwarded to the ThingsBoard server by the gateway"""

    def __init__(self) -> None:
        db_path = os.path.join(ACROPOLIS_DATA_PATH,
                               "acropolis_comm_db.db")

        self.con = sqlite3.connect(db_path,
                                   isolation_level=None,
                                   autocommit=True)
        self.con.execute("""
                CREATE TABLE IF NOT EXISTS queue_out (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type text,
                    message text
                );
            """)
        self.con.execute("PRAGMA journal_mode=WAL;")

    def enqueue_message(self, timestamp: int,
                        payload: THINGSBOARD_PAYLOADS) -> None:
        new_message = {
            "ts": timestamp * 1000,  # ThingsBoard expects milliseconds
            "values": dataclasses.asdict(payload),
        }
        with self.con:
            sql_statement: str = "INSERT INTO queue_out (type, message) VALUES(?, ?);"
            self.con.execute(sql_statement, ("MQTT_message", str(new_message)))
            self.con.execute("PRAGMA wal_checkpoint(PASSIVE);")
