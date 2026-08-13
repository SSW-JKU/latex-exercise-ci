#!/usr/bin/env python

"""Integration test suite"""

import logging
import subprocess
import unittest
from collections.abc import Iterable
from pathlib import Path

from ._test_utils import RealFileSystemTestCase, create_temp_json

log = logging.getLogger(__name__)

INTEGRATION_TEST_CONFIG_BASE: dict[str, str | list[str] | dict[str, str]] = {
    "activeSemester": "25WS",
    "exercises": [],
    "entryPoints": {"exercise": "main.tex", "lesson": "Lernziele.tex"},
}


def run_build(
    workdir: Path, *exercises: str, extra_args: Iterable[str] = (), print_log: bool = False
) -> subprocess.CompletedProcess[bytes]:
    """Runs the integration test for the given exercises in the target working
    directory using the `INTEGRATION_TEST_CONFIG_BASE` example config as a
    baseline.

    Args:
        workdir (Path) : The working directory.
        *exercises (str) : The exercises that should be compiled.
        print_log (bool, default: False) : Debug flag that prints the command
                                           output to console.

    """
    config = {**INTEGRATION_TEST_CONFIG_BASE}
    config["exercises"] = list(exercises)
    json_config = create_temp_json(**config)

    logfile = workdir.joinpath(".test.log")

    with logfile.open("w", encoding="UTF-8") as logf:
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
            stdout=logf,
            stderr=subprocess.STDOUT,
        )

    if print_log:
        with logfile.open(encoding="UTF-8") as f:
            log.info(f.read())

    logfile.unlink()

    return result


class TestBuildExerciseFiles(RealFileSystemTestCase):
    def test_initial_compilation_success(self) -> None:

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

        run_build(self.testdir, "UE01", "UE02", "UE03").check_returncode()

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

        run_build(self.testdir, "UE01", "UE02").check_returncode()

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

        run_build(self.testdir, "UE01", "UE02", "UE03").check_returncode()

        old_checksums = [
            self.checksum("25WS", "UE01"),
            self.checksum("25WS", "UE02"),
            self.checksum("25WS", "UE03"),
        ]

        run_build(self.testdir, "UE01", "UE02", "UE03").check_returncode()

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

        result = run_build(self.testdir, "UE01", "UE02", "UE03")

        assert result.returncode != 0
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

        result = run_build(self.testdir, "UE01", "UE02", "UE03", extra_args=["--rehash-on-error"])

        assert result.returncode != 0

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

        result = run_build(
            self.testdir,
            "UE01",
            "UE02",
            "UE03",
            extra_args=["--abort-on-error", "--rehash-on-error", "--rollback-on-error"],
        )

        assert result.returncode != 0

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


if __name__ == "__main__":
    unittest.main()
