#!/usr/bin/env python

import unittest
from argparse import Namespace
from pathlib import Path

import pytest

from latex_build_action.config import Config

from ._test_utils import create_default_json, create_temp_json


class TestConfig(unittest.TestCase):
    def test_parse_config(self) -> None:
        config = Config(Namespace(config=create_default_json(), workdir=Path()))
        assert config.workdir == Path("25WS")
        assert config.active_semester == 25
        assert config.exercises == ["UE01", "UE02", "UE03"]
        assert config.exercises_entry_point == "ExerciseEntryPoint"
        assert config.lesson_entry_point == "LessonEntryPoint"

    def test_active_semester_invalid(self) -> None:
        invalid_config_json = create_temp_json(
            activeSemester="3WS",
            exercises=[],
            entryPoints={
                "exercise": "a",
                "lesson": "b",
            },
        )

        with pytest.raises(ValueError):  # noqa: PT011
            Config(Namespace(config=invalid_config_json, workdir=Path()))


if __name__ == "__main__":
    unittest.main()
