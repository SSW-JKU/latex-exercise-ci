import shutil
from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def stub_callback(mocker: MockerFixture) -> Generator[MagicMock]:
    """Stubs a callback that should never actually invoked."""
    callback = mocker.stub(name="_should_not_be_called")
    yield callback
    callback.assert_not_called()


def pytest_configure() -> None:
    if shutil.which("latexmk") is None:
        pytest.exit(
            "\n\nERROR: 'latexmk' is required but not found on PATH.\n"
            "Install a TeX distribution (TeX Live, MiKTeX, MacTeX) that "
            "includes latexmk, then re-run tests.\n",
            returncode=1,
        )
