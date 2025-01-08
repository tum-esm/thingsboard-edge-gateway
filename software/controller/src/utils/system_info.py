import os
import random
import subprocess
import time
from datetime import datetime
from typing import Optional


def get_cpu_temperature(simulate: bool = False) -> Optional[float]:
    if simulate:
        return random.uniform(40, 60)
    s = os.popen("vcgencmd measure_temp").readline()
    return float(s.replace("temp=", "").replace("'C\n", ""))


def read_os_uptime() -> int:
    """Reads OS system uptime from terminal and returns time in seconds."""
    uptime_date = subprocess.check_output("uptime -s", shell=True)
    uptime_string = uptime_date.decode("utf-8").strip()
    uptime_datetime = datetime.strptime(uptime_string, "%Y-%m-%d %H:%M:%S")
    uptime_seconds = int(time.time() - uptime_datetime.timestamp())

    return uptime_seconds
