import time
import traceback
from datetime import datetime
from os.path import dirname, abspath, join
from typing import Literal, Optional
import sys

from custom_types import mqtt_playload_types, config_types
from utils import message_queue, shell_commands, log_path

PROJECT_DIR = dirname(dirname(dirname(abspath(__file__))))
LOGS_ARCHIVE_DIR = log_path.get_logs_archive_dir(PROJECT_DIR)


def _pad_str_right(text: str,
                   min_width: int,
                   fill_char: Literal["0", " "] = " ") -> str:
    if len(text) >= min_width:
        return text
    else:
        return text + (fill_char * (min_width - len(text)))


class Logger:

    def __init__(self,
                 config: config_types.Config,
                 origin: str = "insert-name-here") -> None:

        self.config = config
        self.origin: str = origin
        self.print_to_console = self.config.active_components.log_to_console
        self.write_to_file = self.config.active_components.log_to_file
        self.message_queue = message_queue.MessageQueue()

    def horizontal_line(self,
                        fill_char: Literal["-", "=", ".", "_"] = "=") -> None:
        """writes a debug log line, used for verbose output"""
        self._write_log_line("INFO", fill_char * 46)

    def debug(self, message: str) -> None:
        """writes a debug log line, used for verbose output"""
        self._write_log_line("DEBUG", message)

    def info(
        self,
        message: str,
        forward: bool = False,
        details: str = "",
    ) -> None:
        """Writes an info log line. Forwards to MQTT client when set to True."""
        if len(details) == 0:
            self._write_log_line("INFO", message)
        else:
            self._write_log_line("INFO", f"{message}, details: {details}")
        if forward:
            self._enqueue_message(
                level="info",
                subject=message,
                details=details,
            )

    def warning(
        self,
        message: str,
        forward: bool = False,
        details: str = "",
    ) -> None:
        """writes a warning log line, sends the message via
        MQTT when config is passed (required for revision number)
        """
        if len(details) == 0:
            self._write_log_line("WARNING", message)
        else:
            self._write_log_line("WARNING", f"{message}, details: {details}")
        if forward:
            self._enqueue_message(
                level="warning",
                subject=message,
            )

    def error(
        self,
        message: str,
        forward: bool = False,
        details: str = "",
    ) -> None:
        """writes an error log line, sends the message via
        MQTT when config is passed (required for revision number)
        """
        if len(details) == 0:
            self._write_log_line("ERROR", message)
        else:
            self._write_log_line(
                "ERROR",
                "\n".join([
                    message,
                    "--- details: -----------------",
                    details,
                    "------------------------------",
                ]),
            )
        if forward:
            self._enqueue_message(level="error",
                                  subject=message,
                                  details=details)

    def exception(
        self,
        e: Exception,
        label: Optional[str] = None,
        forward: bool = False,
    ) -> None:
        """logs the traceback of an exception, sends the message via
        MQTT when config is passed (required for revision number).

        exceptions will be formatted like this:

        ```txt
        (label, )ZeroDivisionError: division by zer
        --- details: -----------------
        ...
        --- traceback: ---------------
        ...
        ------------------------------
        ```
        """
        exception_name = traceback.format_exception_only(type(e), e)[0].strip()
        exception_traceback = "\n".join(
            traceback.format_exception(type(e), e, e.__traceback__)).strip()
        exception_details = "None"
        if isinstance(e,
                      shell_commands.CommandLineException) and (e.details
                                                                is not None):
            exception_details = e.details.strip()

        subject_string = (exception_name
                          if label is None else f"{label}, {exception_name}")
        details_string = (f"--- details: -----------------\n" +
                          f"{exception_details}\n" +
                          f"--- traceback: ---------------\n" +
                          f"{exception_traceback}\n" +
                          f"------------------------------")

        self._write_log_line("EXCEPTION",
                             f"{subject_string}\n{details_string}")
        if forward:
            self._enqueue_message(
                level="error",
                subject=subject_string,
                details=details_string,
            )

    def _write_log_line(self, level: str, message: str) -> None:
        """formats the log line string and writes it to
        `logs/current-logs.log`"""
        now = datetime.now()
        utc_offset = round(
            (datetime.now() - datetime.utcnow()).total_seconds() / 3600, 1)
        if round(utc_offset) == utc_offset:
            utc_offset = round(utc_offset)

        log_string = (
            f"{str(now)[:-3]} UTC{'' if utc_offset < 0 else '+'}{utc_offset} "
            + f"- {_pad_str_right(self.origin, min_width=23)} " +
            f"- {_pad_str_right(level, min_width=13)} " + f"- {message}\n")
        if self.print_to_console:
            print(log_string, end="")
            sys.stdout.flush()
        if self.write_to_file:
            # YYYY-MM-DD.log
            log_file_name = str(now)[:10] + ".log"
            with open(join(LOGS_ARCHIVE_DIR, log_file_name), "a") as f1:
                f1.write(log_string)

    def _enqueue_message(
        self,
        level: Literal["info", "warning", "error"],
        subject: str,
        details: str = "",
    ) -> None:
        subject = f"{self.origin} - {subject}"

        if len(subject) > 256:
            extension_message_subject = f" ... CUT ({len(subject)} -> 256)"
            subject = (subject[:(256 - len(extension_message_subject))] +
                       extension_message_subject)

        if len(details) > 16384:
            extension_message_details = f" ... CUT ({len(details)} -> 16384)"
            details = (details[:(16384 - len(extension_message_details))] +
                       extension_message_details)

        assert (len(subject) <= 256)
        assert (len(details) <= 16384)

        time.sleep(1)  # ensure that log message has unique timestamp

        self.message_queue.enqueue_message(
            timestamp=int(time.time()),
            payload=mqtt_playload_types.MQTTLogMessage(
                severity=level,
                message=subject + " " + details,
            ),
        )
