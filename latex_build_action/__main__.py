#!/usr/bin/env python

"""
Designed to be executed as a GitHub Action,
this script iterates over the exercises of a semester
(configurable via `--config`) and (re)builds the corresponding TEX homeworks,
lesson files, etc. Successful builds are cached using folder-local `.checksum`
files, containing SHA-1 hashes of all (persistent) files. These hashes allow the
script to skip certain builds if the file hashes match. Note that SHA-1 is used
despite its flaws as the hashes merely impact performance and have no security
requirements.
"""

import logging as log
import sys

from .build import ResultCode, build_exercise, create_compilation_targets
from .config import Config
from .cli import create_parser


def main(config: Config) -> int:
    """
    The main script entry point that takes a given script configuration
    and builds the corresponding exercise and lesson files within.

    Args:
        config (Config) : The configuration that is used for the build.
    """
    result_code: ResultCode = 0

    # create a predefined set of compilation targets
    # (e.g. for all exercises, we build the exercise, the solution and the LZD)
    targets = create_compilation_targets(config)

    for exercise in config.exercises:
        last_result_code = build_exercise(exercise, config, targets)

        result_code |= last_result_code

        # if the build was not a success, we may abort compilation (if enabled)
        if last_result_code != 0:
            assert result_code != 0
            if config.options.abort_all_on_error:
                return result_code

    return result_code


if __name__ == "__main__":
    args = create_parser().parse_args()

    # define the logger format
    LOG_LEVEL = log.DEBUG if args.verbose else log.INFO

    log.basicConfig(format="%(levelname)s: %(message)s", level=LOG_LEVEL)

    # maybe add changed files to outputs of action?

    sys.exit(main(Config(args)))
