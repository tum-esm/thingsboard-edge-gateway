"""
Example controller for the ThingsBoard Edge Gateway demo.

This script demonstrates a minimal controller loop that:
- initializes the local communication database,
- instantiates a (simulated) sensor,
- periodically writes a heartbeat message,
- enqueues sensor measurements for downstream processing.

It is intended as a reference implementation for testing and development
purposes and is not optimized for production use.
"""
import os
import time

import env_vars
from db import setup_and_connect_db, write_health_check_message, enqueue_message
from sensor.basic_sensor import BasicSensor

# Base directory for gateway runtime data
TEG_DATA_PATH = env_vars.TEG_DATA_PATH

print(f"Starting controller with TEG_DATA_PATH={TEG_DATA_PATH}")

# SQLite database used as a local message queue
comm_db_path = os.path.join(TEG_DATA_PATH, "communication_queue.db")
print(f"Connecting to communication db at '{comm_db_path}'...")
db_connection = setup_and_connect_db(comm_db_path)

# Instantiate the sensor in simulation mode
sensor = BasicSensor(simulate=True)

print("Entering main loop...")
# Main controller loop with a fixed heartbeat interval
while True:
    time.sleep(1)

    print("Sending heartbeat and sensor data to ThingsBoard")

    # Write heartbeat to communication db (timestamp in milliseconds since epoch)
    write_health_check_message(db_connection, int(time.time() * 1000))

    # Read sensor data (simulated)
    sensor_data = sensor.read()

    # Queue the payload for asynchronous forwarding to ThingsBoard
    enqueue_message(db_connection, "measurement", {
        "simulated_sensor": sensor_data
    })

    print(f"Sensor data: {sensor_data}")
