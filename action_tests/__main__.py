import subprocess
import shutil
import argparse

from .setup_repository import TestRepository, git, REMOTE_PATH, LOCAL_PATH
from .scenarios import Scenario


def _check_git_installed() -> None:
    try:
        git("--version")
        print("Git is available.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise EnvironmentError("Git is not installed or not found in PATH.") from e


def _prepare() -> None:

    for name, s in Scenario.REGISTRY.items():
        repo = TestRepository(name, REMOTE_PATH, LOCAL_PATH, exist_ok=False)
        repo.initialize_repo()

        shutil.copytree(s.path, repo.local_path, dirs_exist_ok=False)

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
        scenario = Scenario.REGISTRY.get(args.check, None)
        if scenario is None:
            raise ValueError(f"Scenario '{args.check}' not found.")
        print(f"Performing verification for '{scenario.name}'")

        # TODO: perform verification specifically for one target

    else:
        print("Setting up repositories and files")
        _prepare()
