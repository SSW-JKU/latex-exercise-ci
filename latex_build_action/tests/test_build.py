# pylint: disable=missing-module-docstring
import unittest
from latex_build_action.build import create_latexmk_args


class TestLatexMkArgs(unittest.TestCase):
    # pylint: disable=missing-class-docstring
    def test_old_solution_build(self) -> None:
        # pylint: disable=missing-function-docstring
        self.assertEqual(
            r'"\def\withSolutions{} \input{%S}"',
            create_latexmk_args(22, for_solution=True),
        )
        self.assertEqual(
            r'"\def\withSolutions{} \input{%S}"',
            create_latexmk_args(18, for_solution=True),
        )

    def test_new_solution_build(self) -> None:
        # pylint: disable=missing-function-docstring
        self.assertEqual(
            r'"\newif\ifsolutions\solutionstrue \input{%S}"',
            create_latexmk_args(23, for_solution=True),
        )
        self.assertEqual(
            r'"\newif\ifsolutions\solutionstrue \input{%S}"',
            create_latexmk_args(24, for_solution=True),
        )

    def test_common_build(self) -> None:
        # pylint: disable=missing-function-docstring
        self.assertEqual(r'"\input{%S}"', create_latexmk_args(21))
        self.assertEqual(r'"\input{%S}"', create_latexmk_args(24))


if __name__ == "__main__":
    unittest.main()
