# pylint: disable=missing-module-docstring

from argparse import Namespace
import unittest

from pathlib import Path
from latex_build_action.config import Config
from ._test_utils import create_default_json, create_temp_json


class TestConfig(unittest.TestCase):
    # pylint: disable=missing-class-docstring

    def test_parse_config(self) -> None:
        # pylint: disable=missing-function-docstring
        config = Config(Namespace(config=create_default_json(), workdir=Path()))
        self.assertEqual(config.workdir, Path("25WS"))
        self.assertEqual(config.active_semester, "25WS")
        self.assertEqual(config.exercises, ["UE01", "UE02", "UE03"])
        self.assertEqual(config.exercises_entry_point, "ExerciseEntryPoint")
        self.assertEqual(config.lesson_entry_point, "LessonEntryPoint")

    def test_determine_semester_valid(self) -> None:
        # pylint: disable=missing-function-docstring
        config = Config(Namespace(config=create_default_json(), workdir=Path()))
        self.assertEqual(25, config.determine_semester())

    def test_determine_semester_invalid(self) -> None:
        # pylint: disable=missing-function-docstring
        invalid_config_json = create_temp_json(
            activeSemester="3WS",
            exercises=[],
            entryPoints={
                "exercise": "a",
                "lesson": "b",
            },
        )

        config = Config(Namespace(config=invalid_config_json, workdir=Path()))
        self.assertRaises(ValueError, config.determine_semester)


if __name__ == "__main__":
    unittest.main()
