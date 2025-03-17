"""
Integration test suite
"""

from typing import Iterable
from pathlib import Path
import subprocess
import unittest
from ._test_utils import RealFileSystemTestCase, create_temp_json

INTEGRATION_TEST_CONFIG_BASE = {
    "activeSemester": "25WS",
    "exercises": [],
    "entryPoints": {"exercise": "main.tex", "lesson": "Lernziele.tex"},
}


def run_build(
    workdir: Path,
    *exercises: str,
    extra_args: Iterable[str] = tuple(),
    print_log: bool = False
) -> subprocess.CompletedProcess[bytes]:
    """
    Runs the integration test for the given exercises in the target working
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

    with open(logfile, "w", encoding="UTF-8") as log:
        result = subprocess.run(
            [
                "python3",
                "build.py",
                "-d",
                str(workdir.absolute()),
                "-c",
                str(json_config.absolute()),
                "--no-git",
                *extra_args,
            ],
            check=False,
            shell=False,
            stdout=log,
            stderr=subprocess.STDOUT,
        )

    if print_log:
        with open(logfile, "r", encoding="UTF-8") as f:
            print(f.read())

    logfile.unlink()

    return result


class TestBuildExerciseFiles(RealFileSystemTestCase):
    # pylint: disable=missing-class-docstring

    def test_initial_compilation_success(self) -> None:
        # pylint: disable=missing-function-docstring

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

        self.assertWasCompiled("25WS", "UE01", "Aufgabe", "UE01")
        self.assertWasCompiled("25WS", "UE01", "Aufgabe", "UE01_solution")
        self.assertWasCompiled("25WS", "UE01", "Unterricht", "UE01_Lernziele")

        self.assertWasCompiled("25WS", "UE02", "Aufgabe", "UE02")
        self.assertWasCompiled("25WS", "UE02", "Aufgabe", "UE02_solution")
        self.assertWasCompiled("25WS", "UE02", "Unterricht", "UE02_Lernziele")

        self.assertWasCompiled("25WS", "UE03", "Aufgabe", "UE03")
        self.assertWasCompiled("25WS", "UE03", "Aufgabe", "UE03_solution")
        self.assertWasCompiled("25WS", "UE03", "Unterricht", "UE03_Lernziele")

        self.assertIsFile("25WS", "UE03", ".checksum")

    def test_repeated_compilation_success(self) -> None:
        # pylint: disable=missing-function-docstring

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

        self.assertWasCompiled("25WS", "UE01", "Aufgabe", "UE01")
        self.assertWasCompiled("25WS", "UE01", "Aufgabe", "UE01_solution")
        self.assertWasCompiled("25WS", "UE01", "Unterricht", "UE01_Lernziele")

        self.assertWasCompiled("25WS", "UE02", "Aufgabe", "UE02")
        self.assertWasCompiled("25WS", "UE02", "Aufgabe", "UE02_solution")
        self.assertWasCompiled("25WS", "UE02", "Unterricht", "UE02_Lernziele")

        self.assertWasCompiled("25WS", "UE03", "Aufgabe", "UE03")
        self.assertWasCompiled("25WS", "UE03", "Aufgabe", "UE03_solution")
        self.assertWasCompiled("25WS", "UE03", "Unterricht", "UE03_Lernziele")

        self.assertIsFile("25WS", "UE01", ".checksum")
        self.assertIsFile("25WS", "UE02", ".checksum")
        self.assertIsFile("25WS", "UE03", ".checksum")

        new_checksums = [
            self.checksum("25WS", "UE01"),
            self.checksum("25WS", "UE02"),
            self.checksum("25WS", "UE03"),
        ]

        self.assertEqual(old_checksums, new_checksums)

    def test_build_error_no_hashing_no_rollback(self) -> None:
        # pylint: disable=missing-function-docstring

        # create exercise folders
        self.generate_tex_files(
            Path("UE01", "Aufgabe", "main.tex"),
            Path("UE01", "Unterricht", "Lernziele.tex"),
            Path("UE02", "Aufgabe", "main.tex"),
            Path("UE02", "Unterricht", "Lernziele.tex"),
            Path("UE03", "Aufgabe", "main.tex"),
            valid=True,
        )

        self.generate_tex_files(
            Path("UE03", "Unterricht", "Lernziele.tex"), valid=False
        )

        result = run_build(self.testdir, "UE01", "UE02", "UE03")

        self.assertNotEqual(result.returncode, 0)
        self.assertIsFile("25WS", "UE01", ".checksum")
        self.assertIsFile("25WS", "UE02", ".checksum")
        self.assertNoFile("25WS", "UE03", ".checksum")

        self.assertWasCompiled("25WS", "UE01", "Aufgabe", "UE01")
        self.assertWasCompiled("25WS", "UE01", "Aufgabe", "UE01_solution")
        self.assertWasCompiled("25WS", "UE01", "Unterricht", "UE01_Lernziele")

        self.assertWasCompiled("25WS", "UE02", "Aufgabe", "UE02")
        self.assertWasCompiled("25WS", "UE02", "Aufgabe", "UE02_solution")
        self.assertWasCompiled("25WS", "UE02", "Unterricht", "UE02_Lernziele")

        self.assertWasCompiled("25WS", "UE03", "Aufgabe", "UE03")
        self.assertWasCompiled("25WS", "UE03", "Aufgabe", "UE03_solution")
        self.assertNotCompiled("25WS", "UE03", "Unterricht", "UE03_Lernziele")

    def test_build_error_rehashing_no_rollback(self) -> None:
        # pylint: disable=missing-function-docstring

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

        result = run_build(
            self.testdir, "UE01", "UE02", "UE03", extra_args=["--rehash-on-error"]
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIsFile("25WS", "UE01", ".checksum")
        self.assertIsFile("25WS", "UE02", ".checksum")
        self.assertIsFile("25WS", "UE03", ".checksum")

        self.assertNotCompiled("25WS", "UE01", "Aufgabe", "UE01")
        self.assertNotCompiled("25WS", "UE01", "Aufgabe", "UE01_solution")
        self.assertWasCompiled("25WS", "UE01", "Unterricht", "UE01_Lernziele")

        self.assertNotCompiled("25WS", "UE02", "Aufgabe", "UE02")
        self.assertNotCompiled("25WS", "UE02", "Aufgabe", "UE02_solution")
        self.assertWasCompiled("25WS", "UE02", "Unterricht", "UE02_Lernziele")

        self.assertWasCompiled("25WS", "UE03", "Aufgabe", "UE03")
        self.assertWasCompiled("25WS", "UE03", "Aufgabe", "UE03_solution")
        self.assertWasCompiled("25WS", "UE03", "Unterricht", "UE03_Lernziele")

    def test_build_error_rehashing_rollback(self) -> None:
        # pylint: disable=missing-function-docstring

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

        self.assertNotEqual(result.returncode, 0)
        self.assertIsFile("25WS", "UE01", ".checksum")
        self.assertIsFile("25WS", "UE02", ".checksum")
        self.assertIsFile("25WS", "UE03", ".checksum")

        self.assertNotCompiled("25WS", "UE01", "Aufgabe", "UE01", expect_buildlog=False)
        self.assertNotCompiled(
            "25WS", "UE01", "Aufgabe", "UE01_solution", expect_buildlog=False
        )
        self.assertNotCompiled(
            "25WS", "UE01", "Unterricht", "UE01_Lernziele", expect_buildlog=False
        )

        self.assertNotCompiled("25WS", "UE02", "Aufgabe", "UE02", expect_buildlog=False)
        self.assertNotCompiled(
            "25WS", "UE02", "Aufgabe", "UE02_solution", expect_buildlog=False
        )
        self.assertNotCompiled(
            "25WS", "UE02", "Unterricht", "UE02_Lernziele", expect_buildlog=False
        )

        self.assertNotCompiled("25WS", "UE03", "Aufgabe", "UE03", expect_buildlog=False)
        self.assertNotCompiled(
            "25WS", "UE03", "Aufgabe", "UE03_solution", expect_buildlog=False
        )
        self.assertNotCompiled(
            "25WS", "UE03", "Unterricht", "UE03_Lernziele", expect_buildlog=False
        )


if __name__ == "__main__":
    unittest.main()
