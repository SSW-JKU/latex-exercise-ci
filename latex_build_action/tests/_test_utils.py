"""
Contains utility functions and setup tools for unit testing.
"""

from argparse import Namespace
import json
import shutil
import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Iterable, Protocol, Type, cast
from pyfakefs import fake_filesystem_unittest
from latex_build_action.config import Config


DEFAULT_CONFIG = {
    "activeSemester": "25WS",
    "exercises": ["UE01", "UE02", "UE03"],
    "entryPoints": {"exercise": "ExerciseEntryPoint", "lesson": "LessonEntryPoint"},
}


def dont_call[R](*_: Any) -> R:  # type: ignore[type-var]
    """
    Helper function that can be used for callbacks that
    should never be called.
    """
    raise AssertionError("should not be called")


def create_temp_json(**config: Any) -> Path:
    """
    Creates a temporary JSON file with the given contents.

    Args:
        config (dict[str, any]) : The configuration dictionary that is serialized to JSON.

    Returns:
        A path to the created (temporary) JSON file.
    """
    # pylint: disable=consider-using-with
    temp_file = NamedTemporaryFile(delete=False)
    with open(temp_file.name, "w", encoding="UTF-8") as tf:
        json.dump(config, tf)
    # print("wrote tempfile:", temp_file.name)
    return Path(temp_file.name)


def create_default_json() -> Path:
    """
    Creates a JSON containing a default configuration.

    Returns:
        A path to the created (temporary) JSON file.
    """
    return create_temp_json(**DEFAULT_CONFIG)


def create_default_config(workdir: Path = Path()) -> Config:
    """
    Creates the default test configuration and returns it.

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
    """
    Adds the given extension to the last part of the path.

    Args:
        path (Iterable[str]) : The path parts.
        ext (str) : The extension to append.

    Returns:
        list[str] : The path with the extension appended.
    """
    *parts, last = path
    return parts + [f"{last}.{ext}"]


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


class HasAssertions(Protocol):
    """
    Base protocol that provides basic assertion methods.
    This could be omitted if `unittest.TestCase` specified a proper Protocol,
    to be used within both regular and fake file system test suites.
    """

    # pylint: disable=invalid-name
    # pylint: disable=missing-function-docstring
    def assertEqual(self, a: Any, b: Any) -> None: ...

    # pylint: disable=invalid-name
    # pylint: disable=missing-function-docstring
    def assertIsInstance(self, a: Any, expected_type: Type[Any]) -> None: ...


class FileTestCaseMixin:
    """
    Test mixin that uses `pyfakefs` to enable tests with a fake file system.
    """

    def file(self, path: Path, content: str, create_parents: bool = False) -> Path:
        """
        Utility function for creating files.

        Args:
            path (Path) : The path of the target file.
            content (str) : The contents that should be written.
            create_parents (bool, default: False) : Creates parent directories.

        Returns:
            The path to the written file.
        """

        if create_parents:
            path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="UTF-8") as f:
            f.write(content)
        return path

    # pylint: disable=invalid-name
    def assertSamePath(
        self: HasAssertions,
        path_a: Path | Iterable[Path],
        path_b: Path | Iterable[Path],
    ) -> None:
        """
        Helper assertion that allows comparison of `pathlib.Path` objects.
        This is useful in `FakeFileSystemTestCase`s, as direct instance
        comparisons of `Path` objects may fail there.
        """
        if isinstance(path_a, Path):
            self.assertIsInstance(path_b, Path)
            self.assertEqual(str(path_a), str(path_b))
        else:
            self.assertIsInstance(path_a, list)
            self.assertIsInstance(path_b, list)
            self.assertEqual(
                [str(p) for p in path_a], [str(p) for p in cast(Iterable[Path], path_b)]
            )


class FakeFileSystemTestCase(FileTestCaseMixin, fake_filesystem_unittest.TestCase):
    """
    Unit test base class that allows tests using a fake file system.
    """

    def setUp(self) -> None:
        """
        Sets up the fake file system and calls the file system setup function.
        """
        self.setUpPyfakefs()
        self.create_file_structure()

    def create_file_structure(self) -> None:
        """
        Template function that should create the necessary file structure
        for the test.
        """


class RealFileSystemTestCase(FileTestCaseMixin, unittest.TestCase):
    # pylint: disable=missing-class-docstring

    def subdir(self, *subdir: str) -> Path:
        """
        Helper function that registers a subdirectory within the
        `self.testdir`.

        Args:
            *subdir (str) : The subdirectory name or path.

        Returns:
            (Path) the path to the subdirectory.
        """
        sd = self.testdir.joinpath(*subdir)
        return sd

    def setUp(self) -> None:
        super().setUp()
        self.testdir = Path("testdir")
        self.testdir.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.testdir)
        super().tearDown()

    def generate_tex_files(
        self, *paths: Path, semester: str = "25WS", valid: bool = True
    ) -> None:
        """
        Helper function that generates TeX files in the given paths.

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
            self.file(sem_path.joinpath(path), content, create_parents=True)

    def checksum(self, *path: str) -> str:
        """
        Helper function that reads the directory hash from the corresponding
        .checksum file in the directory at the given (relative) path.

        Args:
            *path (str) : The path to the hashed directory.

        Returns:
            str : The directory hash.
        """
        checksum_path = self.testdir.joinpath(*path).joinpath(".checksum")
        with open(checksum_path, "r", encoding="UTF-8") as checksum:
            return checksum.read()

    # pylint: disable=invalid-name
    def assertIsFile(self, *path: str) -> None:
        """
        Custom assertion that checks whether the given path is a valid file
        within the `self.testdir` test directory.

        Args:
            *path (str) : The path to the file.
        """
        p = self.testdir.joinpath(*path)
        self.assertTrue(p.is_file(), msg=f"{str(p.absolute())} is not a file")

    # pylint: disable=invalid-name
    def assertNoFile(self, *path: str) -> None:
        """
        Custom assertion that checks whether the given path within the
        `self.testdir` does not exist.

        Args:
            *path (str) : The path to the file.
        """
        p = self.testdir.joinpath(*path)
        self.assertFalse(p.exists(), msg=f"{str(p.absolute())} exists!")

    # pylint: disable=invalid-name
    def assertWasCompiled(self, *path: str, check_buildlog: bool = True) -> None:
        """
        Assertion that checks whether compilation of the target was successful.
        It does so by verifying that a PDF (and if enabled a build log file)
        was created.

        Args:
            *path (str) : The base path to the directory containing the
                          compilation targets.
            check_buildlog (bool, default: True) : Also verifies that a build
                                                   log file was created.
        """
        self.assertIsFile(*path_with_ext(path, "pdf"))
        if check_buildlog:
            self.assertIsFile(*path_with_ext(path, "build_log"))

    # pylint: disable=invalid-name
    def assertNotCompiled(
        self, *path: str, check_buildlog: bool = True, expect_buildlog: bool = True
    ) -> None:
        """
        Assertion that checks whether compilation of the target failed.
        It does so by verifying that a PDF (and if enabled a build log file)
        was not created.

        Args:
            *path (str) : The base path to the directory containing the
                          compilation targets.
            check_buildlog (bool, default: True) : Also verifies that a build
                                                   log file was created.
        """

        self.assertNoFile(*path_with_ext(path, "pdf"))
        if check_buildlog:
            if expect_buildlog:
                self.assertIsFile(*path_with_ext(path, "build_log"))
            else:
                self.assertNoFile(*path_with_ext(path, "build_log"))
