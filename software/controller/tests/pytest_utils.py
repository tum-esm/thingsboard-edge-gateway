from datetime import datetime
import os
from os.path import dirname, abspath, join

PROJECT_DIR = dirname(dirname(abspath(__file__)))
LOG_FILE = join(PROJECT_DIR, "logs", "archive",
                datetime.now().strftime("%Y-%m-%d.log"))


