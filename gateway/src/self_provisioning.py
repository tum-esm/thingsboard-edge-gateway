import os
import socket
from random import randrange

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
    mqtt_client.username_pw_set("provision", "")
    mqtt_client.connect(args.tb_host, args.tb_port)
    print("Connected to ThingsBoard for self-provisioning")
    mqtt_client.subscribe("/provision/response")
    mqtt_client.publish("/provision/request", "self-provisioning")
    mqtt_client.disconnect()

    return access_token


def get_device_name(args):
    return (
            args.device_name
        or os.environ.get("THINGSBOARD_DEVICE_NAME")
        or socket.gethostname()
        or ("acropolis-gateway-" + str(randrange(1000000, 9999999, 1)))
    )