"""
A module containing functions and classes to define and perform
LaTeX compilations.
"""

import os
from pathlib import Path
from typing import Callable, Generic, Iterable, TypeVar
import subprocess
from .config import Config


def latexmk_compile(
    file_path: Path,
    output_name: str,
    pdflatex_args: str,
    logfile: Path,
    log_cmd: bool = False,
) -> subprocess.CompletedProcess[bytes]:
    """
    Uses `latexmk` and `pdflatex` to compile the given file to a PDF.

    Args:
        pdflatex_args (str) : The arguments that are passed to the command.
        file_path (Path) : The path to the input TeX file.
        output_name (str) : The output name of the compilation.
        logfile (Path) : A path to the logfile to which the command output is
                         written.
        log (bool, default: False) : Print the executed command to console.
    """

    # For some reason, calling `latexmk .. -pdflatex='pdflatex ...'` via
    # subprocess does not work as it cannot find `pdflatex` afterwards.
    # Maybe, this has something to do with environment vars (particularly PATH)
    # that are not properly propagated to the command executed from `latexmk`.
    # Putting the actual call into a separate shell script seems to do the
    # trick.
    compile_script = Path(os.path.dirname(__file__), "compile_tex.sh")

    with open(logfile, "w", encoding="UTF-8") as log:
        proc = subprocess.run(
            # latexmk_cmd(file_path, output_name, pdflatex_args),
            [
                "sh",
                compile_script,
                str(file_path.resolve()),
                output_name,
                pdflatex_args,
            ],
            check=False,
            shell=False,
            stdout=log,
            stderr=subprocess.STDOUT,
        )

        if log_cmd:
            print(f"the commandline is {proc.args}")

        return proc


R = TypeVar("R")

CompileAction = Callable[[Path, str, str, Path], R]


class TexCompilationTarget(Generic[R]):
    """
    Defines a compilation target for arbitrary exercises.
    A compilation target takes a single (TeX) file as an input
    and produces an output and typically a log file.
    """

    def __init__(
        self,
        config: Config,
        local_directory: str,
        entry_point: str,
        latexmk_args: str,
        compile_action: CompileAction[R],
        file_suffix: str = "",
    ) -> None:
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        """
        Defines a new compilation target for the given local directory in the
        context of the given context.

        Args:
            config (Config) : The configuration that should be used.
            local_directory (str) : The local directory that is used within a
                                    given exercise for a compilation.
            entry_point (str) : The entry point for the compilation (the TeX
                                file name).
            latexmk_args (str) : The arguments that are passed to the
                                 compilation.
            file_suffix (str) : The suffix that is appended for the output file
                                name.
            compile_action (CompileAction, default) : The compilation action.
        """
        self.config = config
        self.local_directory = local_directory
        self.entry_point = entry_point
        self.file_suffix = file_suffix
        self.latexmk_args = latexmk_args
        self.compile_action: CompileAction[R] = compile_action

    def _generate_path(self, exercise: str) -> Path:
        """
        Generates the base path for the given exercise.
        Args:
            exercise (str) : The target exercise.

        Returns:
            (Path) The target base path for the exercise.
        """
        return self.config.workdir.joinpath(exercise).joinpath(self.local_directory)

    def name(self, exercise: str) -> str:
        """
        Returns the target name for the given exercise.
        Args:
            exercise (str) : The target exercise.

        Returns:
            (str) The target name for the exercise.
        """
        return exercise + self.file_suffix + ".pdf"

    def logfile_name(self, exercise: str) -> str:
        """
        Returns the logfile name for the given exercise.
        Args:
            exercise (str) : The target exercise.

        Returns:
            (str) The target logfile name for the exercise.
        """
        return exercise + self.file_suffix + ".build_log"

    def logfile(self, exercise: str) -> Path:
        """
        Returns the logfile path for the given exercise.
        Args:
            exercise (str) : The target exercise.

        Returns:
            (str) The target logfile path for the exercise.
        """
        return self._generate_path(exercise).joinpath(self.logfile_name(exercise))

    def generated_files(self, exercise: str) -> Iterable[Path]:
        """
        Returns the (relative) file paths that will be generated by this
        compilation.
        """
        file_names = [self.name(exercise), self.logfile_name(exercise)]
        basepath = self._generate_path(exercise)
        return [basepath.joinpath(n) for n in file_names]

    def compile(self, exercise: str) -> R:
        """
        Compiles this target for the given exercise.

        Args:
            exercise (str) : The exercise number for whom the target should be
                             compiled.

        Returns:
            The result of the compilation action.
        """
        assert (
            exercise in self.config.exercises
        ), f"Exercise {exercise} not defined in config"
        target_file_dir = self._generate_path(exercise)
        output_name = f"{exercise}{self.file_suffix}"
        file_path = target_file_dir.joinpath(self.entry_point)

        return self.compile_action(
            file_path, output_name, self.latexmk_args, self.logfile(exercise)
        )

    def rollback(self, exercise: str) -> None:
        """
        Rolls back any changes to the target generated files.

        Args:
            exercise (str) : The exercise for which the changes should be
                             reverted.
        """
        for f in self.generated_files(exercise):
            resolved = f.resolve()
            if resolved.exists():
                path = str(resolved)

                git_rollback = ["git", "checkout", "--", path]
                rm_cmd = ["rm", path]

                cmd = []
                if not self.config.options.no_git:
                    cmd += git_rollback
                    cmd += ["||"]
                cmd += rm_cmd

                subprocess.run(
                    cmd,
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
