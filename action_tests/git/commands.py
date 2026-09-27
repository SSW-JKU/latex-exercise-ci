"""Git command execution helper functions."""

import subprocess
from pathlib import Path

GIT_ONELINE_LOG_FMT = r"--format=%cn:%ce:%s"


def git(*commands: str, check: bool = True, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Execute a git command. The "git" prefix is automatically prepended.

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


def get_oneline_log(cwd: Path) -> str:
    """Retrieve the git log output for the given working directory.

    The log is displayed in --oneline format using the pattern '%cn:%ce:%s'.

    Args:
        cwd (Path) : The working directory

    Returns:
        (str) The log output

    """
    return git(
        "log",
        "--oneline",
        GIT_ONELINE_LOG_FMT,
        check=True,
        cwd=cwd,
    ).stdout.strip()


def get_changed_files(cwd: Path) -> list[str]:
    """Retrieve a list of files marked as changed in the build commit.

    Args:
        cwd (Path) : The working directory

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
        cwd=cwd,
    )
    return log.stdout.strip().split("\n")


def set_git_config(repo_dir: Path, user_name: str, user_email: str) -> None:
    """Set git author and email configuration for the given repository.

    Args:
        repo_dir (Path) : The path to the directory.
        user_name (str) : The name of the git user.
        user_email (str) : The email of the git user.

    """
    git("config", "user.name", user_name, cwd=repo_dir)
    git("config", "user.email", user_email, cwd=repo_dir)


def check_git_installation() -> None:
    """Verify that git is installed and available in the PATH.

    Successfully returns if git is installed and available in the PATH,
    otherwise raises an OSError.
    """
    try:
        git("--version")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        msg = "Git is not installed or not found in PATH."
        raise OSError(msg) from e
