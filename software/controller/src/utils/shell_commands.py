import os
import subprocess
from typing import Optional


class CommandLineException(Exception):

    def __init__(self, value: str, details: Optional[str] = None) -> None:
        self.value = value
        self.details = details
        Exception.__init__(self)

    def __str__(self) -> str:
        return repr(self.value)


def run_shell_command(
    command: str,
    working_directory: Optional[str] = None,
) -> str:
    """runs a shell command and raises a CommandLineException if the
    return code is not zero, returns the stdout"""
    p = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=working_directory,
        env=os.environ.copy(),
        executable="/bin/bash",
    )
    stdout = p.stdout.decode("utf-8", errors="replace").strip()
    stderr = p.stderr.decode("utf-8", errors="replace").strip()
    if p.returncode != 0:
        raise CommandLineException(
            f"command '{command}' failed with exit code {p.returncode}",
            details=f"\nstderr:\n{stderr}\nstout:\n{stdout}",
        )

    return stdout
