import os


from modules.mqtt import GatewayMqttClient

# get log level from env var
LOG_LEVEL = os.getenv('LOG_LEVEL') or 'INFO'

def log(level, message):
    print(f'[{level}] {message}')
    if level is 'DEBUG' and LOG_LEVEL is not 'DEBUG':
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