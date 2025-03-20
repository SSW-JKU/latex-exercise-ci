"""
Handles command line option definitions and parsing.
"""


from argparse import ArgumentParser
from pathlib import Path


def create_parser() -> ArgumentParser:
    """
    Defines the available command line options and creates a parser that handles
    them.

    Returns:
        (ArgumentParser) an argument parser configured for the available
                         options.
    """
    parser = ArgumentParser()
    parser.add_argument('-c',
                        '--config',
                        help="The configuration JSON to use.",
                        type=Path,
                        required=True)

    parser.add_argument('-d',
                        '--workdir',
                        help="The working directory for the build process.",
                        type=Path,
                        required=False,
                        default=Path())

    parser.add_argument(
        '--no-git',
        help='Prevents use of `git checkout` to rollback exercise directory changes.',
        action='store_true')

    parser.add_argument(
        '--abort-on-error',
        help='Aborts the build of a directory if errors occurred.',
        action='store_true')

    parser.add_argument(
        '--abort-all-on-error',
        help='Aborts the overall build if errors occurred.',
        action='store_true')

    parser.add_argument(
        '--rollback-on-error',
        help='Reverts any changes to the current exercise directory if build \
            errors occurred. Requires --abort-on-error',
        action='store_true')

    parser.add_argument(
        '--rehash-on-error',
        help='Rehashes the current exercise directory even if build errors occurred.',
        action='store_true')

    parser.add_argument(
        '-v',
        '--verbose',
        help='Enables verbose logging',
        action='store_true'
    )

    return parser
