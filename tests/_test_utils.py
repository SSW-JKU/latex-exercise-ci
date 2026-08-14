#!/usr/bin/env python

"""Contains utility functions and setup tools for unit testing."""

import json
import shutil
from argparse import Namespace
from collections.abc import Iterable
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, cast

from latex_build_action.config import Config

DEFAULT_CONFIG: dict[str, str | dict[str, str] | list[str]] = {
    "activeSemester": "25WS",
    "exercises": ["UE01", "UE02", "UE03"],
    "entryPoints": {"exercise": "ExerciseEntryPoint", "lesson": "LessonEntryPoint"},
}


def create_temp_json(**config: Any) -> Path:  # noqa: ANN401
    """Creates a temporary JSON file with the given contents.

    Args:
        config (dict[str, any]) : The configuration dictionary that is serialized to JSON.

    Returns:
        A path to the created (temporary) JSON file.

    """
    with NamedTemporaryFile(delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        with temp_path.open("w", encoding="UTF-8") as tf:
            json.dump(config, tf)
        return temp_path


def create_default_json() -> Path:
    """Creates a JSON containing a default configuration.

    Returns:
        A path to the created (temporary) JSON file.

    """
    return create_temp_json(**DEFAULT_CONFIG)


def create_default_config(workdir: Path = Path()) -> Config:
    """Creates the default test configuration and returns it.

    Args:
        workdir (Path, default='.') : The working directory that is used
                                      for resolving the configuration paths.

    Returns:
        A new config object containing the default test settings.

    """
    return Config(
        Namespace(
            config=create_default_json(),
            workdir=workdir,
            no_git=False,
            abort_on_error=False,
            abort_all_on_error=False,
            rollback_on_error=False,
            rehash_on_error=False,
            verbose=False,
        )
    )


def path_with_ext(path: Iterable[str], ext: str) -> list[str]:
    """Adds the given extension to the last part of the path.

    Args:
        path (Iterable[str]) : The path parts.
        ext (str) : The extension to append.

    Returns:
        list[str] : The path with the extension appended.

    """
    *parts, last = path
    return [*parts, f"{last}.{ext}"]


VALID_TEX_CONTENT = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\begin{document}
This is just a test document.
\end{document}
"""


INVALID_TEX_CONTENT = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\begin{document}
\begin{enumerate}
This is just a faulty test document.
\end{document}
"""


def file(path: Path, content: str) -> Path:
    """Utility function for creating files.

    Args:
        path (Path) : The path of the target file.
        content (str) : The contents that should be written.

    Returns:
        The path to the written file.

    """
    with path.open("w", encoding="UTF-8") as f:
        f.write(content)
    return path


def file_with_parents(path: Path, content: str) -> Path:
    """Utility function for creating files including their parent directories.

    Args:
        path (Path) : The path of the target file.
        content (str) : The contents that should be written.

    Returns:
        The path to the written file.

    """
    path.parent.mkdir(parents=True, exist_ok=True)

    return file(path, content)


def assert_same_path(
    path_a: Path | Iterable[Path],
    path_b: Path | Iterable[Path],
) -> None:
    """Helper assertion that allows comparison of `pathlib.Path` objects.
    This is useful in `FakeFileSystemTestCase`s, as direct instance
    comparisons of `Path` objects may fail there.
    """
    if isinstance(path_a, Path):
        assert isinstance(path_b, Path)
        assert str(path_a) == str(path_b)
    else:
        assert isinstance(path_a, list)
        assert isinstance(path_b, list)
        assert [str(p) for p in path_a] == [str(p) for p in cast("Iterable[Path]", path_b)]


class RealFileSystemTest:
    """
    Base test class that creates a temporary test directory for each test case
    and removes it afterwards.
    """

    """Constant that determines whether the test directory should be removed after each test case."""
    DEBUG = False

    def setup_method(self) -> None:
        self.testdir = Path("testdir")
        self.testdir.mkdir()

    def teardown_method(self) -> None:
        if not self.DEBUG:
            shutil.rmtree(self.testdir)

    def subdir(self, *subdir: str) -> Path:
        """Helper function that registers a subdirectory within the
        `self.testdir`.

        Args:
            *subdir (str) : The subdirectory name or path.

        Returns:
            (Path) the path to the subdirectory.

        """
        return self.testdir.joinpath(*subdir)

    def generate_tex_files(self, *paths: Path, semester: str = "25WS", valid: bool = True) -> None:
        """Helper function that generates TeX files in the given paths.

        Args:
            *paths (Path) : The list of paths to tex files.
            semester (str, default: '25WS') : The semester that is used as the
                                              base directory.
            valid (bool, default: True) : Determines whether the generated files
                                          are valid or invalid TeX files.

        """
        content = VALID_TEX_CONTENT if valid else INVALID_TEX_CONTENT
        sem_path = self.testdir.joinpath(semester)
        for path in paths:
            file_with_parents(sem_path.joinpath(path), content)

    def checksum(self, *path: str) -> str:
        """Helper function that reads the directory hash from the corresponding
        .checksum file in the directory at the given (relative) path.

        Args:
            *path (str) : The path to the hashed directory.

        Returns:
            str : The directory hash.

        """
        checksum_path = self.testdir.joinpath(*path).joinpath(".checksum")
        with checksum_path.open(encoding="UTF-8") as checksum:
            return checksum.read()

    def assert_is_file(self, *path: str) -> None:
        """Custom assertion that checks whether the given path is a valid file
        within the `self.testdir` test directory.

        Args:
            *path (str) : The path to the file.

        """
        p = self.testdir.joinpath(*path)
        assert p.is_file(), f"{p.absolute()!s} is not a file"

    def assert_no_file(self, *path: str) -> None:
        """Custom assertion that checks whether the given path within the
        `self.testdir` does not exist.

        Args:
            *path (str) : The path to the file.

        """
        p = self.testdir.joinpath(*path)
        assert not p.exists(), f"{p.absolute()!s} exists!"

    def assert_was_compiled(self, *path: str, check_buildlog: bool = True) -> None:
        """Assertion that checks whether compilation of the target was successful.
        It does so by verifying that a PDF (and if enabled a build log file)
        was created.

        Args:
            *path (str) : The base path to the directory containing the
                          compilation targets.
            check_buildlog (bool, default: True) : Also verifies that a build
                                                   log file was created.

        """
        self.assert_is_file(*path_with_ext(path, "pdf"))
        if check_buildlog:
            self.assert_is_file(*path_with_ext(path, "build_log"))

    def assert_not_compiled(self, *path: str, check_buildlog: bool = True, expect_buildlog: bool = True) -> None:
        """Assertion that checks whether compilation of the target failed.
        It does so by verifying that a PDF (and if enabled a build log file)
        was not created.

        Args:
            *path (str) : The base path to the directory containing the
                          compilation targets.
            check_buildlog (bool, default: True) : Also verifies that a build
                                                   log file was created.

        """
        self.assert_no_file(*path_with_ext(path, "pdf"))
        if check_buildlog:
            if expect_buildlog:
                self.assert_is_file(*path_with_ext(path, "build_log"))
            else:
                self.assert_no_file(*path_with_ext(path, "build_log"))
