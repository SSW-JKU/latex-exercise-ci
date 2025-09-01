"""
Creates local repository pairings for integration tests.
WARNING: This file is only intended for testing and should not be executed or
imported in other contexts!
"""

# import argparse
from pathlib import Path
from random import choice
import subprocess
from typing import Optional

REMOTE_PATH = Path("/tmp/test-remotes")
LOCAL_PATH = Path("/tmp/test-locals")
DEFAULT_BRANCH = "master"
DEFAULT_USER = "Test User"
DEFAULT_EMAIL = "test@user.com"


def git(
    *commands: str, check: bool = True, cwd: Optional[Path] = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *commands], capture_output=True, text=True, check=check, cwd=cwd
    )


# def _parse_args() -> argparse.Namespace:
#     parser = argparse.ArgumentParser(
#         description="Setup test git repositories for integration tests."
#     )
#     parser.add_argument(
#         "id",
#         type=str,
#         help="Identifier for the repository pair that is used as a"\
#              "relative path from the base path for each repository.",
#     )
#     parser.add_argument(
#         "--remote-path",
#         type=Path,
#         default=REMOTE_PATH,
#         help="Base path of the test remote repository.",
#     )
#     parser.add_argument(
#         "--local-path",
#         type=Path,
#         default=LOCAL_PATH,
#         help="Base path of the test local repository.",
#     )

#     return parser.parse_args()


def _set_git_config(repo_dir: Path) -> None:
    git("config", "user.name", DEFAULT_USER, cwd=repo_dir)
    git("config", "user.email", DEFAULT_EMAIL, cwd=repo_dir)


def _setup_repository_path(base_path: Path, repo_id: str, exist_ok: bool) -> Path:
    repo_path = base_path / repo_id
    base_path.mkdir(parents=True, exist_ok=True)
    repo_path.mkdir(parents=False, exist_ok=exist_ok)
    return repo_path


class TestRepository:
    """
    Represents a local git repository consisting of a bare remote and a local clone.
    """

    def __init__(
        self,
        tag: str,
        remote_base_path: Path,
        local_base_path: Path,
        exist_ok: bool = True,
    ) -> None:
        self.tag = tag
        self.remote_base_path = remote_base_path
        self.local_base_path = local_base_path
        self.remote_path = _setup_repository_path(remote_base_path, tag, exist_ok)
        self.local_path = _setup_repository_path(local_base_path, tag, exist_ok)
        default_branch_config = git(
            "config", "--global", "init.defaultBranch", check=False
        )
        if default_branch_config.returncode != 0:
            raise RuntimeError(
                "Could not determine git default branch name - "
                "'git config --global init.defaultBranch' "
                "returned non-zero exit code.\n"
                f"STDOUT={default_branch_config.stdout}\n"
                f"STDERR={default_branch_config.stderr}"
            )
        default_branch = default_branch_config.stdout.strip()
        self.default_branch = default_branch if default_branch else DEFAULT_BRANCH

    def initialize_repo(self) -> None:
        print(git("init", "--bare", cwd=self.remote_path).stdout)
        print(git("clone", str(self.remote_path), ".", cwd=self.local_path).stdout)
        _set_git_config(self.local_path)

    def commit_all(self, message: Optional[str] = None) -> None:
        if message is None:
            message = "".join(choice("abcdefghijklmnopqrstuvwxyz") for _ in range(8))

        git("add", ".", cwd=self.local_path)
        git("commit", "-am", message, cwd=self.local_path)

    def push(self) -> None:
        git("push", "origin", self.default_branch, cwd=self.local_path)
