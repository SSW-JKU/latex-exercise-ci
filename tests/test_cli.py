# pylint: disable=missing-module-docstring


from pathlib import Path
import unittest
from latex_build_action.cli import create_parser


class TestConfig(unittest.TestCase):
    # pylint: disable=missing-class-docstring

    def setUp(self) -> None:
        super().setUp()
        self.parser = create_parser()

    def test_parser_minimal_args(self) -> None:
        # pylint: disable=missing-function-docstring
        args = self.parser.parse_args(["-c", "no-file.json"])

        self.assertEqual(args.config, Path("no-file.json"))
        self.assertEqual(args.workdir, Path())
        self.assertFalse(args.no_git)
        self.assertFalse(args.abort_on_error)
        self.assertFalse(args.abort_all_on_error)
        self.assertFalse(args.rollback_on_error)
        self.assertFalse(args.rehash_on_error)
        self.assertFalse(args.verbose)

    def test_parser_short_form_args(self) -> None:
        # pylint: disable=missing-function-docstring
        args = self.parser.parse_args(["-c", "no-file.json", "-d", "myworkdir", "-v"])

        self.assertEqual(args.config, Path("no-file.json"))
        self.assertEqual(args.workdir, Path("myworkdir"))
        self.assertFalse(args.no_git)
        self.assertFalse(args.abort_on_error)
        self.assertFalse(args.abort_all_on_error)
        self.assertFalse(args.rollback_on_error)
        self.assertFalse(args.rehash_on_error)
        self.assertTrue(args.verbose)

    def test_parser_all_args_long_form(self) -> None:
        # pylint: disable=missing-function-docstring
        args = self.parser.parse_args(
            [
                "--config",
                "no-file.json",
                "--workdir",
                "myworkdir",
                "--no-git",
                "--abort-on-error",
                "--abort-all-on-error",
                "--rollback-on-error",
                "--rehash-on-error",
                "--verbose",
            ]
        )

        self.assertEqual(args.config, Path("no-file.json"))
        self.assertEqual(args.workdir, Path("myworkdir"))
        self.assertTrue(args.no_git)
        self.assertTrue(args.abort_on_error)
        self.assertTrue(args.abort_all_on_error)
        self.assertTrue(args.rollback_on_error)
        self.assertTrue(args.rehash_on_error)
        self.assertTrue(args.verbose)


if __name__ == "__main__":
    unittest.main()
