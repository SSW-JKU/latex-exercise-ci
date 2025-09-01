import subprocess
import shutil
import argparse

from .test_repository import TestRepository, git, REMOTE_PATH, LOCAL_PATH
from .scenarios import get_scenario, scenarios


def _check_git_installed() -> None:
    try:
        git("--version")
        print("Git is available.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise EnvironmentError("Git is not installed or not found in PATH.") from e


def _prepare() -> None:
    print("Setting up repositories and files")

    for name, s in scenarios():
        print("-- Setting up scenario:", name)
        repo = TestRepository(name, REMOTE_PATH, LOCAL_PATH)
        repo.initialize_repo()
        print("---- Remote path:", repo.remote_path)
        print("---- Local path:", repo.local_path)

        shutil.copytree(s.path, repo.local_path, dirs_exist_ok=True)

        repo.commit_all("Initial commit")
        repo.push()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set up test git repositories for testing and verify "
        "their contents afterwards."
    )
    parser.add_argument(
        "--check",
        type=str,
        help="Performs checks for the given scenario.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    _check_git_installed()
    args = _parse_args()
    if args.check:
        s = get_scenario(args.check)
        if s is None:
            raise ValueError(f"Scenario '{args.check}' not found.")
        print(f"Verifying integration test outputs for '{s.name}'")
        repo = TestRepository(s.name, REMOTE_PATH, LOCAL_PATH)
        s.verify(repo)
    else:
        _prepare()
