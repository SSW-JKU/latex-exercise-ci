"""Main entry point for the LaTeX build action.

Designed to be executed as a GitHub Action, this script iterates over the exercises of a semester (configurable via
`--config`) and (re)builds the corresponding TEX homeworks, lesson files, etc.
Successful builds are cached using folder-local `.checksum`
files, containing SHA-1 hashes of all (persistent) files. These hashes allow the
script to skip certain builds if the file hashes match. Note that SHA-1 is used
despite its flaws as the hashes merely impact performance and have no security
requirements.
"""

import logging
import sys
from argparse import Namespace

from .cli.args import create_parser
from .config import Config
from .gh.utils import github_action_output
from .tex.build import ResultCode, build_exercise, create_compilation_targets

log = logging.getLogger(__name__)


def main() -> None:
    """Invoke the build action with the implicitly set CLI args."""
    args = create_parser().parse_args()

    setup_logger(args)

    config = Config.from_args(args)

    result_code = run_action(config)

    sys.exit(result_code)


def setup_logger(args: Namespace) -> None:
    """Set up the logger config based on the CLI arguments.

    Args:
        args (Namespace) : the CLI args

    """
    # define the logger format
    log_level = logging.DEBUG if args.verbose else logging.INFO

    logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)


def run_action(config: Config) -> int:
    """Run the LaTeX build action.

    Build the corresponding exercise and lesson files within.

    Args:
        config (Config) : The configuration that is used for the build.

    """
    result_code: ResultCode = 0

    # create a predefined set of compilation targets
    # (e.g. for all exercises, we build the exercise, the solution and the LZD)
    targets = create_compilation_targets(config)

    changed_exercises = list[str]()

    for exercise in config.exercises:
        changed, last_result_code = build_exercise(exercise, config, targets)

        if changed:
            changed_exercises.append(exercise)

        result_code |= last_result_code

        # if the build was not a success, we may abort compilation (if enabled)
        if last_result_code != 0:
            assert result_code != 0  # noqa: S101
            if config.options.abort_all_on_error:
                return github_action_output(changed_exercises, result_code)

    return github_action_output(changed_exercises, result_code)
