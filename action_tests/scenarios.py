"""Defines various integration test scenarios and their verification steps."""

from pathlib import Path

from .asserts import assert_eq, assert_files_exist, assert_files_missing
from .git.commands import get_changed_files, get_oneline_log
from .git.repository import DEFAULT_EMAIL, DEFAULT_USER, TestRepository
from .scenario import Scenario, check_commit
from .scenario_manager import ScenarioManager

BOT_NAME = "Integration Test Build[bot]"
BOT_EMAIL = "integration-test-bot@users.noreply.github.com"
BOT_COMMIT_MSG = "Build TEX files"

SUCCESS_OUTCOME = "success"
FAILURE_OUTCOME = "failure"


class BuildTestScenario(Scenario):
    """Abstract base class for all build action integration test scenarios."""

    def assert_bot_commit(self, repo: TestRepository, *changed_files: Path) -> None:
        """Asserts that a bot commit happened and verifies the commit messages
        and commiters.

        Args:
            repo (TestRepository) : The test repository that defines the
                                    working directory
            *changed_files (Path) : The list of changed files (paths
                                          relative to the local repository)

        """
        log = get_oneline_log(repo.local_path)
        lines = log.split("\n")
        assert_eq(2, len(lines), "Unexpected number of commits")
        bot_commit, initial_commit = lines

        check_commit(initial_commit, DEFAULT_USER, DEFAULT_EMAIL)
        check_commit(bot_commit, BOT_NAME, BOT_EMAIL, BOT_COMMIT_MSG)

        actual_changes = set(get_changed_files(repo.local_path))

        expected_changes = {str(path) for path in changed_files}

        missing_changed = expected_changes.difference(actual_changes)

        error_msg: str = ""

        if len(missing_changed) != 0:
            error_msg += f"\nThe following files should have been modified:\n{'\n'.join(missing_changed)}"

        unexpectedly_modified = actual_changes.difference(expected_changes)

        if len(unexpectedly_modified) != 0:
            error_msg += f"\nThe following files should not have been modified:\n{'\n'.join(unexpectedly_modified)}"

        if error_msg != "":
            msg = f"Invalid changed files:{error_msg}"
            raise AssertionError(msg)

    def assert_no_bot_commit(self, repo: TestRepository) -> None:
        """Asserts that no bot commit happened.

        Args:
            repo (TestRepository) : The test repository that defines the
                                    working directory

        """
        log = get_oneline_log(repo.local_path)
        lines = log.split("\n")
        assert_eq(1, len(lines), "Unexpected number of commits")
        check_commit(lines[0], DEFAULT_USER, DEFAULT_EMAIL)


#### OLD BUILD SYSTEM ####


class OldBuildSuccessNoChecksum(BuildTestScenario):
    """Integration test scenario that checks that there is always a rebuild if the
    checksum file does not exist.
    """

    def __init__(self) -> None:
        super().__init__("old_build_success_no_checksum", SUCCESS_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        new_files = [
            Path("22W", "Ex01", ".checksum"),
            Path("22W", "Ex01", "Aufgabe", "Ex01.pdf"),
            Path("22W", "Ex01", "Aufgabe", "Ex01.build_log"),
            Path("22W", "Ex01", "Aufgabe", "Ex01_solution.pdf"),
            Path("22W", "Ex01", "Aufgabe", "Ex01_solution.build_log"),
            Path("22W", "Ex01", "Unterricht", "Ex01_Lernziele.pdf"),
            Path("22W", "Ex01", "Unterricht", "Ex01_Lernziele.build_log"),
        ]

        self.assert_bot_commit(repo, *new_files)
        assert_files_exist(repo.local_path, *new_files)


class OldBuildSuccessSameChecksum(BuildTestScenario):
    """Integration test scenario that checks that there is no build when the
    checksum matches and all PDFs exist.
    """

    def __init__(self) -> None:
        super().__init__("old_build_success_same_checksum", SUCCESS_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")
        self.assert_no_bot_commit(repo)


class OldBuildSuccessSameChecksumNoPDF(BuildTestScenario):
    """Integration test scenario that checks that even a valid checksum with some
    PDFs missing does not trigger a rebuild.
    """

    def __init__(self) -> None:
        super().__init__("old_build_success_same_checksum_no_pdf", SUCCESS_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")
        self.assert_no_bot_commit(repo)

        assert_files_missing(
            repo.local_path,
            Path("22W", "Ex03", "Aufgabe", "Ex03.pdf"),
            Path("22W", "Ex03", "Aufgabe", "Ex03.build_log"),
            Path("22W", "Ex03", "Aufgabe", "Ex03_solution.pdf"),
            Path("22W", "Ex03", "Aufgabe", "Ex03_solution.build_log"),
            Path("22W", "Ex03", "Unterricht", "Ex03_Lernziele.build_log"),
        )


class OldBuildSuccessWrongCheckSum(BuildTestScenario):
    """Integration test scenario that checks that an invalid checksum causes a
    rebuild.
    """

    def __init__(self) -> None:
        super().__init__("old_build_success_wrong_checksum", SUCCESS_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        modified_files = [
            Path("22W", "Ex04", ".checksum"),
            Path("22W", "Ex04", "Aufgabe", "Ex04.pdf"),
            Path("22W", "Ex04", "Aufgabe", "Ex04.build_log"),
            Path("22W", "Ex04", "Aufgabe", "Ex04_solution.pdf"),
            Path("22W", "Ex04", "Aufgabe", "Ex04_solution.build_log"),
            Path("22W", "Ex04", "Unterricht", "Ex04_Lernziele.pdf"),
            Path("22W", "Ex04", "Unterricht", "Ex04_Lernziele.build_log"),
        ]

        self.assert_bot_commit(repo, *modified_files)
        assert_files_exist(repo.local_path, *modified_files)


class OldBuildFailureNewFile(BuildTestScenario):
    """Integration test scenario that checks that the checksum is not updated
    if the build fails on a new file.
    """

    def __init__(self) -> None:
        super().__init__("old_build_failure_new_file", FAILURE_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        modified_files = [
            Path("22W", "Ex03", "Aufgabe", "Ex03.build_log"),
            Path("22W", "Ex03", "Aufgabe", "Ex03_solution.build_log"),
            Path("22W", "Ex03", "Unterricht", "Ex03_Lernziele.pdf"),
            Path("22W", "Ex03", "Unterricht", "Ex03_Lernziele.build_log"),
        ]

        self.assert_bot_commit(repo, *modified_files)

        assert_files_exist(repo.local_path, *modified_files)

        assert_files_missing(
            repo.local_path,
            Path("22W", "Ex03", "Aufgabe", "Ex03.pdf"),
            Path("22W", "Ex03", "Aufgabe", "Ex03_solution.pdf"),
        )


class OldBuildFailureNoChecksum(BuildTestScenario):
    """Integration test scenario that checks that there is no checksum file created
    if a build (partially) fails and no checksum file existed before.
    """

    def __init__(self) -> None:
        super().__init__("old_build_failure_no_checksum", FAILURE_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        modified_files = [
            Path("22W", "Ex01", "Aufgabe", "Ex01.build_log"),
            Path("22W", "Ex01", "Aufgabe", "Ex01_solution.build_log"),
            Path("22W", "Ex01", "Unterricht", "Ex01_Lernziele.build_log"),
            Path("22W", "Ex02", ".checksum"),
            Path("22W", "Ex02", "Aufgabe", "Ex02.pdf"),
            Path("22W", "Ex02", "Aufgabe", "Ex02.build_log"),
            Path("22W", "Ex02", "Aufgabe", "Ex02_solution.pdf"),
            Path("22W", "Ex02", "Aufgabe", "Ex02_solution.build_log"),
            Path("22W", "Ex02", "Unterricht", "Ex02_Lernziele.pdf"),
            Path("22W", "Ex02", "Unterricht", "Ex02_Lernziele.build_log"),
        ]

        self.assert_bot_commit(repo, *modified_files)

        assert_files_exist(repo.local_path, *modified_files)

        assert_files_missing(
            repo.local_path,
            Path("22W", "Ex01", ".checksum"),
            Path("22W", "Ex01", "Aufgabe", "Ex01.pdf"),
            Path("22W", "Ex01", "Aufgabe", "Ex01_solution.pdf"),
            Path("22W", "Ex01", "Unterricht", "Ex01_Lernziele.pdf"),
        )


class OldBuildFailureUpdateFile(BuildTestScenario):
    """Integration test scenario that checks that the checksum file is not updated
    if a build (partially) fails due to a file update.
    """

    def __init__(self) -> None:
        super().__init__("old_build_failure_update_file", FAILURE_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        new_files = [
            Path("22W", "Ex01", "Aufgabe", "Ex01.pdf"),
            Path("22W", "Ex01", "Aufgabe", "Ex01.build_log"),
            Path("22W", "Ex01", "Aufgabe", "Ex01_solution.build_log"),
            Path("22W", "Ex01", "Unterricht", "Ex01_Lernziele.build_log"),
        ]

        deleted_files = [
            Path("22W", "Ex01", "Aufgabe", "Ex01_solution.pdf"),
            Path("22W", "Ex01", "Unterricht", "Ex01_Lernziele.pdf"),
        ]

        self.assert_bot_commit(repo, *new_files, *deleted_files)

        assert_files_exist(repo.local_path, *new_files)
        assert_files_missing(repo.local_path, *deleted_files)


#### NEW BUILD SYSTEM ####


class NewBuildSuccessNoChecksum(BuildTestScenario):
    """Integration test scenario that checks that there is always a rebuild if the
    checksum file does not exist.
    """

    def __init__(self) -> None:
        super().__init__("new_build_success_no_checksum", SUCCESS_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        new_files = [
            Path("25ST", "Ex01", ".checksum"),
            Path("25ST", "Ex01", "Aufgabe", "Ex01.pdf"),
            Path("25ST", "Ex01", "Aufgabe", "Ex01.build_log"),
            Path("25ST", "Ex01", "Aufgabe", "Ex01_solution.pdf"),
            Path("25ST", "Ex01", "Aufgabe", "Ex01_solution.build_log"),
            Path("25ST", "Ex01", "Unterricht", "Ex01_Lernziele.pdf"),
            Path("25ST", "Ex01", "Unterricht", "Ex01_Lernziele.build_log"),
        ]

        self.assert_bot_commit(repo, *new_files)
        assert_files_exist(repo.local_path, *new_files)


class NewBuildSuccessSameChecksum(BuildTestScenario):
    """Integration test scenario that checks that there is no build when the
    checksum matches and all PDFs exist.
    """

    def __init__(self) -> None:
        super().__init__("new_build_success_same_checksum", SUCCESS_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")
        self.assert_no_bot_commit(repo)


class NewBuildSuccessSameChecksumNoPDF(BuildTestScenario):
    """Integration test scenario that checks that even a valid checksum with some
    PDFs missing does not trigger a rebuild.
    """

    def __init__(self) -> None:
        super().__init__("new_build_success_same_checksum_no_pdf", SUCCESS_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")
        self.assert_no_bot_commit(repo)

        assert_files_missing(
            repo.local_path,
            Path("25ST", "Ex03", "Aufgabe", "Ex03.pdf"),
            Path("25ST", "Ex03", "Aufgabe", "Ex03.build_log"),
            Path("25ST", "Ex03", "Aufgabe", "Ex03_solution.pdf"),
            Path("25ST", "Ex03", "Aufgabe", "Ex03_solution.build_log"),
            Path("25ST", "Ex03", "Unterricht", "Ex03_Lernziele.build_log"),
        )


class NewBuildSuccessWrongCheckSum(BuildTestScenario):
    """Integration test scenario that checks that an invalid checksum causes a
    rebuild.
    """

    def __init__(self) -> None:
        super().__init__("new_build_success_wrong_checksum", SUCCESS_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        modified_files = [
            Path("25ST", "Ex04", ".checksum"),
            Path("25ST", "Ex04", "Aufgabe", "Ex04.pdf"),
            Path("25ST", "Ex04", "Aufgabe", "Ex04.build_log"),
            Path("25ST", "Ex04", "Aufgabe", "Ex04_solution.pdf"),
            Path("25ST", "Ex04", "Aufgabe", "Ex04_solution.build_log"),
            Path("25ST", "Ex04", "Unterricht", "Ex04_Lernziele.pdf"),
            Path("25ST", "Ex04", "Unterricht", "Ex04_Lernziele.build_log"),
        ]

        self.assert_bot_commit(repo, *modified_files)
        assert_files_exist(repo.local_path, *modified_files)


class NewBuildFailureNewFile(BuildTestScenario):
    """Integration test scenario that checks that the checksum is not updated
    if the build fails on a new file.
    """

    def __init__(self) -> None:
        super().__init__("new_build_failure_new_file", FAILURE_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        modified_files = [
            Path("25ST", "Ex03", "Aufgabe", "Ex03.build_log"),
            Path("25ST", "Ex03", "Aufgabe", "Ex03_solution.build_log"),
            Path("25ST", "Ex03", "Unterricht", "Ex03_Lernziele.pdf"),
            Path("25ST", "Ex03", "Unterricht", "Ex03_Lernziele.build_log"),
        ]

        self.assert_bot_commit(repo, *modified_files)

        assert_files_exist(repo.local_path, *modified_files)

        assert_files_missing(
            repo.local_path,
            Path("25ST", "Ex03", "Aufgabe", "Ex03.pdf"),
            Path("25ST", "Ex03", "Aufgabe", "Ex03_solution.pdf"),
        )


class NewBuildFailureNoChecksum(BuildTestScenario):
    """Integration test scenario that checks that there is no checksum file created
    if a build (partially) fails and no checksum file existed before.
    """

    def __init__(self) -> None:
        super().__init__("new_build_failure_no_checksum", FAILURE_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        modified_files = [
            Path("25ST", "Ex01", "Aufgabe", "Ex01.build_log"),
            Path("25ST", "Ex01", "Aufgabe", "Ex01_solution.build_log"),
            Path("25ST", "Ex01", "Unterricht", "Ex01_Lernziele.build_log"),
            Path("25ST", "Ex02", ".checksum"),
            Path("25ST", "Ex02", "Aufgabe", "Ex02.pdf"),
            Path("25ST", "Ex02", "Aufgabe", "Ex02.build_log"),
            Path("25ST", "Ex02", "Aufgabe", "Ex02_solution.pdf"),
            Path("25ST", "Ex02", "Aufgabe", "Ex02_solution.build_log"),
            Path("25ST", "Ex02", "Unterricht", "Ex02_Lernziele.pdf"),
            Path("25ST", "Ex02", "Unterricht", "Ex02_Lernziele.build_log"),
        ]

        self.assert_bot_commit(repo, *modified_files)

        assert_files_exist(repo.local_path, *modified_files)

        assert_files_missing(
            repo.local_path,
            Path("25ST", "Ex01", ".checksum"),
            Path("25ST", "Ex01", "Aufgabe", "Ex01.pdf"),
            Path("25ST", "Ex01", "Aufgabe", "Ex01_solution.pdf"),
            Path("25ST", "Ex01", "Unterricht", "Ex01_Lernziele.pdf"),
        )


class NewBuildFailureUpdateFile(BuildTestScenario):
    """Integration test scenario that checks that the checksum file is not updated
    if a build (partially) fails due to a file update.
    """

    def __init__(self) -> None:
        super().__init__("new_build_failure_update_file", FAILURE_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        new_files = [
            Path("25ST", "Ex01", "Aufgabe", "Ex01.pdf"),
            Path("25ST", "Ex01", "Aufgabe", "Ex01.build_log"),
            Path("25ST", "Ex01", "Aufgabe", "Ex01_solution.build_log"),
            Path("25ST", "Ex01", "Unterricht", "Ex01_Lernziele.build_log"),
        ]

        deleted_files = [
            Path("25ST", "Ex01", "Aufgabe", "Ex01_solution.pdf"),
            Path("25ST", "Ex01", "Unterricht", "Ex01_Lernziele.pdf"),
        ]

        self.assert_bot_commit(repo, *new_files, *deleted_files)

        assert_files_exist(repo.local_path, *new_files)
        assert_files_missing(repo.local_path, *deleted_files)


SCENARIOS = ScenarioManager(
    OldBuildSuccessNoChecksum(),
    OldBuildSuccessSameChecksum(),
    OldBuildSuccessSameChecksumNoPDF(),
    OldBuildSuccessWrongCheckSum(),
    OldBuildFailureNewFile(),
    OldBuildFailureNoChecksum(),
    OldBuildFailureUpdateFile(),
    NewBuildSuccessNoChecksum(),
    NewBuildSuccessSameChecksum(),
    NewBuildSuccessSameChecksumNoPDF(),
    NewBuildSuccessWrongCheckSum(),
    NewBuildFailureNewFile(),
    NewBuildFailureNoChecksum(),
    NewBuildFailureUpdateFile(),
)
