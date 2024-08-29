from paho.mqtt.client import Client
from time import sleep

from args import parse_args
import ssl

class GatewayMqttClient(Client):
    def __init__(self):
        super().__init__()
        self.on_connect = self.__on_connect
        self.on_message = self.__on_message


    def __on_connect(self, _client, _userdata, _flags, _result_code, *_extra_params):
        print("Connected to ThingsBoard")
        self.subscribe("v1/devices/me/attributes/response/+")
        self.subscribe("v1/devices/me/attributes")
        self.subscribe("v2/fw/response/+")

    def __on_message(self, _client, _userdata, msg):
        print(f"Received message from topic: {msg.topic}")
        print(f"Message: {msg.payload}")

    def __update_thread(self):
        while True:
            sleep(1)


if __name__ == '__main__':
    args = parse_args()

    client = GatewayMqttClient()
    client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)
    client.username_pw_set("provision", "")
    client.connect(args.tb_host, args.tb_port)
    client.loop_forever()