"""CLI interface for the LaTeX build action.

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

from .cli.args import create_parser
from .config import Config
from .latex_build_action import main

if __name__ == "__main__":
    args = create_parser().parse_args()

    # define the logger format
    LOG_LEVEL = logging.DEBUG if args.verbose else logging.INFO

    logging.basicConfig(format="%(levelname)s: %(message)s", level=LOG_LEVEL)

    # maybe add changed files to outputs of action?

    sys.exit(main(Config(args)))
