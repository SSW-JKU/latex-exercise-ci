#!/usr/bin/env python

"""Defines configuration environments and classes."""

import json
from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path

EXERCISE_DIR_NAME = "Aufgabe"
LESSON_DIR_NAME = "Unterricht"
LESSON_SUFFIX = "_Lernziele"
SOLUTION_SUFFIX = "_solution"

# Determines whether the "old" solution build system should be used
OLD_SOLUTION_BUILD_SEMESTER_CUTOFF = 23


@dataclass
class Config:
    """Base configuration object for the LaTeX build action.

    The configuration object tracks all directory paths by parsing them from an
    initially provided JSON configuration file.
    """

    workdir: Path
    active_semester: int
    exercises: list[str]
    exercises_entry_point: str
    lesson_entry_point: str
    options: Namespace

    @staticmethod
    def from_args(options: Namespace) -> "Config":
        """Create a new Config object from CLI options.

        Args:
            options (Namespace) : the parsed CLI args

        Returns:
            Config : the config object initialized with the given args

        """
        with options.config.open(encoding="UTF-8") as cf:
            json_config = json.load(cf)
            active_semester_str = json_config["activeSemester"]
            workdir: Path = options.workdir.joinpath(active_semester_str)
            active_semester = int(active_semester_str[:2])
            exercises: list[str] = json_config["exercises"]
            exercises_entry_point: str = json_config["entryPoints"]["exercise"]
            lesson_entry_point: str = json_config["entryPoints"]["lesson"]
            return Config(workdir, active_semester, exercises, exercises_entry_point, lesson_entry_point, options)
