"""Preparation and verification script for the integration tests.

This module prepares the test repositories and sets up the test files
for the integration tests or performs verification after the action was
executed.
"""

import logging
from collections.abc import Sequence

from .cli.args import create_parser
from .git import check_git_installation
from .scenario import ScenarioManager

log = logging.getLogger(__name__)


def main(args: Sequence[str] | None = None) -> None:
    """Run the integration test script."""
    check_git_installation()
    log.info("Git is available.")
    options = create_parser().parse_args(args)
    scenario_manager = ScenarioManager.collect_scenarios(
        directory=options.scenario_dir, remote_path=options.remote_path, local_path=options.local_path
    )
    if options.task == "verify":
        scenario_manager.verify(options.scenario, options.outcome)
    else:
        scenario_manager.prepare(options.scenario)
