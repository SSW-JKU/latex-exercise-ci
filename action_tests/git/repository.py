"""Create local repository pairings for integration tests.

WARNING: This file is only intended for testing and should not be executed or
imported in other contexts.
"""

import logging
from pathlib import Path

from .commands import git, set_git_config
from .utils import generate_secure_string

log = logging.getLogger(__name__)

DEFAULT_BRANCH = "main"
DEFAULT_USER = "Test User"
DEFAULT_EMAIL = "test@user.com"


def _setup_repository_path(repo_path: Path) -> None:
    """Ensure that the given repository directory and its parent - the base directory of all test repositories - exist.

    Args:
        repo_path (Path) : The path to the repository (must be a subdirectory
                           of the base path).

    """
    base_path = repo_path.parent
    base_path.mkdir(parents=True, exist_ok=True)
    repo_path.mkdir(parents=False, exist_ok=False)


class TestRepository:
    """Represents a local git repository consisting of a bare remote and a local clone."""

    def __init__(
        self,
        tag: str,
        remote_base_path: Path,
        local_base_path: Path,
        default_branch: str = DEFAULT_BRANCH,
    ) -> None:
        """Initialize a new test repository.

        Args:
            tag (str) : The tag that identifies the repository
            remote_base_path (Path) : The base path of the remote repository
            local_base_path (Path) : The base path of the local repository
            default_branch (str, default: DEFAULT_BRANCH) : The default branch name of the repository

        """
        self.tag = tag
        self.remote_path = remote_base_path / tag
        self.local_path = local_base_path / tag
        # ignore return code of this command as it may fail if config option is not set
        config_default_branch = git("config", "--global", "init.defaultBranch", check=False).stdout.strip()
        self.default_branch = config_default_branch or default_branch

    def initialize_repo(self, default_user: str = DEFAULT_USER, default_email: str = DEFAULT_EMAIL) -> None:
        """Initialize the remote and the local clone of the test repository.

        Args:
            default_user (str, default: DEFAULT_USER) : The default user name for the repository
            default_email (str, default: DEFAULT_EMAIL) : The default user email for the repository

        """
        _setup_repository_path(self.remote_path)
        _setup_repository_path(self.local_path)
        git_init = git("init", "--bare", cwd=self.remote_path)
        log.info(git_init.stdout)
        git_clone = git("clone", str(self.remote_path), ".", cwd=self.local_path)
        log.info(git_clone.stdout)
        set_git_config(self.local_path, default_user, default_email)

    def commit_all(self, message: str | None = None) -> None:
        """Commit all changes in the repository.

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
