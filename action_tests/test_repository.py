#!/usr/bin/env python

"""Creates local repository pairings for integration tests.
WARNING: This file is only intended for testing and should not be executed or
imported in other contexts!
"""

import secrets
import string
import subprocess
from pathlib import Path

REMOTE_PATH = Path("/tmp/test-remotes")  # noqa: S108
LOCAL_PATH = Path("/tmp/test-locals")  # noqa: S108
DEFAULT_BRANCH = "master"
DEFAULT_USER = "Test User"
DEFAULT_EMAIL = "test@user.com"

# define the character pool (letters, digits, and punctuation)
alphabet = string.ascii_letters + string.digits + string.punctuation


def git(*commands: str, check: bool = True, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Helper to execute a git command.
    The "git" prefix is automatically prepended.

    Args:
        *commands (str) : The git commands to execute.
        check (bool, default: True) : Check that the command exited with a
                                      result code of 0
        cwd (Path | None, default: None) : The working directory in which the
                                           git command should be executed

    """
    return subprocess.run(  # noqa: S603
        ["/usr/bin/env", "git", *commands],
        capture_output=True,
        text=True,
        check=check,
        cwd=cwd,
    )


def _set_git_config(repo_dir: Path) -> None:
    """Sets git author and email configuration for the given repository.

    Args:
        repo_dir (Path) : The path to the directory.

    """
    git("config", "user.name", DEFAULT_USER, cwd=repo_dir)
    git("config", "user.email", DEFAULT_EMAIL, cwd=repo_dir)


def _setup_repository_path(base_path: Path, repo_path: Path) -> None:
    """Ensures that the base directory of all test repositories and the specific
    repository directory exist.

    Args:
        base_path (Path) : The base path of all repositories.
        repo_path (Path) : The path to the repository (must be a subdirectory
                           of `base_path`).

    """
    assert repo_path.is_relative_to(base_path), (
        f"Repository path {repo_path.absolute()} must be a subdirectory of the base path {base_path.absolute()}."
    )
    base_path.mkdir(parents=True, exist_ok=True)
    repo_path.mkdir(parents=False, exist_ok=False)


class TestRepository:
    """Represents a local git repository consisting of a bare remote and a local clone."""

    def __init__(
        self,
        tag: str,
        remote_base_path: Path,
        local_base_path: Path,
    ) -> None:
        self.tag = tag
        self.remote_base_path = remote_base_path
        self.local_base_path = local_base_path
        self.remote_path = remote_base_path / tag
        self.local_path = local_base_path / tag
        # ignore return code of this command as it may fail if config option is not set
        default_branch = git("config", "--global", "init.defaultBranch", check=False).stdout.strip()
        self.default_branch = default_branch or DEFAULT_BRANCH

    def initialize_repo(self) -> None:
        """Initializes the remote and the local clone of the test repository."""
        _setup_repository_path(self.remote_base_path, self.remote_path)
        _setup_repository_path(self.local_base_path, self.local_path)
        print(git("init", "--bare", cwd=self.remote_path).stdout)
        print(git("clone", str(self.remote_path), ".", cwd=self.local_path).stdout)
        _set_git_config(self.local_path)

    def commit_all(self, message: str | None = None) -> None:
        """Commits all changes in the repository.

        Args:
            message (str | None) : An optional commit message
                                   (otherwise a random message is generated)

        """
        if message is None:
            message = generate_secure_string()

        git("add", ".", cwd=self.local_path)
        git("commit", "-am", message, cwd=self.local_path)

    def push(self) -> None:
        """Pushes the commits to the remote."""
        git("push", "origin", self.default_branch, cwd=self.local_path)


# Generate a secure random string of length 16
def generate_secure_string() -> str:
    """Generates a secure random string of length 16 using letters, digits, and punctuation."""
    return "".join(secrets.choice(alphabet) for _ in range(16))
