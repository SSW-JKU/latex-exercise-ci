#!/usr/bin/env python

import unittest
from argparse import Namespace
from pathlib import Path

import pytest

from latex_build_action.compilation import TexCompilationTarget, latexmk_compile
from latex_build_action.config import Config

from ._test_utils import (
    INVALID_TEX_CONTENT,
    VALID_TEX_CONTENT,
    FileTestCaseMixin,
    RealFileSystemTestCase,
    create_default_config,
    create_default_json,
)


def _should_not_be_called(a: Path, b: str, c: str, d: Path) -> None:  # noqa: ARG001
    """Asserts that this callback is never actually invoked."""
    msg = "should not be called"
    raise AssertionError(msg)


class TestTexCompilationTarget(FileTestCaseMixin, unittest.TestCase):
    def test_compile(self) -> None:
        was_called = "was-called"

        # this helper action is used to verify the computed and passed arguments
        def compile_action(file_path: Path, output_name: str, latexmk_args: str, logfile_path: Path) -> str:
            basepath = Path().joinpath("25WS").joinpath("UE01").joinpath("testdir")

            self.assert_same_path(file_path, basepath.joinpath("texfile.tex"))
            assert output_name == "UE01_testfile"
            assert latexmk_args == "no-args"
            self.assert_same_path(logfile_path, basepath.joinpath("UE01_testfile.build_log"))
            return was_called

        target = TexCompilationTarget(
            create_default_config(),
            "testdir",
            "texfile.tex",
            "no-args",
            compile_action,
            "_testfile",
        )

        assert target.compile("UE01") is was_called

    def test_compile_invalid_exercise(self) -> None:
        target = TexCompilationTarget[None](
            create_default_config(),
            "testdir",
            "texfile.tex",
            "no-args",
            _should_not_be_called,
            "_testfile",
        )

        with pytest.raises(ValueError):  # noqa: PT011
            target.compile("custom-exercise")

    def test_generated_files(self) -> None:
        target = TexCompilationTarget[None](
            create_default_config(),
            "testdir",
            "texfile.tex",
            "no-args",
            _should_not_be_called,
            "_testfile",
        )

        file_names = list(target.generated_files("UE02"))

        self.assert_same_path(
            file_names,
            [
                Path("25WS", "UE02", "testdir", "UE02_testfile.pdf"),
                Path("25WS", "UE02", "testdir", "UE02_testfile.build_log"),
            ],
        )


class TestTexCompilationRollback(RealFileSystemTestCase):
    def test_rollback(self) -> None:

        target = TexCompilationTarget[None](
            Config(Namespace(config=create_default_json(), workdir=self.testdir, no_git=True)),
            "testsubdir",
            "texfile.tex",
            "no-args",
            _should_not_be_called,
            "_testfile",
        )

        self.file_with_parents(
            self.testdir.joinpath("25WS", "UE01", "testsubdir", "UE01_testfile.pdf"),
            "mycontent",
        )
        assert self.testdir.joinpath("25WS", "UE01", "testsubdir", "UE01_testfile.pdf").is_file()
        target.rollback("UE01")
        assert not self.testdir.joinpath("25WS", "UE01", "testsubdir", "UE01_testfile.pdf").is_file()


class TestTexCompilation(RealFileSystemTestCase):
    def test_latexmk_compile_success(self) -> None:

        texfiles = self.subdir("texfiles")
        texpath = texfiles.joinpath("texfile.tex")
        logpath = texfiles.joinpath("texfile.log")

        self.file_with_parents(texpath, VALID_TEX_CONTENT)

        res = latexmk_compile(texpath, "TexFile", r'"\input{%S}"', logpath)
        assert logpath.is_file()

        if res.returncode != 0:
            with logpath.open(encoding="UTF-8") as f:
                msg = "Error while compiling TeX file. Log contents:\n" + f.read()
                raise AssertionError(msg)

        assert Path("testdir", "texfiles", "TexFile.pdf").is_file()

    def test_latexmk_compile_failure(self) -> None:

        texfiles = self.subdir("texfiles")
        texpath = texfiles.joinpath("texfile.tex")
        logpath = texfiles.joinpath("texfile.log")

        self.file_with_parents(texpath, INVALID_TEX_CONTENT)

        res = latexmk_compile(texpath, "TexFile", r'"\input{%S}"', logpath)
        assert logpath.is_file()

        assert res.returncode != 0

        assert not Path("testdir", "texfiles", "TexFile.pdf").exists()


if __name__ == "__main__":
    unittest.main()
