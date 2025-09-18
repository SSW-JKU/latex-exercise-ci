"""
Defines various integration test scenarios and their verification steps.
"""

from action_tests.scenario import Scenario, ScenarioManager, assert_eq, check_commit

from .test_repository import DEFAULT_EMAIL, DEFAULT_USER, TestRepository, git

BOT_NAME = "Integration Test Build[bot]"
BOT_EMAIL = "integration-test-bot@users.noreply.github.com"
BOT_COMMIT_MSG = "Build TEX files"

SUCCESS_OUTCOME = "success"
FAILURE_OUTCOME = "failure"


class BuildTestScenario(Scenario):
    """
    Abstract base class for all build action integration test scenarios.
    """

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
        lines = log.split("\n")
        assert_eq(2, len(lines), "Unexpected number of commits")
        bot_commit, initial_commit = lines

        check_commit(initial_commit, DEFAULT_USER, DEFAULT_EMAIL)
        check_commit(bot_commit, BOT_NAME, BOT_EMAIL, BOT_COMMIT_MSG)

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
        lines = log.split("\n")
        assert_eq(1, len(lines), "Unexpected number of commits")
        check_commit(lines[0], DEFAULT_USER, DEFAULT_EMAIL)


#### OLD BUILD SYSTEM ####


class OldBuildSuccessNoChecksum(BuildTestScenario):
    """
    Integration test scenario that checks that there is always a rebuild if the
    checksum file does not exist.
    """

    def __init__(self) -> None:
        super().__init__("old_build_success_no_checksum", SUCCESS_OUTCOME)

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
        self.assert_files_exist(repo, *new_files)


class OldBuildSuccessSameChecksum(BuildTestScenario):
    """
    Integration test scenario that checks that there is no build when the
    checksum matches and all PDFs exist.
    """

    def __init__(self) -> None:
        super().__init__("old_build_success_same_checksum", SUCCESS_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")
        self.assert_no_bot_commit(repo)


class OldBuildSuccessSameChecksumNoPDF(BuildTestScenario):
    """
    Integration test scenario that checks that even a valid checksum with some
    PDFs missing does not trigger a rebuild.
    """

    def __init__(self) -> None:
        super().__init__("old_build_success_same_checksum_no_pdf", SUCCESS_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")
        self.assert_no_bot_commit(repo)

        self.assert_files_missing(
            repo,
            ["22W", "Ex03", "Aufgabe", "Ex03.pdf"],
            ["22W", "Ex03", "Aufgabe", "Ex03.build_log"],
            ["22W", "Ex03", "Aufgabe", "Ex03_solution.pdf"],
            ["22W", "Ex03", "Aufgabe", "Ex03_solution.build_log"],
            ["22W", "Ex03", "Unterricht", "Ex03_Lernziele.build_log"],
        )


class OldBuildSuccessWrongCheckSum(BuildTestScenario):
    """
    Integration test scenario that checks that an invalid checksum causes a
    rebuild.
    """

    def __init__(self) -> None:
        super().__init__("old_build_success_wrong_checksum", SUCCESS_OUTCOME)

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
        self.assert_files_exist(repo, *modified_files)


class OldBuildFailureNewFile(BuildTestScenario):
    """
    Integration test scenario that checks that the checksum is not updated
    if the build fails on a new file.
    """

    def __init__(self) -> None:
        super().__init__("old_build_failure_new_file", FAILURE_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        modified_files = [
            ["22W", "Ex03", "Aufgabe", "Ex03.build_log"],
            ["22W", "Ex03", "Aufgabe", "Ex03_solution.build_log"],
            ["22W", "Ex03", "Unterricht", "Ex03_Lernziele.pdf"],
            ["22W", "Ex03", "Unterricht", "Ex03_Lernziele.build_log"],
        ]

        self.assert_bot_commit(repo, *modified_files)

        self.assert_files_exist(repo, *modified_files)

        self.assert_files_missing(
            repo,
            ["22W", "Ex03", "Aufgabe", "Ex03.pdf"],
            ["22W", "Ex03", "Aufgabe", "Ex03_solution.pdf"],
        )


class OldBuildFailureNoChecksum(BuildTestScenario):
    """
    Integration test scenario that checks that there is no checksum file created
    if a build (partially) fails and no checksum file existed before.
    """

    def __init__(self) -> None:
        super().__init__("old_build_failure_no_checksum", FAILURE_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        modified_files = [
            ["22W", "Ex01", "Aufgabe", "Ex01.build_log"],
            ["22W", "Ex01", "Aufgabe", "Ex01_solution.build_log"],
            ["22W", "Ex01", "Unterricht", "Ex01_Lernziele.build_log"],
            ["22W", "Ex02", ".checksum"],
            ["22W", "Ex02", "Aufgabe", "Ex02.pdf"],
            ["22W", "Ex02", "Aufgabe", "Ex02.build_log"],
            ["22W", "Ex02", "Aufgabe", "Ex02_solution.pdf"],
            ["22W", "Ex02", "Aufgabe", "Ex02_solution.build_log"],
            ["22W", "Ex02", "Unterricht", "Ex02_Lernziele.pdf"],
            ["22W", "Ex02", "Unterricht", "Ex02_Lernziele.build_log"],
        ]

        self.assert_bot_commit(repo, *modified_files)

        self.assert_files_exist(repo, *modified_files)

        self.assert_files_missing(
            repo,
            ["22W", "Ex01", ".checksum"],
            ["22W", "Ex01", "Aufgabe", "Ex01.pdf"],
            ["22W", "Ex01", "Aufgabe", "Ex01_solution.pdf"],
            ["22W", "Ex01", "Unterricht", "Ex01_Lernziele.pdf"],
        )


class OldBuildFailureUpdateFile(BuildTestScenario):
    """
    Integration test scenario that checks that the checksum file is not updated
    if a build (partially) fails due to a file update.
    """

    def __init__(self) -> None:
        super().__init__("old_build_failure_update_file", FAILURE_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        new_files = [
            ["22W", "Ex01", "Aufgabe", "Ex01.pdf"],
            ["22W", "Ex01", "Aufgabe", "Ex01.build_log"],
            ["22W", "Ex01", "Aufgabe", "Ex01_solution.build_log"],
            ["22W", "Ex01", "Unterricht", "Ex01_Lernziele.build_log"],
        ]

        deleted_files = [
            ["22W", "Ex01", "Aufgabe", "Ex01_solution.pdf"],
            ["22W", "Ex01", "Unterricht", "Ex01_Lernziele.pdf"],
        ]

        self.assert_bot_commit(repo, *new_files, *deleted_files)

        self.assert_files_exist(repo, *new_files)
        self.assert_files_missing(repo, *deleted_files)


#### NEW BUILD SYSTEM ####


class NewBuildSuccessNoChecksum(BuildTestScenario):
    """
    Integration test scenario that checks that there is always a rebuild if the
    checksum file does not exist.
    """

    def __init__(self) -> None:
        super().__init__("new_build_success_no_checksum", SUCCESS_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        new_files = [
            ["25ST", "Ex01", ".checksum"],
            ["25ST", "Ex01", "Aufgabe", "Ex01.pdf"],
            ["25ST", "Ex01", "Aufgabe", "Ex01.build_log"],
            ["25ST", "Ex01", "Aufgabe", "Ex01_solution.pdf"],
            ["25ST", "Ex01", "Aufgabe", "Ex01_solution.build_log"],
            ["25ST", "Ex01", "Unterricht", "Ex01_Lernziele.pdf"],
            ["25ST", "Ex01", "Unterricht", "Ex01_Lernziele.build_log"],
        ]

        self.assert_bot_commit(repo, *new_files)
        self.assert_files_exist(repo, *new_files)


class NewBuildSuccessSameChecksum(BuildTestScenario):
    """
    Integration test scenario that checks that there is no build when the
    checksum matches and all PDFs exist.
    """

    def __init__(self) -> None:
        super().__init__("new_build_success_same_checksum", SUCCESS_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")
        self.assert_no_bot_commit(repo)


class NewBuildSuccessSameChecksumNoPDF(BuildTestScenario):
    """
    Integration test scenario that checks that even a valid checksum with some
    PDFs missing does not trigger a rebuild.
    """

    def __init__(self) -> None:
        super().__init__("new_build_success_same_checksum_no_pdf", SUCCESS_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")
        self.assert_no_bot_commit(repo)

        self.assert_files_missing(
            repo,
            ["25ST", "Ex03", "Aufgabe", "Ex03.pdf"],
            ["25ST", "Ex03", "Aufgabe", "Ex03.build_log"],
            ["25ST", "Ex03", "Aufgabe", "Ex03_solution.pdf"],
            ["25ST", "Ex03", "Aufgabe", "Ex03_solution.build_log"],
            ["25ST", "Ex03", "Unterricht", "Ex03_Lernziele.build_log"],
        )


class NewBuildSuccessWrongCheckSum(BuildTestScenario):
    """
    Integration test scenario that checks that an invalid checksum causes a
    rebuild.
    """

    def __init__(self) -> None:
        super().__init__("new_build_success_wrong_checksum", SUCCESS_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        modified_files = [
            ["25ST", "Ex04", ".checksum"],
            ["25ST", "Ex04", "Aufgabe", "Ex04.pdf"],
            ["25ST", "Ex04", "Aufgabe", "Ex04.build_log"],
            ["25ST", "Ex04", "Aufgabe", "Ex04_solution.pdf"],
            ["25ST", "Ex04", "Aufgabe", "Ex04_solution.build_log"],
            ["25ST", "Ex04", "Unterricht", "Ex04_Lernziele.pdf"],
            ["25ST", "Ex04", "Unterricht", "Ex04_Lernziele.build_log"],
        ]

        self.assert_bot_commit(repo, *modified_files)
        self.assert_files_exist(repo, *modified_files)


class NewBuildFailureNewFile(BuildTestScenario):
    """
    Integration test scenario that checks that the checksum is not updated
    if the build fails on a new file.
    """

    def __init__(self) -> None:
        super().__init__("new_build_failure_new_file", FAILURE_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        modified_files = [
            ["25ST", "Ex03", "Aufgabe", "Ex03.build_log"],
            ["25ST", "Ex03", "Aufgabe", "Ex03_solution.build_log"],
            ["25ST", "Ex03", "Unterricht", "Ex03_Lernziele.pdf"],
            ["25ST", "Ex03", "Unterricht", "Ex03_Lernziele.build_log"],
        ]

        self.assert_bot_commit(repo, *modified_files)

        self.assert_files_exist(repo, *modified_files)

        self.assert_files_missing(
            repo,
            ["25ST", "Ex03", "Aufgabe", "Ex03.pdf"],
            ["25ST", "Ex03", "Aufgabe", "Ex03_solution.pdf"],
        )


class NewBuildFailureNoChecksum(BuildTestScenario):
    """
    Integration test scenario that checks that there is no checksum file created
    if a build (partially) fails and no checksum file existed before.
    """

    def __init__(self) -> None:
        super().__init__("new_build_failure_no_checksum", FAILURE_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        modified_files = [
            ["25ST", "Ex01", "Aufgabe", "Ex01.build_log"],
            ["25ST", "Ex01", "Aufgabe", "Ex01_solution.build_log"],
            ["25ST", "Ex01", "Unterricht", "Ex01_Lernziele.build_log"],
            ["25ST", "Ex02", ".checksum"],
            ["25ST", "Ex02", "Aufgabe", "Ex02.pdf"],
            ["25ST", "Ex02", "Aufgabe", "Ex02.build_log"],
            ["25ST", "Ex02", "Aufgabe", "Ex02_solution.pdf"],
            ["25ST", "Ex02", "Aufgabe", "Ex02_solution.build_log"],
            ["25ST", "Ex02", "Unterricht", "Ex02_Lernziele.pdf"],
            ["25ST", "Ex02", "Unterricht", "Ex02_Lernziele.build_log"],
        ]

        self.assert_bot_commit(repo, *modified_files)

        self.assert_files_exist(repo, *modified_files)

        self.assert_files_missing(
            repo,
            ["25ST", "Ex01", ".checksum"],
            ["25ST", "Ex01", "Aufgabe", "Ex01.pdf"],
            ["25ST", "Ex01", "Aufgabe", "Ex01_solution.pdf"],
            ["25ST", "Ex01", "Unterricht", "Ex01_Lernziele.pdf"],
        )


class NewBuildFailureUpdateFile(BuildTestScenario):
    """
    Integration test scenario that checks that the checksum file is not updated
    if a build (partially) fails due to a file update.
    """

    def __init__(self) -> None:
        super().__init__("new_build_failure_update_file", FAILURE_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")

        new_files = [
            ["25ST", "Ex01", "Aufgabe", "Ex01.pdf"],
            ["25ST", "Ex01", "Aufgabe", "Ex01.build_log"],
            ["25ST", "Ex01", "Aufgabe", "Ex01_solution.build_log"],
            ["25ST", "Ex01", "Unterricht", "Ex01_Lernziele.build_log"],
        ]

        deleted_files = [
            ["25ST", "Ex01", "Aufgabe", "Ex01_solution.pdf"],
            ["25ST", "Ex01", "Unterricht", "Ex01_Lernziele.pdf"],
        ]

        self.assert_bot_commit(repo, *new_files, *deleted_files)

        self.assert_files_exist(repo, *new_files)
        self.assert_files_missing(repo, *deleted_files)


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
