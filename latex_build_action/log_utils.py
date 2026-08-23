#!/usr/bin/env python

"""Additional logging utility methods."""

from logging import Logger
from pathlib import Path


def print_build_log(logger: Logger, log_path: Path) -> None:
    """Print all lines of the specified build log file.

    Args:
        logger (Logger) : The logger to use for printing the log lines.
        log_path (Path) : The path to the log file.

    """
    if log_path.is_file():
        with log_path.open(encoding="UTF-8") as f:
            for line in f.read().splitlines():
                logger.info(line)
