"""Defines common assertion functions."""

from os import PathLike
from pathlib import Path
from typing import Any


def assert_true(cond: bool, *msg: str) -> None:  # noqa: FBT001
    """Assert that the given `cond` is `True` and otherwise raises an `AssertionError` with the given `msg`.

    Args:
        cond (bool) : The condition to check
        *msg (str) : The error message to add to the raised error

    """
    if not cond:
        error_msg = " ".join(msg)
        raise AssertionError(error_msg)


def assert_eq(expected: Any, actual: Any, *msg: str) -> None:  # noqa: ANN401
    """Assert that the given values match and raises an `AssertionError` with the given `msg`.

    Args:
        expected (Any) : The expected value
        actual (Any) : The actual value
        *msg (str) : The error message to add to the raised error

    """
    assert_true(expected == actual, *msg, f"Expected: <{expected}>, Actual: <{actual}>")


type AnyPath = str | PathLike[str]


def assert_files_exist(base_path: AnyPath, *paths: AnyPath) -> None:
    """Assert that the given files exist.

    Also fails if the list of files is empty.

    Args:
        base_path (AnyPath) : The base directory for all target files
        *paths (AnyPath) : The (relative) paths to the target files

    """
    assert_true(len(paths) > 0, "Must specify at least one path")
    base_dir = Path(base_path)
    for path in paths:
        assert_file_exists(base_dir, path)


def assert_files_missing(base_path: AnyPath, *paths: AnyPath) -> None:
    """Assert that the given files do not exist.

    Also fails if the list of files is empty.

    Args:
        base_path (Path) : The base directory for all target files
        *paths (list[AnyPath]) : The (relative) paths to the target files

    """
    assert_true(len(paths) > 0, "Must specify at least one path")
    base_dir = Path(base_path)
    for path in paths:
        assert_file_missing(base_dir, path)


def assert_file_exists(*path: AnyPath) -> None:
    """Assert that the given file exists.

    Args:
        *path (AnyPath) : The path to the target file

    """
    file_path = Path(*path)
    assert_true(
        file_path.is_file(),
        "File does not exist or is not a regular file:",
        str(file_path),
    )


def assert_file_missing(*path: AnyPath) -> None:
    """Assert that the given file does not exist.

    Args:
        *path (AnyPath) : The path to the target file

    """
    file_path = Path(*path)
    assert_true(
        not file_path.is_file(),
        "File does exist but shouldn't:",
        str(file_path),
    )
