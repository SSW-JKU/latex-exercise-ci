#!/usr/bin/env python

"""Defines configuration environments and classes."""

import json
from argparse import Namespace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

EXERCISE_DIR_NAME = "Aufgabe"
LESSON_DIR_NAME = "Unterricht"
LESSON_SUFFIX = "_Lernziele"
SOLUTION_SUFFIX = "_solution"

# Determines whether the "old" solution build system should be used
OLD_SOLUTION_BUILD_SEMESTER_CUTOFF = 23


class Config:
    """Base configuration object for the LaTeX build action.

    The configuration object tracks all directory paths by parsing them from an
    initially provided JSON configuration file.
    """

    def __init__(self, options: Namespace) -> None:
        """Create a new configuration by parsing the given JSON and using the provided working directory as a base path.

        Args:
            config_file (Path) : The path to the initial config JSON.
            workdir (Path) : The directory that should be used as a base path.
            options (Namespace) : The passed CLI options.

        """
        with options.config.open(encoding="UTF-8") as cf:
            json_config = json.load(cf)
            active_semester_str = json_config["activeSemester"]
            self.workdir: Path = options.workdir.joinpath(active_semester_str)
            self.active_semester = int(active_semester_str[:2])
            self.exercises: list[str] = json_config["exercises"]
            self.exercises_entry_point: str = json_config["entryPoints"]["exercise"]
            self.lesson_entry_point: str = json_config["entryPoints"]["lesson"]
            self.options = options
