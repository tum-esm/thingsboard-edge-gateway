import json
import os
import sqlite3
from os.path import dirname
import dataclasses
from typing import Any, Optional, Union

import filelock

from src import custom_types

PROJECT_DIR = dirname(dirname(dirname(os.path.abspath(__file__))))
ACTIVE_QUEUE_FILE = os.path.join(PROJECT_DIR, "data",
                                 "active-mqtt-messages.db")
QUEUE_ARCHIVE_DIR = os.path.join(PROJECT_DIR, "data", "archive")
ARCHIVE_FILELOCK_PATH = os.path.join(PROJECT_DIR, "data", "archive.lock")

MQTT_PAYLOADS = Union[custom_types.MQTTCO2Data,
                      custom_types.MQTTCO2CalibrationData,
                      custom_types.MQTTSystemData, custom_types.MQTTWindData,
                      custom_types.MQTTWindSensorInfo,
                      custom_types.MQTTLogMessage]


class MessageQueue:

    def __init__(self) -> None:
        self.connection = sqlite3.connect(ACTIVE_QUEUE_FILE,
                                          check_same_thread=True)
        self.__write_sql("""
                CREATE TABLE IF NOT EXISTS QUEUE (
                    internal_id INTEGER PRIMARY KEY,
                    status text,
                    content text
                );
            """)
        self.filelock = filelock.FileLock(ARCHIVE_FILELOCK_PATH, timeout=3)

    def __read_sql(self, sql_statement: str) -> list[Any]:
        with self.connection:
            results = list(self.connection.execute(sql_statement).fetchall())
        return results

    def __write_sql(
            self,
            sql_statement: str,
            parameters: Optional[list[tuple]] = None,  # type: ignore
    ) -> None:
        with self.connection:
            if parameters is not None:
                self.connection.executemany(sql_statement, parameters)
            else:
                self.connection.execute(sql_statement)

    def __add_row(
        self,
        message: str,
    ) -> None:
        """add a new message to the active queue db and message archive"""

        # add pending messages to active queue
        self.__write_sql(
            f"""
                INSERT INTO QUEUE (status, content)
                VALUES (
                    ?,
                    ?
                );
            """,
            parameters=[(json.dumps(message.dict()))],
        )

    def enqueue_message(self, timestamp: float, data: MQTT_PAYLOADS) -> None:

        values: json = dataclasses.asdict(data)

        new_message = {
            "ts": timestamp,
            "values": values,
        }

        self.__add_row(new_message)
