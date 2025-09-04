"""
Defines various integration test scenarios and their verification steps.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Iterable, Optional

from .test_repository import DEFAULT_EMAIL, DEFAULT_USER, TestRepository, git

BOT_NAME = "Integration Test Build[bot]"
BOT_EMAIL = "integration-test-bot@users.noreply.github.com"
BOT_COMMIT_MSG = "Build TEX files"


# auto-register scenario to simplify access and iteration
_scenarios = dict[str, "Scenario"]()


def _add_scenario(s: "Scenario") -> None:
    """
    Registers the given scenario in the `scenarios` dictionary.

    Args:
        s (Scenario) : The test scenario to register.
    """
    assert s.name not in _scenarios, f"Scenario '{s.name}' already registered."
    _scenarios[s.name] = s


def get_scenario(name: str) -> Optional["Scenario"]:
    return _scenarios.get(name, None)


def scenarios() -> Iterable[tuple[str, "Scenario"]]:
    return _scenarios.items()


def _assert(cond: bool, *msg: str) -> None:
    if not cond:
        raise AssertionError(*msg)


def _assert_eq(expected: Any, actual: Any, *msg: str) -> None:
    _assert(expected == actual, *msg, f"Expected: <{expected}>, Actual: <{actual}>")


def _check_commit(
    commit: str,
    expected_name: str,
    expected_email: str,
    expected_msg: Optional[str] = None,
) -> None:
    name, email, *msg = commit.split(":")
    _assert_eq(expected_name, name, "Invalid commit author name")
    _assert_eq(expected_email, email, "Invalid commit author email")
    if expected_msg:
        _assert_eq(expected_msg, ":".join(msg), "Mismatching commit message")


class Scenario(ABC):
    def __init__(self, name: str, path: list[str]) -> None:
        self.name = name
        self.path = Path(".") / "action_tests" / "_files" / Path(*path)

    def get_changed_files(self, repo: TestRepository) -> str:
        log = git(
            "log",
            "--name-only",
            '--pretty=""',
            "HEAD~1..HEAD",
            check=True,
            cwd=repo.local_path,
        )
        return log.stdout

    def assert_is_file(self, repo: TestRepository, *path: str) -> None:
        file_path = repo.local_path.joinpath(*path)
        _assert(
            file_path.is_file(),
            "File does not exist or is not a regular file:",
            str(file_path),
        )

    def assert_is_no_file(self, repo: TestRepository, *path: str) -> None:
        file_path = repo.local_path.joinpath(*path)
        _assert(
            not file_path.is_file(),
            "File does exist but shouldn't:",
            str(file_path),
        )

    def get_oneline_log(self, repo: TestRepository) -> str:
        return git(
            "log",
            "--oneline",
            r"--format=%an:%ae:%s",
            check=True,
            cwd=repo.local_path,
        ).stdout

    def assert_bot_commit(
        self, repo: TestRepository, *changed_files: list[str]
    ) -> None:
        log = self.get_oneline_log(repo)
        print("got commit log:\n", log)
        lines = log.split("\n")
        _assert_eq(2, len(lines), "Unexpected number of commits")
        setup_commit, bot_commit = lines

        _check_commit(setup_commit, DEFAULT_USER, DEFAULT_EMAIL)
        _check_commit(bot_commit, BOT_NAME, BOT_EMAIL, BOT_COMMIT_MSG)

        actual_changes = set(self.get_changed_files(repo).split("\n"))

        expected_changes = set(["/".join(path) for path in changed_files])

        missing_changed = expected_changes.difference(actual_changes)

        error_msg: str = ""

        if len(missing_changed) != 0:
            error_msg += f"\nThe following files should have been modified:\n{'\n'.join(missing_changed)}"

        unexpectedly_modified = actual_changes.difference(expected_changes)

        if len(unexpectedly_modified) != 0:
            error_msg += f"\nThe following files should not have been modified:\n{'\n'.join(unexpectedly_modified)}"

        if error_msg != "":
            raise AssertionError(f"Invalid changed files:{error_msg}")

    def assert_no_bot_commit(self, repo: TestRepository) -> None:
        log = self.get_oneline_log(repo)
        print("got commit log:\n", log)
        lines = log.split("\n")
        _assert_eq(1, len(lines), "Unexpected number of commits")
        _check_commit(lines[0], DEFAULT_USER, DEFAULT_EMAIL)

    @abstractmethod
    def verify(self, repo: TestRepository) -> None: ...


#### OLD BUILD SYSTEM ####


class OldBuildWorkingNoChecksum(Scenario):
    def __init__(self) -> None:
        super().__init__(
            "old_build_working_no_checksum",
            ["old_build_system", "working_build_no_checksum"],
        )

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        new_files = [
            ["22WS", "Ex01", ".checksum"],
            ["22WS", "Ex01", "Aufgabe", "Ex01.pdf"],
            ["22WS", "Ex01", "Aufgabe", "Ex01.build_log"],
            ["22WS", "Ex01", "Aufgabe", "Ex01_solution.pdf"],
            ["22WS", "Ex01", "Aufgabe", "Ex01_solution.build_log"],
            ["22WS", "Ex01", "Unterricht", "Ex01_Lernziele.pdf"],
            ["22WS", "Ex01", "Unterricht", "Ex01_Lernziele.build_log"],
        ]

        self.assert_bot_commit(repo, *new_files)

        for f in new_files:
            self.assert_is_file(repo, *f)


class OldBuildWorkingSameChecksum(Scenario):
    def __init__(self) -> None:
        super().__init__(
            "old_build_working_same_checksum",
            ["old_build_system", "working_build_same_checksum"],
        )

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        self.assert_no_bot_commit(repo)


class OldBuildWorkingSameChecksumNoPDF(Scenario):
    def __init__(self) -> None:
        super().__init__(
            "old_build_working_same_checksum_no_pdf",
            ["old_build_system", "working_build_same_checksum_no_pdf"],
        )

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        modified_files = [
            ["22WS", "Ex03", "Aufgabe", "Ex03.pdf"],
            ["22WS", "Ex03", "Aufgabe", "Ex03.build_log"],
            ["22WS", "Ex03", "Aufgabe", "Ex03_solution.pdf"],
            ["22WS", "Ex03", "Aufgabe", "Ex03_solution.build_log"],
        ]

        existing_files = [
            ["22WS", "Ex03", ".checksum"],
            ["22WS", "Ex03", "Unterricht", "Ex03_Lernziele.pdf"],
        ]

        self.assert_bot_commit(repo, *modified_files)

        for f in modified_files + existing_files:
            self.assert_is_file(repo, *f)


class OldBuildWorkingWrongCheckSum(Scenario):
    def __init__(self) -> None:
        super().__init__(
            "old_build_working_wrong_checksum",
            ["old_build_system", "working_build_wrong_checksum"],
        )

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        modified_files = [
            ["22WS", "Ex01", ".checksum"],
            ["22WS", "Ex01", "Aufgabe", "Ex01.pdf"],
            ["22WS", "Ex01", "Aufgabe", "Ex01.build_log"],
            ["22WS", "Ex01", "Aufgabe", "Ex01_solution.pdf"],
            ["22WS", "Ex01", "Aufgabe", "Ex01_solution.build_log"],
            ["22WS", "Ex01", "Unterricht", "Ex01_Lernziele.pdf"],
            ["22WS", "Ex01", "Unterricht", "Ex01_Lernziele.build_log"],
        ]

        self.assert_bot_commit(repo, *modified_files)

        for f in modified_files:
            self.assert_is_file(repo, *f)


#### NEW BUILD SYSTEM ####


_add_scenario(OldBuildWorkingNoChecksum())
_add_scenario(OldBuildWorkingSameChecksum())
_add_scenario(OldBuildWorkingSameChecksumNoPDF())
_add_scenario(OldBuildWorkingWrongCheckSum())
