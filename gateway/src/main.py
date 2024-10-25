import queue
import threading
from time import sleep

from args import parse_args
from modules import mqtt, sqlite, docker_client
from self_provisioning import self_provisioning_get_access_token
from utils import get_maybe

if __name__ == '__main__':
    # setup
    mqtt_message_queue = queue.Queue()
    docker_client = docker_client.GatewayDockerClient()
    args = parse_args()
    access_token = self_provisioning_get_access_token(args)

    archive_sqlite_db = sqlite.SqliteConnection("archive.db")
    communication_sqlite_db = sqlite.SqliteConnection("communication.db")

    # create and run the mqtt client in a separate thread
    mqtt_client = mqtt.GatewayMqttClient(mqtt_message_queue, access_token)
    mqtt_client.connect(args.tb_host, args.tb_port)
    mqtt_client_thread = threading.Thread(target=lambda: mqtt_client.loop_forever())
    mqtt_client_thread.start()

    while True:
        if not mqtt_client_thread.is_alive():
            print("MQTT client thread died, exiting in 30 seconds...")
            sleep(30)
            exit()

        # check if there are any new mqtt messages in the queue
        if not mqtt_message_queue.empty():
            msg = mqtt_message_queue.get()
            print("Got message: " + str(msg))

            sw_title = get_maybe(msg, "payload", "shared", "sw_title")
            sw_url = get_maybe(msg, "payload", "shared", "sw_url")
            sw_version = get_maybe(msg, "payload", "shared", "sw_version")
            if sw_title is not None and sw_url is not None and sw_version is not None:
                print("Software update available: " + sw_title)

            continue

        # if nothing happened this iteration, sleep for a while
        sleep(1)
