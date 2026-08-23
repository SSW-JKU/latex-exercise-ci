#!/usr/bin/env python

"""Integration test suite"""

import logging
import subprocess
from collections.abc import Callable, Iterable
from enum import Enum
from pathlib import Path

import pytest

from ._test_utils import RealFileSystemTest, create_temp_json

log = logging.getLogger(__name__)

INTEGRATION_TEST_CONFIG_BASE: dict[str, str | list[str] | dict[str, str]] = {
    "activeSemester": "25WS",
    "exercises": [],
    "entryPoints": {"exercise": "main.tex", "lesson": "Lernziele.tex"},
}


def build_success(workdir: Path, exercises: Iterable[str]) -> None:
    """Runs the integration test for the given exercises in the target working
    directory using the `INTEGRATION_TEST_CONFIG_BASE` example config as a
    baseline and asserts that the build was successful.

    Args:
        workdir (Path): the current working directory
        exercises (Iterable[str]) : The exercises that should be compiled.
    """
    result = _build(workdir, exercises)
    result.check_returncode()


def build_failed(workdir: Path, exercises: Iterable[str], extra_args: Iterable[str] = ()) -> None:
    """Runs the integration test for the given exercises in the target working
    directory using the `INTEGRATION_TEST_CONFIG_BASE` example config as a
    baseline and asserts that the build failed.

    Args:
        workdir (Path): the current working directory
        exercises (Iterable[str]) : The exercises that should be compiled.
        extra_args (Iterable[str], optional) : Additional command line arguments
                                                to pass to the build action.
    """
    result = _build(workdir, exercises, extra_args)
    assert result.returncode != 0, "Expected build to fail, but it succeeded."


class Mode(Enum):
    DEFAULT = 1
    DEBUG = 2


def _build(
    workdir: Path, exercises: Iterable[str], extra_args: Iterable[str] = (), mode: Mode = Mode.DEFAULT
) -> subprocess.CompletedProcess[bytes]:
    """Runs the integration test for the given exercises in the target working
    directory using the `INTEGRATION_TEST_CONFIG_BASE` example config as a
    baseline and logs the command output if enabled.

    Args:
        workdir (Path): the current working directory
        exercises (Iterable[str]) : The exercises that should be compiled.
        extra_args (Iterable[str], optional) : Additional command line arguments
                                                to pass to the build action.
        mode (Mode, optional) : The running mode of the test

    Returns:
        subprocess.CompletedProcess[bytes] : The result of the build process.
    """

    config = {**INTEGRATION_TEST_CONFIG_BASE}
    config["exercises"] = list(exercises)
    json_config = create_temp_json(**config)

    logfile = workdir.joinpath(".test.log")

    with logfile.open("w", encoding="UTF-8") as f:
        result = subprocess.run(  # noqa: S603
            [
                "/usr/bin/env",
                "python3",
                "-m",
                "latex_build_action",
                "-d",
                str(workdir.absolute()),
                "-c",
                str(json_config.absolute()),
                "--no-git",
                *extra_args,
            ],
            check=False,
            shell=False,
            stdout=f,
            stderr=subprocess.STDOUT,
        )

    if mode == Mode.DEBUG:
        with logfile.open(encoding="UTF-8") as f:
            log.info(f.read())

    logfile.unlink()

    return result


type BuildSuccessFn = Callable[[Path, Iterable[str]], None]


success_builds: list[BuildSuccessFn] = [build_success]


class TestBuildExerciseFiles(RealFileSystemTest):
    @pytest.mark.parametrize("build", success_builds)
    def test_initial_compilation_success(self, build: BuildSuccessFn) -> None:

        # create exercise folders
        self.generate_tex_files(
            Path("UE01", "Aufgabe", "main.tex"),
            Path("UE01", "Unterricht", "Lernziele.tex"),
            Path("UE02", "Aufgabe", "main.tex"),
            Path("UE02", "Unterricht", "Lernziele.tex"),
            Path("UE03", "Aufgabe", "main.tex"),
            Path("UE03", "Unterricht", "Lernziele.tex"),
            valid=True,
        )

        build(self.testdir, ["UE01", "UE02", "UE03"])

        self.assert_was_compiled("25WS", "UE01", "Aufgabe", "UE01")
        self.assert_was_compiled("25WS", "UE01", "Aufgabe", "UE01_solution")
        self.assert_was_compiled("25WS", "UE01", "Unterricht", "UE01_Lernziele")

        self.assert_was_compiled("25WS", "UE02", "Aufgabe", "UE02")
        self.assert_was_compiled("25WS", "UE02", "Aufgabe", "UE02_solution")
        self.assert_was_compiled("25WS", "UE02", "Unterricht", "UE02_Lernziele")

        self.assert_was_compiled("25WS", "UE03", "Aufgabe", "UE03")
        self.assert_was_compiled("25WS", "UE03", "Aufgabe", "UE03_solution")
        self.assert_was_compiled("25WS", "UE03", "Unterricht", "UE03_Lernziele")

        self.assert_is_file("25WS", "UE01", ".checksum")
        self.assert_is_file("25WS", "UE02", ".checksum")
        self.assert_is_file("25WS", "UE03", ".checksum")

    def test_exercise_directory_does_not_exist_success(self) -> None:

        # create exercise folders
        self.generate_tex_files(
            Path("UE01", "Aufgabe", "main.tex"),
            Path("UE01", "Unterricht", "Lernziele.tex"),
            valid=True,
        )

        build_success(self.testdir, ["UE01", "UE02"])

        self.assert_was_compiled("25WS", "UE01", "Aufgabe", "UE01")
        self.assert_was_compiled("25WS", "UE01", "Aufgabe", "UE01_solution")
        self.assert_was_compiled("25WS", "UE01", "Unterricht", "UE01_Lernziele")

        self.assert_is_file("25WS", "UE01", ".checksum")

    def test_repeated_compilation_success(self) -> None:

        # create exercise folders
        self.generate_tex_files(
            Path("UE01", "Aufgabe", "main.tex"),
            Path("UE01", "Unterricht", "Lernziele.tex"),
            Path("UE02", "Aufgabe", "main.tex"),
            Path("UE02", "Unterricht", "Lernziele.tex"),
            Path("UE03", "Aufgabe", "main.tex"),
            Path("UE03", "Unterricht", "Lernziele.tex"),
            valid=True,
        )

        build_success(self.testdir, ["UE01", "UE02", "UE03"])

        old_checksums = [
            self.checksum("25WS", "UE01"),
            self.checksum("25WS", "UE02"),
            self.checksum("25WS", "UE03"),
        ]

        build_success(self.testdir, ["UE01", "UE02", "UE03"])

        self.assert_was_compiled("25WS", "UE01", "Aufgabe", "UE01")
        self.assert_was_compiled("25WS", "UE01", "Aufgabe", "UE01_solution")
        self.assert_was_compiled("25WS", "UE01", "Unterricht", "UE01_Lernziele")

        self.assert_was_compiled("25WS", "UE02", "Aufgabe", "UE02")
        self.assert_was_compiled("25WS", "UE02", "Aufgabe", "UE02_solution")
        self.assert_was_compiled("25WS", "UE02", "Unterricht", "UE02_Lernziele")

        self.assert_was_compiled("25WS", "UE03", "Aufgabe", "UE03")
        self.assert_was_compiled("25WS", "UE03", "Aufgabe", "UE03_solution")
        self.assert_was_compiled("25WS", "UE03", "Unterricht", "UE03_Lernziele")

        self.assert_is_file("25WS", "UE01", ".checksum")
        self.assert_is_file("25WS", "UE02", ".checksum")
        self.assert_is_file("25WS", "UE03", ".checksum")

        new_checksums = [
            self.checksum("25WS", "UE01"),
            self.checksum("25WS", "UE02"),
            self.checksum("25WS", "UE03"),
        ]

        assert old_checksums == new_checksums

    def test_build_error_no_hashing_no_rollback(self) -> None:

        # create exercise folders
        self.generate_tex_files(
            Path("UE01", "Aufgabe", "main.tex"),
            Path("UE01", "Unterricht", "Lernziele.tex"),
            Path("UE02", "Aufgabe", "main.tex"),
            Path("UE02", "Unterricht", "Lernziele.tex"),
            Path("UE03", "Aufgabe", "main.tex"),
            valid=True,
        )

        self.generate_tex_files(Path("UE03", "Unterricht", "Lernziele.tex"), valid=False)

        build_failed(self.testdir, ["UE01", "UE02", "UE03"])

        self.assert_is_file("25WS", "UE01", ".checksum")
        self.assert_is_file("25WS", "UE02", ".checksum")
        self.assert_no_file("25WS", "UE03", ".checksum")

        self.assert_was_compiled("25WS", "UE01", "Aufgabe", "UE01")
        self.assert_was_compiled("25WS", "UE01", "Aufgabe", "UE01_solution")
        self.assert_was_compiled("25WS", "UE01", "Unterricht", "UE01_Lernziele")

        self.assert_was_compiled("25WS", "UE02", "Aufgabe", "UE02")
        self.assert_was_compiled("25WS", "UE02", "Aufgabe", "UE02_solution")
        self.assert_was_compiled("25WS", "UE02", "Unterricht", "UE02_Lernziele")

        self.assert_was_compiled("25WS", "UE03", "Aufgabe", "UE03")
        self.assert_was_compiled("25WS", "UE03", "Aufgabe", "UE03_solution")
        self.assert_not_compiled("25WS", "UE03", "Unterricht", "UE03_Lernziele")

    def test_build_error_rehashing_no_rollback(self) -> None:

        # create exercise folders
        self.generate_tex_files(
            Path("UE01", "Unterricht", "Lernziele.tex"),
            Path("UE02", "Unterricht", "Lernziele.tex"),
            Path("UE03", "Aufgabe", "main.tex"),
            Path("UE03", "Unterricht", "Lernziele.tex"),
            valid=True,
        )

        self.generate_tex_files(
            Path("UE01", "Aufgabe", "main.tex"),
            Path("UE02", "Aufgabe", "main.tex"),
            valid=False,
        )

        build_failed(self.testdir, ["UE01", "UE02", "UE03"], extra_args=["--rehash-on-error"])

        self.assert_is_file("25WS", "UE01", ".checksum")
        self.assert_is_file("25WS", "UE02", ".checksum")
        self.assert_is_file("25WS", "UE03", ".checksum")

        self.assert_not_compiled("25WS", "UE01", "Aufgabe", "UE01")
        self.assert_not_compiled("25WS", "UE01", "Aufgabe", "UE01_solution")
        self.assert_was_compiled("25WS", "UE01", "Unterricht", "UE01_Lernziele")

        self.assert_not_compiled("25WS", "UE02", "Aufgabe", "UE02")
        self.assert_not_compiled("25WS", "UE02", "Aufgabe", "UE02_solution")
        self.assert_was_compiled("25WS", "UE02", "Unterricht", "UE02_Lernziele")

        self.assert_was_compiled("25WS", "UE03", "Aufgabe", "UE03")
        self.assert_was_compiled("25WS", "UE03", "Aufgabe", "UE03_solution")
        self.assert_was_compiled("25WS", "UE03", "Unterricht", "UE03_Lernziele")

    def test_build_error_rehashing_rollback(self) -> None:

        # create exercise folders
        self.generate_tex_files(
            Path("UE01", "Aufgabe", "main.tex"),
            Path("UE01", "Unterricht", "Lernziele.tex"),
            Path("UE02", "Aufgabe", "main.tex"),
            Path("UE02", "Unterricht", "Lernziele.tex"),
            Path("UE03", "Aufgabe", "main.tex"),
            Path("UE03", "Unterricht", "Lernziele.tex"),
            valid=True,
        )

        self.generate_tex_files(
            Path("UE01", "Unterricht", "Lernziele.tex"),
            Path("UE02", "Unterricht", "Lernziele.tex"),
            Path("UE03", "Unterricht", "Lernziele.tex"),
            valid=False,
        )

        build_failed(
            self.testdir,
            ["UE01", "UE02", "UE03"],
            extra_args=["--abort-on-error", "--rehash-on-error", "--rollback-on-error"],
        )

        self.assert_is_file("25WS", "UE01", ".checksum")
        self.assert_is_file("25WS", "UE02", ".checksum")
        self.assert_is_file("25WS", "UE03", ".checksum")

        self.assert_not_compiled("25WS", "UE01", "Aufgabe", "UE01", expect_buildlog=False)
        self.assert_not_compiled("25WS", "UE01", "Aufgabe", "UE01_solution", expect_buildlog=False)
        self.assert_not_compiled("25WS", "UE01", "Unterricht", "UE01_Lernziele", expect_buildlog=False)

        self.assert_not_compiled("25WS", "UE02", "Aufgabe", "UE02", expect_buildlog=False)
        self.assert_not_compiled("25WS", "UE02", "Aufgabe", "UE02_solution", expect_buildlog=False)
        self.assert_not_compiled("25WS", "UE02", "Unterricht", "UE02_Lernziele", expect_buildlog=False)

        self.assert_not_compiled("25WS", "UE03", "Aufgabe", "UE03", expect_buildlog=False)
        self.assert_not_compiled("25WS", "UE03", "Aufgabe", "UE03_solution", expect_buildlog=False)
        self.assert_not_compiled("25WS", "UE03", "Unterricht", "UE03_Lernziele", expect_buildlog=False)
