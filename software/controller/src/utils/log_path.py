import os
from os.path import join


def get_logs_archive_dir(project_dir: str):
    """
    Determines the log directory based on availability.
    Defaults to '/root/logs', falls back to './logs' if unavailable.
    """
    primary_dir = "/root/logs"
    fallback_dir = join(project_dir, "logs")

    if os.path.exists(primary_dir):
        return primary_dir
    else:
        os.makedirs(fallback_dir, exist_ok=True)
        return fallback_dir
