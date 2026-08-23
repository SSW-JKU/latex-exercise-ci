"""File defining utility functions specifically for GitHub Action handling."""

import logging
import os
from pathlib import Path

from latex_build_action.tex.build import ResultCode

log = logging.getLogger(__name__)


def github_action_output(changed_exercises: list[str], result_code: ResultCode) -> ResultCode:
    """Set the output of the GitHub Action to the changed exercises.

    Args:
        changed_exercises (list[str]) : The list of changed exercises.
        result_code (int) : The result code of the compilation.

    Returns:
        (int) The result code of the compilation.

    """
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        exercise_str = ",".join(changed_exercises)
        log.info(
            "Writing changed exercises (%s) to GitHub output file %s",
            exercise_str,
            github_output,
        )
        try:
            with Path(github_output).open("a", encoding="UTF-8") as f:
                f.write(f"changed-exercises={exercise_str}\n")
        except OSError:
            log.exception("Failed to write to %s", github_output)
            return 1

    return result_code
