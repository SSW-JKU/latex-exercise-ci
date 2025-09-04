"""
Defines various integration test scenarios and their verification steps.
"""

from abc import ABC, abstractmethod
import os
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
    """
    Retrieves the scenario registered under the given `name`.

    Args:
        name (str) : The name that identifies the target scenario

    Returns:
        (Scenario | None) The scenario or `None` if no such scenario is
        registered
    """
    return _scenarios.get(name, None)


def scenarios() -> Iterable[tuple[str, "Scenario"]]:
    """
    Returns all registered scenarios.

    Returns:
        (Iterable[tuple[str, Scenario]]) an iterable of name-scenario tuples
    """
    return _scenarios.items()


def _assert(cond: bool, *msg: str) -> None:
    """
    Asserts that the given `cond` is `True` and otherwise raises an
    `AssertionError` with the given `msg`.

    Args:
        cond (bool) : The condition to check
        *msg (str) : The error message to add to the raised error
    """
    if not cond:
        raise AssertionError(*msg)


def _assert_eq(expected: Any, actual: Any, *msg: str) -> None:
    """
    Asserts that the given values match and raises an `AssertionError` with the
    given `msg`.

    Args:
        expected (Any) : The expected value
        actual (Any) : The actual value
        *msg (str) : The error message to add to the raised error
    """
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
    """
    An abstract integration test scenario.
    """

    def __init__(self, name: str, path: list[str]) -> None:
        self.name = name
        self.path = Path(".") / "action_tests" / "_files" / Path(*path)

    def get_changed_files(self, repo: TestRepository) -> list[str]:
        """
        Retrieves a list of files marked as changed in the build commit.

        Args:
            repo (TestRepository) : The test repository that defines the
                                    working directory

        Returns:
            (list[str]) A list of all changed files (all relative to the local
            repository)
        """
        log = git(
            "log",
            "--name-only",
            "--pretty=",
            "HEAD~1..HEAD",
            check=True,
            cwd=repo.local_path,
        )
        return log.stdout.strip().split("\n")

    def assert_is_file(self, repo: TestRepository, *path: str) -> None:
        """
        Asserts that the given file exists.

        Args:
            repo (TestRepository) : The test repository that defines the
                                    working directory
            *path (str) : The (relative) path to the target file
        """
        file_path = repo.local_path.joinpath(*path)
        _assert(
            file_path.is_file(),
            "File does not exist or is not a regular file:",
            str(file_path),
        )

    def assert_is_no_file(self, repo: TestRepository, *path: str) -> None:
        """
        Asserts that the given file does not exist.

        Args:
            repo (TestRepository) : The test repository that defines the
                                    working directory
            *path (str) : The (relative) path to the target file
        """
        file_path = repo.local_path.joinpath(*path)
        _assert(
            not file_path.is_file(),
            "File does exist but shouldn't:",
            str(file_path),
        )

    def get_oneline_log(self, repo: TestRepository) -> str:
        """
        Retrieves the git log output for the current repository in --oneline
        format and using the pattern '%cn:%ce:%s'.

        Args:
            repo (TestRepository) : The test repository that defines the
                                    working directory

        Returns:
            (str) The log output
        """
        return git(
            "log",
            "--oneline",
            r"--format=%cn:%ce:%s",
            check=True,
            cwd=repo.local_path,
        ).stdout.strip()

    def assert_bot_commit(
        self, repo: TestRepository, *changed_files: list[str]
    ) -> None:
        """
        Asserts that a bot commit happened and verifies the commit messages
        and commiters.

        Args:
            repo (TestRepository) : The test repository that defines the
                                    working directory
            *changed_files (list[str]) : The list of changed files (paths
                                         relative to the local repository)
        """
        log = self.get_oneline_log(repo)
        print(f"git commit log:\n'{log}'")
        lines = log.split("\n")
        _assert_eq(2, len(lines), "Unexpected number of commits")
        bot_commit, initial_commit = lines

        _check_commit(initial_commit, DEFAULT_USER, DEFAULT_EMAIL)
        _check_commit(bot_commit, BOT_NAME, BOT_EMAIL, BOT_COMMIT_MSG)

        actual_changes = set(self.get_changed_files(repo))

        expected_changes = {"/".join(path) for path in changed_files}

        missing_changed = expected_changes.difference(actual_changes)

        error_msg: str = ""

        if len(missing_changed) != 0:
            error_msg += (
                "\nThe following files should have been modified:\n"
                f"{'\n'.join(missing_changed)}"
            )

        unexpectedly_modified = actual_changes.difference(expected_changes)

        if len(unexpectedly_modified) != 0:
            error_msg += (
                "\nThe following files should not have been modified:"
                f"\n{'\n'.join(unexpectedly_modified)}"
            )

        if error_msg != "":
            raise AssertionError(f"Invalid changed files:{error_msg}")

    def assert_no_bot_commit(self, repo: TestRepository) -> None:
        """
        Asserts that no bot commit happened.

        Args:
            repo (TestRepository) : The test repository that defines the
                                    working directory
        """
        log = self.get_oneline_log(repo)
        print(f"git commit log:\n'{log}'")
        lines = log.split("\n")
        _assert_eq(1, len(lines), "Unexpected number of commits")
        _check_commit(lines[0], DEFAULT_USER, DEFAULT_EMAIL)

    def assert_action_result(self, expected_result: str) -> None:
        """
        Asserts that the action produced the given result.

        Args:
            expected_result (str) : The expected result
        """
        github_output = os.getenv("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "r", encoding="UTF-8") as f:
                lines = f.read().split("\n")
                variables = [
                    line.removeprefix("changed-exercises=")
                    for line in lines
                    if line.startswith("changed-exercises=")
                ]
                print(f"action outputs:'{'\n'.join(lines)}'\n")
                print(f"action output variables:'{variables}'\n")
                last_result = variables[-1]
                _assert_eq(expected_result, last_result, "Invalid action result")

    @abstractmethod
    def verify(self, repo: TestRepository) -> None:
        """
        Verifies this test scenario by checking the commits and files.

        Args:
            repo (TestRepository) : The test repository that defines the
                                    working directory
        """


#### OLD BUILD SYSTEM ####


class OldBuildWorkingNoChecksum(Scenario):
    """
    Integration test scenario that checks that there is always a rebuild if the
    checksum file does not exist.
    """

    def __init__(self) -> None:
        super().__init__(
            "old_build_working_no_checksum",
            ["old_build_system", "working_build_no_checksum"],
        )

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        new_files = [
            ["22W", "Ex01", ".checksum"],
            ["22W", "Ex01", "Aufgabe", "Ex01.pdf"],
            ["22W", "Ex01", "Aufgabe", "Ex01.build_log"],
            ["22W", "Ex01", "Aufgabe", "Ex01_solution.pdf"],
            ["22W", "Ex01", "Aufgabe", "Ex01_solution.build_log"],
            ["22W", "Ex01", "Unterricht", "Ex01_Lernziele.pdf"],
            ["22W", "Ex01", "Unterricht", "Ex01_Lernziele.build_log"],
        ]

        self.assert_bot_commit(repo, *new_files)

        for f in new_files:
            self.assert_is_file(repo, *f)

        self.assert_action_result("Ex01")


class OldBuildWorkingSameChecksum(Scenario):
    """
    Integration test scenario that checks that there is no build when the
    checksum matches and all PDFs exist.
    """

    def __init__(self) -> None:
        super().__init__(
            "old_build_working_same_checksum",
            ["old_build_system", "working_build_same_checksum"],
        )

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        self.assert_no_bot_commit(repo)

        self.assert_action_result("")


class OldBuildWorkingSameChecksumNoPDF(Scenario):
    """
    Integration test scenario that checks that even a valid checksum to a
    missing PDF causes a build.
    """

    def __init__(self) -> None:
        super().__init__(
            "old_build_working_same_checksum_no_pdf",
            ["old_build_system", "working_build_same_checksum_no_pdf"],
        )

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        modified_files = [
            ["22W", "Ex03", "Aufgabe", "Ex03.pdf"],
            ["22W", "Ex03", "Aufgabe", "Ex03.build_log"],
            ["22W", "Ex03", "Aufgabe", "Ex03_solution.pdf"],
            ["22W", "Ex03", "Aufgabe", "Ex03_solution.build_log"],
        ]

        existing_files = [
            ["22W", "Ex03", ".checksum"],
            ["22W", "Ex03", "Unterricht", "Ex03_Lernziele.pdf"],
        ]

        self.assert_bot_commit(repo, *modified_files)

        for f in modified_files + existing_files:
            self.assert_is_file(repo, *f)

        self.assert_action_result("Ex03")


class OldBuildWorkingWrongCheckSum(Scenario):
    """
    Integration test scenario that checks that an invalid checksum causes a
    rebuild.
    """

    def __init__(self) -> None:
        super().__init__(
            "old_build_working_wrong_checksum",
            ["old_build_system", "working_build_wrong_checksum"],
        )

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        modified_files = [
            ["22W", "Ex04", ".checksum"],
            ["22W", "Ex04", "Aufgabe", "Ex04.pdf"],
            ["22W", "Ex04", "Aufgabe", "Ex04.build_log"],
            ["22W", "Ex04", "Aufgabe", "Ex04_solution.pdf"],
            ["22W", "Ex04", "Aufgabe", "Ex04_solution.build_log"],
            ["22W", "Ex04", "Unterricht", "Ex04_Lernziele.pdf"],
            ["22W", "Ex04", "Unterricht", "Ex04_Lernziele.build_log"],
        ]

        self.assert_bot_commit(repo, *modified_files)

        for f in modified_files:
            self.assert_is_file(repo, *f)

        self.assert_action_result("Ex04")


#### NEW BUILD SYSTEM ####


_add_scenario(OldBuildWorkingNoChecksum())
_add_scenario(OldBuildWorkingSameChecksum())
_add_scenario(OldBuildWorkingSameChecksumNoPDF())
_add_scenario(OldBuildWorkingWrongCheckSum())
