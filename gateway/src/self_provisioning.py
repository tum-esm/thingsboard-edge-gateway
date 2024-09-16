import json
import os
import socket
import ssl
from random import randrange
from time import sleep

from paho.mqtt.client import Client

# Perform self-provisioning if needed to get an access-token for the gateway
def self_provisioning_get_access_token(args):
    # check if access token exists
    access_token_path_env_var = os.environ.get("THINGSBOARD_GATEWAY_ACCESS_TOKEN") or "./tb_access_token"

    if os.path.exists(access_token_path_env_var):
        with open(access_token_path_env_var, "r") as f:
            access_token = f.read()
            return access_token

    # else, perform self-provisioning
    print("No access token found, performing self-provisioning...")
    mqtt_client = Client()
    mqtt_client.username_pw_set("provision", None)
    mqtt_client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    mqtt_client.on_connect = (lambda client, userdata, flags, rc: print(f"Connected to ThingsBoard for self-provisioning with result code {rc}"))
    mqtt_client.connect(args.tb_host, args.tb_port)
    mqtt_client.on_message = (lambda client, userdata, message: print(f"Received message: {message.payload}"))
    mqtt_client.subscribe("/provision/response", qos=1)
    mqtt_client.loop_start()
    sleep(0.1)
    mqtt_client.publish("/provision/request",
                        payload=json.dumps({
                            "deviceName": get_device_name(args),
                            "provisionDeviceKey": "u89nftek43npopnvnt21",
                            "provisionDeviceSecret": "r4acqug0fzh2wii4o4n6"
                        }), qos=1 )

    for _ in range(100):
        sleep(0.1)
    mqtt_client.loop_stop()
    mqtt_client.disconnect()

    return "x"#access_token


def get_device_name(args):
    return (
            getattr(args, "device_name", None)
        or os.environ.get("THINGSBOARD_DEVICE_NAME")
        or socket.gethostname()
        or ("acropolis-gateway-" + str(randrange(1000000, 9999999, 1)))
    )