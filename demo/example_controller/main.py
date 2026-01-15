import os
import time

import env_vars
from db import setup_and_connect_db, write_health_check_message, enqueue_message
from sensor.basic_sensor import BasicSensor

TEG_DATA_PATH = env_vars.TEG_DATA_PATH

print(f"Starting controller with TEG_DATA_PATH={TEG_DATA_PATH}")

comm_db_path = os.path.join(TEG_DATA_PATH, "communication_queue.db")
print(f"Connecting to communication db at '{comm_db_path}'...")
db_connection = setup_and_connect_db(comm_db_path)

sensor = BasicSensor(simulate=True)

print("Entering main loop...")
# main loop
while True:
    time.sleep(1)

    print("Sending heartbeat and sensor data to ThingsBoard")

    # write heartbeat to communication db
    write_health_check_message(db_connection, int(time.time() * 1000))

    sensor_data = sensor.read()

    enqueue_message(db_connection, "measurement", {
        "simulated_sensor": sensor_data
    })

    print(f"Sensor data: {sensor_data}")

