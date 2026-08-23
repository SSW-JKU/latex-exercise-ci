"""Main entry point for the LaTeX build action."""

import logging

from .config import Config
from .gh.utils import github_action_output
from .tex.build import ResultCode, build_exercise, create_compilation_targets

log = logging.getLogger(__name__)


def main(config: Config) -> int:
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
