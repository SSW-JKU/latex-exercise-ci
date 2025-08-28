# pylint: disable=missing-module-docstring
from argparse import Namespace
from pathlib import Path
import unittest
from latex_build_action.compilation import TexCompilationTarget, latexmk_compile
from latex_build_action.config import Config
from ._test_utils import (
    HasAssertions,
    create_default_config,
    create_default_json,
    FileTestCaseMixin,
    RealFileSystemTestCase,
    VALID_TEX_CONTENT,
    INVALID_TEX_CONTENT,
)


def _should_not_be_called(a: Path, b: str, c: str, d: Path) -> None:
    """
    Asserts that this callback is never actually invoked.
    """
    raise AssertionError("should not be called")


class TestTexCompilationTarget(FileTestCaseMixin, HasAssertions, unittest.TestCase):
    # pylint: disable=missing-class-docstring

    def test_compile(self) -> None:
        # pylint: disable=missing-function-docstring
        was_called = "was-called"

        # this helper action is used to verify the computed and passed arguments
        def compile_action(
            file_path: Path, output_name: str, latexmk_args: str, logfile_path: Path
        ) -> str:
            # pylint: disable=missing-function-docstring
            basepath = Path().joinpath("25WS").joinpath("UE01").joinpath("testdir")

            self.assertSamePath(file_path, basepath.joinpath("texfile.tex"))
            self.assertEqual(output_name, "UE01_testfile")
            self.assertEqual(latexmk_args, "no-args")
            self.assertSamePath(
                logfile_path, basepath.joinpath("UE01_testfile.build_log")
            )
            return was_called

        target = TexCompilationTarget(
            create_default_config(),
            "testdir",
            "texfile.tex",
            "no-args",
            compile_action,
            "_testfile",
        )

        self.assertIs(target.compile("UE01"), was_called)

    def test_compile_invalid_exercise(self) -> None:
        # pylint: disable=missing-function-docstring
        target = TexCompilationTarget[None](
            create_default_config(),
            "testdir",
            "texfile.tex",
            "no-args",
            _should_not_be_called,
            "_testfile",
        )

        self.assertRaises(AssertionError, lambda: target.compile("custom-exercise"))

    def test_generated_files(self) -> None:
        # pylint: disable=missing-function-docstring
        target = TexCompilationTarget[None](
            create_default_config(),
            "testdir",
            "texfile.tex",
            "no-args",
            _should_not_be_called,
            "_testfile",
        )

        file_names = list(target.generated_files("UE02"))

        self.assertSamePath(
            file_names,
            [
                Path("25WS", "UE02", "testdir", "UE02_testfile.pdf"),
                Path("25WS", "UE02", "testdir", "UE02_testfile.build_log"),
            ],
        )


class TestTexCompilationRollback(RealFileSystemTestCase):
    # pylint: disable=missing-class-docstring

    def test_rollback(self) -> None:
        # pylint: disable=missing-function-docstring

        target = TexCompilationTarget[None](
            Config(
                Namespace(
                    config=create_default_json(), workdir=self.testdir, no_git=True
                )
            ),
            "testsubdir",
            "texfile.tex",
            "no-args",
            _should_not_be_called,
            "_testfile",
        )

        self.file(
            self.testdir.joinpath("25WS", "UE01", "testsubdir", "UE01_testfile.pdf"),
            "mycontent",
            create_parents=True,
        )
        self.assertTrue(
            self.testdir.joinpath(
                "25WS", "UE01", "testsubdir", "UE01_testfile.pdf"
            ).is_file()
        )
        target.rollback("UE01")
        self.assertFalse(
            self.testdir.joinpath(
                "25WS", "UE01", "testsubdir", "UE01_testfile.pdf"
            ).is_file()
        )


class TestTexCompilation(RealFileSystemTestCase):
    # pylint: disable=missing-class-docstring

    def test_latexmk_compile_success(self) -> None:
        # pylint: disable=missing-function-docstring

        texfiles = self.subdir("texfiles")
        texpath = texfiles.joinpath("texfile.tex")
        logpath = texfiles.joinpath("texfile.log")

        self.file(texpath, VALID_TEX_CONTENT, create_parents=True)

        res = latexmk_compile(texpath, "TexFile", r'"\input{%S}"', logpath)
        self.assertTrue(logpath.is_file())

        if res.returncode != 0:
            with open(logpath, "r", encoding="UTF-8") as f:
                print("Error while compiling TeX file. Log contents:")
                print(f.read())

            res.check_returncode()

        self.assertTrue(Path("testdir", "texfiles", "TexFile.pdf").is_file())

    def test_latexmk_compile_failure(self) -> None:
        # pylint: disable=missing-function-docstring

        texfiles = self.subdir("texfiles")
        texpath = texfiles.joinpath("texfile.tex")
        logpath = texfiles.joinpath("texfile.log")

        self.file(texpath, INVALID_TEX_CONTENT, create_parents=True)

        res = latexmk_compile(texpath, "TexFile", r'"\input{%S}"', logpath)
        self.assertTrue(logpath.is_file())

        self.assertNotEqual(res.returncode, 0)

        self.assertFalse(Path("testdir", "texfiles", "TexFile.pdf").exists())


if __name__ == "__main__":
    unittest.main()
