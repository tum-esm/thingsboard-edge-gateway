"""Command-line argument parsing for the Edge Gateway.

This module defines the command-line interface (CLI) arguments supported by the
ThingsBoard Edge Gateway entry point. Parsed arguments are used to override
runtime configuration such as the ThingsBoard host and port.

The CLI is intentionally minimal and primarily intended for local testing,
development, and containerized deployments.
"""
import argparse
import os


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the Edge Gateway.

    Returns:
      Parsed command-line arguments as an :class:`argparse.Namespace`.
    """
    parser = argparse.ArgumentParser(prog='ThingsBoard Edge Gateway', )
    parser.add_argument('--tb-host', help="ThingsBoard host address (hostname or IP)", default=os.environ.get("TB_HOST"),)
    parser.add_argument('--tb-port', type=int, help="ThingsBoard server port", default=os.environ.get("TB_PORT"))
    return parser.parse_args()
