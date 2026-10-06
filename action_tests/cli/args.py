"""CLI argument parsing."""

from argparse import ArgumentParser


def create_parser() -> ArgumentParser:
    """Initialize the CLI argument parser used for executing the integration test suite."""
    parser = ArgumentParser(
        description="Set up test git repositories for testing and verify their contents afterwards."
    )
    parser.add_argument(
        "outcome",
        type=str,
        nargs="?",
        help="The outcome of the action execution.",
    )
    parser.add_argument(
        "--check",
        type=str,
        required=False,
        help="Performs checks for the given scenario.",
    )

    return parser
