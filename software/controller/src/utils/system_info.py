import os
import random
from typing import Optional


def get_cpu_temperature(simulate: bool = False) -> Optional[float]:
    if simulate:
        return random.uniform(40, 60)
    s = os.popen("vcgencmd measure_temp").readline()
    return float(s.replace("temp=", "").replace("'C\n", ""))
