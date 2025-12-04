import os
import time

import env_vars
from db import setup_and_connect_db, write_health_check_message

TEG_DATA_PATH = env_vars.TEG_DATA_PATH

print(f"Starting controller with TEG_DATA_PATH={TEG_DATA_PATH}")

print("Connecting to communication db...")
db_connection = setup_and_connect_db(os.path.join(TEG_DATA_PATH, "communication_queue.db"))

print("Entering main loop...")
# main loop
while True:
    time.sleep(1)

    # write heartbeat to communication db
    write_health_check_message(db_connection, int(time.time() * 1000))