import os
from os.path import dirname, abspath, join

PROJECT_DIR = dirname(dirname(dirname(abspath(__file__))))

# DATA/STATE/CONFIG PATH
if os.path.exists("/root/data"):
    ACROPOLIS_CONTROLLER_DATA_PATH = "/root/data"
    ACROPOLIS_CONTROLLER_CONFIG_PATH = join(ACROPOLIS_CONTROLLER_DATA_PATH,
                                            "config.json")
    ACROPOLIS_CONTROLLER_STATE_PATH = join(ACROPOLIS_CONTROLLER_DATA_PATH,
                                           "state.json")
else:
    fallback_dir = join(PROJECT_DIR, "data")
    os.makedirs(fallback_dir, exist_ok=True)
    ACROPOLIS_CONTROLLER_DATA_PATH = fallback_dir
    ACROPOLIS_CONTROLLER_CONFIG_PATH = join(PROJECT_DIR, "config",
                                            "config.json")
    ACROPOLIS_CONTROLLER_STATE_PATH = join(PROJECT_DIR, "data", "state.json")

# LOGS PATH
if os.path.exists("/root/logs"):
    ACROPOLIS_CONTROLLER_LOGS_PATH = "/root/logs"
else:
    fallback_dir = join(PROJECT_DIR, "logs")
    os.makedirs(fallback_dir, exist_ok=True)
    ACROPOLIS_CONTROLLER_LOGS_PATH = fallback_dir

# LOCKFILE PATH
if os.path.exists("/root/"):
    ACROPOLIS_CONTROLLER_LOCKFILE_PATH = join("/root",
                                              "acropolis-hardware.lock")
else:
    ACROPOLIS_CONTROLLER_LOCKFILE_PATH = join(PROJECT_DIR,
                                              "acropolis-hardware.lock")
