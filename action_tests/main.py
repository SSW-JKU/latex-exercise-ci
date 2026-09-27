"""Preparation and verification script for the integration tests.

This module prepares the test repositories and sets up the test files
for the integration tests or performs verification after the action was
executed.
"""

import logging
from pathlib import Path

from .cli.args import create_parser
from .git import check_git_installation
from .scenario_manager import ScenarioManager

log = logging.getLogger(__name__)

REMOTE_PATH = Path("/tmp/test-remotes")  # noqa: S108
LOCAL_PATH = Path("/tmp/test-locals")  # noqa: S108


def _prepare(scenario_manager: ScenarioManager) -> None:
    log.info("Setting up repositories and files")

    for scenario in scenario_manager.scenarios():
        scenario.prepare(REMOTE_PATH, LOCAL_PATH)


def run_integration_test(scenario_manager: ScenarioManager) -> None:
    """Run the integration test script."""
    check_git_installation()
    log.info("Git is available.")
    args = create_parser().parse_args()
    if args.check:
        s = scenario_manager.get_scenario(args.check)
        if s is None:
            msg = f"Scenario '{args.check}' not found."
            raise ValueError(msg)

        s.test(REMOTE_PATH, LOCAL_PATH, args.outcome)
    else:
        _prepare(scenario_manager)
