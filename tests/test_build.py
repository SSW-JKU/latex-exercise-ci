#!/usr/bin/env python

import unittest

from latex_build_action.build import create_latexmk_args, create_latexmk_solution_args


class TestLatexMkArgs(unittest.TestCase):
    def test_old_solution_build(self) -> None:
        assert create_latexmk_solution_args(22) == r'"\def\withSolutions{} \input{%S}"'

        assert create_latexmk_solution_args(18) == r'"\def\withSolutions{} \input{%S}"'

    def test_new_solution_build(self) -> None:
        assert create_latexmk_solution_args(23) == r'"\newif\ifsolutions\solutionstrue \input{%S}"'
        assert create_latexmk_solution_args(24) == r'"\newif\ifsolutions\solutionstrue \input{%S}"'

    def test_common_build(self) -> None:
        assert create_latexmk_args() == r'"\input{%S}"'
        assert create_latexmk_args() == r'"\input{%S}"'


if __name__ == "__main__":
    unittest.main()
