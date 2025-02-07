import importlib
import os

# get log level from env var
LOG_LEVEL = os.getenv('LOG_LEVEL') or 'INFO'

# import GatewayMqttClient at runtime to avoid circular imports
GatewayMqttClient = None

def log(level, message):
    global GatewayMqttClient
    if GatewayMqttClient is None:
        GatewayMqttClient = importlib.import_module('modules.mqtt').GatewayMqttClient
    print(f'[{level}] {message}')
    if level == 'DEBUG' and LOG_LEVEL != 'DEBUG':
        return
    try:
        GatewayMqttClient().publish_log(LOG_LEVEL, message)
    except Exception as e:
        print(f'Failed to publish log message via MQTT: {e}')

def debug(message: str):
    log('DEBUG', message)

def info(message: str):
    log('INFO', message)

def error(message: str):
    log('ERROR', message)

def warn(message: str):
    log('WARN', message)