"""
This module contains the main build logic for the LaTeX build action.
"""

from subprocess import CompletedProcess
import logging as log
from typing import Tuple
from .config import (
    EXERCISE_DIR_NAME,
    LESSON_DIR_NAME,
    LESSON_SUFFIX,
    SOLUTION_SUFFIX,
    OLD_SOLUTION_BUILD_SEMESTER_CUTOFF,
    Config,
)
from .compilation import TexCompilationTarget, latexmk_compile
from .hashing import check_and_update_hash, DEFAULT_IGNORE_PATTERNS
from .log_utils import print_build_log

ResultCode = int

Targets = list[TexCompilationTarget[CompletedProcess[bytes]]]


def create_latexmk_args(semester: int, for_solution: bool = False) -> str:
    """
    Creates the arguments that should be passed to `latexmk`.

    Args:
        semester (int) : The affected semester (used to distinguish between the
                         old and new build system).
        for_solution (bool, default: False) : Specifies whether the build should
                                              include solution material.

    Returns:
        (str) The argument string that can be passed to `latexmk`.
    """
    if for_solution:
        if semester < OLD_SOLUTION_BUILD_SEMESTER_CUTOFF:
            # build with old solution system
            return r'"\def\withSolutions{} \input{%S}"'

        # otherwise use new solution system
        return r'"\newif\ifsolutions\solutionstrue \input{%S}"'

    return r'"\input{%S}"'


def create_compilation_targets(config: Config) -> Targets:
    """
    Creates the default compilation targets for the given configuration.

    Args:
        config (Config) : The configuration that holds the relevant paths and
                          parameters.

    Returns:
        (list[TexCompilationTarget[CompletedProcess[bytes]]]) A list of compilation
        targets.
    """
    semester = config.determine_semester()

    def create_target(
        local_dir: str, entry_point: str, for_solution: bool = False, suffix: str = ""
    ) -> TexCompilationTarget[CompletedProcess[bytes]]:
        return TexCompilationTarget(
            config,
            local_dir,
            entry_point,
            create_latexmk_args(semester, for_solution),
            latexmk_compile,
            suffix,
        )

    return [
        # lesson
        create_target(LESSON_DIR_NAME, config.lesson_entry_point, suffix=LESSON_SUFFIX),
        # exercise
        create_target(EXERCISE_DIR_NAME, config.exercises_entry_point),
        # solution
        create_target(
            EXERCISE_DIR_NAME,
            config.exercises_entry_point,
            for_solution=True,
            suffix=SOLUTION_SUFFIX,
        ),
    ]


def compile_targets(
    config: Config, exercise: str, targets: Targets
) -> tuple[bool, ResultCode]:
    """
    Compiles the targets for the given exercise.

    Args:
        config (Config) : The config to use.
        exercise (str) : The exercise that should be compiled.
        targets (list[TexCompilationTarget[CompletedProcess]]) : The targets.

    Returns:
        (bool, int) A flag specifying whether the hash should be cached and the
                    result code of the compilation.
    """

    log.info(
        "%s: Changes detected. Rebuilding targets %s",
        exercise,
        [t.name(exercise) for t in targets],
    )

    result: ResultCode = 0

    for target in targets:
        log.info("%s: Building %s", exercise, target.name(exercise))

        # compile the corresponding target (create the PDF)
        result_process = target.compile(exercise)

        # the result is a CompletedProcess object, so we access its result code
        # manually (since we don't want to throw on error, we don't use
        # `check_returncode`)
        curr_return_code = result_process.returncode

        if curr_return_code == 0:
            log.info("%s: Successfully compiled %s", exercise, target.name(exercise))
        else:
            # if the compilation failed, we add the build log contents to the
            # output to simplify debugging in the CI
            log.error("%s: Failed compilation of %s", exercise, target.name(exercise))
            print_build_log(target.logfile(exercise))

            # depending on the provided command line options, we may rollback
            # changes, rehash the directory, or even abort the current
            # compilation
            if config.options.abort_on_error or config.options.abort_all_on_error:
                if config.options.rollback_on_error:
                    for target in targets:
                        target.rollback(exercise)
                return config.options.rehash_on_error, curr_return_code

        result |= curr_return_code

    rehash = result == 0 or config.options.rehash_on_error
    return rehash, result


def build_exercise(
    exercise: str, config: Config, targets: Targets
) -> Tuple[bool, ResultCode]:
    """
    Builds all specified targets for the given exercise.

    Args:
        exercise (str) : The target exercise.
        config (Config) : The configuration.
        targets (list[TexCompilationTarget[CompletedProcess]]) : The compilation
                                                                 targets.

    Returns:
        (ResultCode) The result code
    """
    basepath = config.workdir.joinpath(exercise)

    if basepath.is_dir():
        # resolve paths relative to basepath as the hash function only
        # allows relative or glob patterns
        generated_files = [
            str(file.relative_to(basepath))
            for target in targets
            for file in target.generated_files(exercise)
        ]

        ignores = list(DEFAULT_IGNORE_PATTERNS) + generated_files

        # only compile targets if hashes mismatch
        result = check_and_update_hash(
            basepath, lambda: compile_targets(config, exercise, targets), ignores
        )

        # if the hashes matched, we consider it an auto-success
        if result is None:
            log.info("%s: No changes detected", exercise)
            return (False, 0)
        return (True, result)

    log.warning("%s: Exercise directory does not exist", exercise)
    return (False, 1)
