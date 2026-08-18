# conftest.py
import shutil

import pytest


def pytest_configure() -> None:
    if shutil.which("latexmk") is None:
        pytest.exit(
            "\n\nERROR: 'latexmk' is required but not found on PATH.\n"
            "Install a TeX distribution (TeX Live, MiKTeX, MacTeX) that "
            "includes latexmk, then re-run tests.\n",
            returncode=1,
        )
