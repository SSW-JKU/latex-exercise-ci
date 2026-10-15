"""CLI argument parsing."""

from argparse import ArgumentParser


def create_parser() -> ArgumentParser:
    """Initialize the CLI argument parser used for executing the integration test suite."""
    parser = ArgumentParser(
        description="Set up test git repositories for testing and verify their contents afterwards."
    )
    parser.add_argument(
        "--scenario-dir",
        type=str,
        nargs="?",
        default="action_tests",
        help="The source directory containing the scenario definitions.",
    )
    parser.add_argument(
        "--remote-path",
        type=str,
        required=False,
        default="/tmp/test-remotes",  # noqa: S108
        help="The path to the remote git repository.",
    )
    parser.add_argument(
        "--local-path",
        type=str,
        required=False,
        default="/tmp/test-locals",  # noqa: S108
        help="The path to the local git repository.",
    )

    subparsers = parser.add_subparsers(dest="task", required=True)

    prepare_p = subparsers.add_parser("prepare")
    prepare_p.add_argument(
        "scenario",
        type=str,
        nargs="?",
        help="The name of the target scenario.",
    )

    verify_p = subparsers.add_parser("verify")
    verify_p.add_argument("outcome", type=str, help="The outcome of the action execution to verify.")

    verify_p.add_argument(
        "scenario",
        type=str,
        nargs="?",
        help="The name of the target scenario.",
    )

    return parser
