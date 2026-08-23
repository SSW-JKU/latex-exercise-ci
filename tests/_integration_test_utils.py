"""Collection of utility functions/definitions for integration/system tests."""

import logging
import subprocess
from collections.abc import Callable, Iterable
from enum import Enum
from pathlib import Path

from latex_build_action.cli.args import create_parser
from latex_build_action.config import Config
from latex_build_action.main import run_action

from ._test_utils import create_temp_json

log = logging.getLogger(__name__)

INTEGRATION_TEST_CONFIG_BASE: dict[str, str | list[str] | dict[str, str]] = {
    "activeSemester": "25WS",
    "exercises": [],
    "entryPoints": {"exercise": "main.tex", "lesson": "Lernziele.tex"},
}


type BuildSuccessFn = Callable[[Path, Iterable[str]], None]
type BuildErrorFn = Callable[[Path, Iterable[str], Iterable[str]], None]


class Mode(Enum):
    DEFAULT = 1
    DEBUG = 2


def create_json_config(exercises: Iterable[str]) -> Path:
    config = {**INTEGRATION_TEST_CONFIG_BASE}
    config["exercises"] = list(exercises)
    return create_temp_json(**config)


def build_success_cli(workdir: Path, exercises: Iterable[str]) -> None:
    result = _build(workdir, exercises)
    result.check_returncode()


def build_success_main(workdir: Path, exercises: Iterable[str]) -> None:
    result_code = _main(workdir, exercises, extra_args=())
    assert result_code == 0, "Expected build to succeed, but it failed"


def build_failed_cli(workdir: Path, exercises: Iterable[str], extra_args: Iterable[str] = ()) -> None:
    result = _build(workdir, exercises, extra_args)
    assert result.returncode != 0, "Expected build to fail, but it succeeded."


def build_failed_main(workdir: Path, exercises: Iterable[str], extra_args: Iterable[str] = ()) -> None:
    result_code = _main(workdir, exercises, extra_args)
    assert result_code != 0, "Expected build to fail, but it succeeded."


def _main(workdir: Path, exercises: Iterable[str], extra_args: Iterable[str] = ()) -> int:
    json_config = create_json_config(exercises)
    args = create_parser().parse_args(
        [
            "-c",
            str(json_config),
            "-d",
            str(workdir),
            "--no-git",
            *extra_args,
        ]
    )
    config = Config.from_args(args)
    return run_action(config)


def _build(
    workdir: Path, exercises: Iterable[str], extra_args: Iterable[str] = (), mode: Mode = Mode.DEFAULT
) -> subprocess.CompletedProcess[bytes]:
    """Runs the integration test for the given exercises in the target working
    directory using the `INTEGRATION_TEST_CONFIG_BASE` example config as a
    baseline and logs the command output if enabled.

    Args:
        workdir (Path): the current working directory
        exercises (Iterable[str]) : The exercises that should be compiled.
        extra_args (Iterable[str], optional) : Additional command line arguments
                                                to pass to the build action.
        mode (Mode, optional) : The running mode of the test

    Returns:
        subprocess.CompletedProcess[bytes] : The result of the build process.
    """

    json_config = create_json_config(exercises)

    logfile = workdir.joinpath(".test.log")

    with logfile.open("w", encoding="UTF-8") as f:
        result = subprocess.run(  # noqa: S603
            [
                "/usr/bin/env",
                "python3",
                "-m",
                "latex_build_action",
                "-d",
                str(workdir.absolute()),
                "-c",
                str(json_config.absolute()),
                "--no-git",
                *extra_args,
            ],
            check=False,
            shell=False,
            stdout=f,
            stderr=subprocess.STDOUT,
        )

    if mode == Mode.DEBUG:
        with logfile.open(encoding="UTF-8") as f:
            log.info(f.read())

    logfile.unlink()

    return result


success_builds: list[BuildSuccessFn] = [build_success_cli, build_success_main]
failed_builds: list[BuildErrorFn] = [build_failed_cli, build_failed_main]
