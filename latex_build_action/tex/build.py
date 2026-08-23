#!/usr/bin/env python

"""Module that contains the main build logic for the LaTeX build action."""

import logging
from subprocess import CompletedProcess

from latex_build_action.config import (
    EXERCISE_DIR_NAME,
    LESSON_DIR_NAME,
    LESSON_SUFFIX,
    OLD_SOLUTION_BUILD_SEMESTER_CUTOFF,
    SOLUTION_SUFFIX,
    Config,
)
from latex_build_action.hashing import DEFAULT_IGNORE_PATTERNS, check_and_update_hash
from latex_build_action.log_utils import print_build_log

from .compilation import TexCompilationTarget, latexmk_compile

log = logging.getLogger(__name__)

ResultCode = int

Targets = list[TexCompilationTarget[CompletedProcess[bytes]]]


def create_latexmk_args() -> str:
    """Create the arguments that should be passed to `latexmk`.

    Args:
        semester (int) : The affected semester (used to distinguish between the
                         old and new build system).

    Returns:
        (str) The argument string that can be passed to `latexmk`.

    """
    return r'"\input{%S}"'


def create_latexmk_solution_args(semester: int) -> str:
    """Create the arguments that should be passed to `latexmk` to also include solution files.

    Args:
        semester (int) : The affected semester (used to distinguish between the
                         old and new build system).

    Returns:
        (str) The argument string that can be passed to `latexmk`.

    """
    if semester < OLD_SOLUTION_BUILD_SEMESTER_CUTOFF:
        # build with old solution system
        return r'"\def\withSolutions{} \input{%S}"'

    # otherwise use new solution system
    return r'"\newif\ifsolutions\solutionstrue \input{%S}"'


def create_compilation_targets(config: Config) -> Targets:
    """Create the default compilation targets for the given configuration.

    Args:
        config (Config) : The configuration that holds the relevant paths and
                          parameters.

    Returns:
        (list[TexCompilationTarget[CompletedProcess[bytes]]]) A list of compilation
        targets.

    """
    default_latexmk_args = create_latexmk_args()

    def create_target(
        local_dir: str, entry_point: str, latexmk_args: str, suffix: str = ""
    ) -> TexCompilationTarget[CompletedProcess[bytes]]:
        return TexCompilationTarget(
            config,
            local_dir,
            entry_point,
            latexmk_args,
            latexmk_compile,
            suffix,
        )

    return [
        # lesson
        create_target(
            LESSON_DIR_NAME,
            config.lesson_entry_point,
            default_latexmk_args,
            suffix=LESSON_SUFFIX,
        ),
        # exercise
        create_target(EXERCISE_DIR_NAME, config.exercises_entry_point, default_latexmk_args),
        # solution
        create_target(
            EXERCISE_DIR_NAME,
            config.exercises_entry_point,
            create_latexmk_solution_args(config.active_semester),
            suffix=SOLUTION_SUFFIX,
        ),
    ]


def compile_targets(config: Config, exercise: str, targets: Targets) -> tuple[bool, ResultCode]:
    """Compile the targets for the given exercise.

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
            print_build_log(log, target.logfile(exercise))

            # depending on the provided command line options, we may rollback
            # changes, rehash the directory, or even abort the current
            # compilation
            if config.options.abort_on_error or config.options.abort_all_on_error:
                if config.options.rollback_on_error:
                    for rollback_target in targets:
                        rollback_target.rollback(exercise)
                return config.options.rehash_on_error, curr_return_code

        result |= curr_return_code

    rehash = result == 0 or config.options.rehash_on_error
    return rehash, result


def build_exercise(exercise: str, config: Config, targets: Targets) -> tuple[bool, ResultCode]:
    """Build all specified targets for the given exercise.

    Args:
        exercise (str) : The target exercise.
        config (Config) : The configuration.
        targets (list[TexCompilationTarget[CompletedProcess]]) : The compilation
                                                                 targets.

    Returns:
        (bool, ResultCode) A tuple where the first entry denotes whether the
                           exercise has changed and the second entry denotes the
                           result code

    """
    basepath = config.workdir.joinpath(exercise)

    if basepath.is_dir():
        # resolve paths relative to basepath as the hash function only
        # allows relative or glob patterns
        generated_files = [
            str(file.relative_to(basepath)) for target in targets for file in target.generated_files(exercise)
        ]

        ignores = list(DEFAULT_IGNORE_PATTERNS) + generated_files

        # only compile targets if hashes mismatch
        result = check_and_update_hash(basepath, lambda: compile_targets(config, exercise, targets), ignores)

        # if the hashes matched, we consider it an auto-success
        if result is None:
            log.info("%s: No changes detected", exercise)
            return (False, 0)
        return (True, result)

    log.warning("%s: Exercise directory (%s) does not exist", exercise, str(basepath.absolute()))
    return (False, 0)
