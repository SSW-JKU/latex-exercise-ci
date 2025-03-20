"""
Additional logging utility methods
"""

from pathlib import Path


def print_build_log(log_path: Path) -> None:
    """
    Prints all lines of the specified build log file.

    Args:
        log_path (Path) : The path to the log file.
    """
    if log_path.is_file():
        with open(log_path, "r", encoding="UTF-8") as f:
            for line in f.read().splitlines():
                print(line)
