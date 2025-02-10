from os import path, environ
from os.path import dirname, join

from modules.logging import debug

PROJECT_DIR = dirname(dirname(dirname(path.abspath(__file__)))) # path to "gateway" folder
ACROPOLIS_DATA_PATH = str(environ.get("ACROPOLIS_DATA_PATH") or join(dirname(PROJECT_DIR)))
ACROPOLIS_CONTROLLER_LOGS_PATH = str(environ.get("ACROPOLIS_CONTROLLER_LOGS_PATH") or join(dirname(dirname(PROJECT_DIR)), "logs"))
ACROPOLIS_GATEWAY_GIT_PATH = str(environ.get("ACROPOLIS_GATEWAY_GIT_PATH") or join(dirname(dirname(PROJECT_DIR)), ".git"))

debug(f'PROJECT_DIR: {PROJECT_DIR}')
debug(f'ACROPOLIS_DATA_PATH: {ACROPOLIS_DATA_PATH}')
debug(f'ACROPOLIS_GATEWAY_GIT_PATH: {ACROPOLIS_GATEWAY_GIT_PATH}')