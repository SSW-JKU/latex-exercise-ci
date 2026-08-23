#!/usr/bin/env python

"""Integration test suite"""

from pathlib import Path

import pytest

from tests._integration_test_utils import BuildErrorFn, BuildSuccessFn, failed_builds, success_builds

from ._test_utils import RealFileSystemTest


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

    @pytest.mark.parametrize("build", success_builds)
    def test_exercise_directory_does_not_exist_success(self, build: BuildSuccessFn) -> None:

        # create exercise folders
        self.generate_tex_files(
            Path("UE01", "Aufgabe", "main.tex"),
            Path("UE01", "Unterricht", "Lernziele.tex"),
            valid=True,
        )

        build(self.testdir, ["UE01", "UE02"])

        self.assert_was_compiled("25WS", "UE01", "Aufgabe", "UE01")
        self.assert_was_compiled("25WS", "UE01", "Aufgabe", "UE01_solution")
        self.assert_was_compiled("25WS", "UE01", "Unterricht", "UE01_Lernziele")

        self.assert_is_file("25WS", "UE01", ".checksum")

    @pytest.mark.parametrize("build", success_builds)
    def test_repeated_compilation_success(self, build: BuildSuccessFn) -> None:

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

        old_checksums = [
            self.checksum("25WS", "UE01"),
            self.checksum("25WS", "UE02"),
            self.checksum("25WS", "UE03"),
        ]

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

        new_checksums = [
            self.checksum("25WS", "UE01"),
            self.checksum("25WS", "UE02"),
            self.checksum("25WS", "UE03"),
        ]

        assert old_checksums == new_checksums

    @pytest.mark.parametrize("build", failed_builds)
    def test_build_error_no_hashing_no_rollback(self, build: BuildErrorFn) -> None:

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

        build(self.testdir, ["UE01", "UE02", "UE03"], [])

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

    @pytest.mark.parametrize("build", failed_builds)
    def test_build_error_rehashing_no_rollback(self, build: BuildErrorFn) -> None:

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

        build(self.testdir, ["UE01", "UE02", "UE03"], ["--rehash-on-error"])

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

    @pytest.mark.parametrize("build", failed_builds)
    def test_build_error_rehashing_rollback(self, build: BuildErrorFn) -> None:

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

        build(
            self.testdir,
            ["UE01", "UE02", "UE03"],
            ["--abort-on-error", "--rehash-on-error", "--rollback-on-error"],
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
