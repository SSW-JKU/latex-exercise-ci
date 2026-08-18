from pathlib import Path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture

from latex_build_action.gh.utils import github_action_output

GH_OUTPUT = Path("/mock/github_output")


@pytest.fixture
def set_up_env_var(fs: FakeFilesystem, mocker: MockerFixture) -> None:
    fs.create_file(GH_OUTPUT)
    getenv = mocker.patch("os.getenv")
    getenv.return_value = GH_OUTPUT


def test_github_action_output_no_env_var() -> None:
    result_code = github_action_output(["exercise1"], 0)
    assert not GH_OUTPUT.exists()
    assert result_code == 0


def test_github_action_output_invalid_output_var(fs: FakeFilesystem, mocker: MockerFixture) -> None:
    fs.create_dir(GH_OUTPUT)
    getenv = mocker.patch("os.getenv")
    getenv.return_value = GH_OUTPUT

    with pytest.raises(OSError, match=f"Failed to write to {GH_OUTPUT}"):
        github_action_output(["exercise1"], 0)


@pytest.mark.usefixtures("set_up_env_var")
def test_github_action_output_no_files() -> None:
    result_code = github_action_output([], 0)
    assert GH_OUTPUT.read_text(encoding="UTF-8") == "changed-exercises=\n"
    assert result_code == 0


@pytest.mark.usefixtures("set_up_env_var")
def test_github_action_output_single_file() -> None:
    result_code = github_action_output(["exercise10"], 0)
    assert GH_OUTPUT.read_text(encoding="UTF-8") == "changed-exercises=exercise10\n"
    assert result_code == 0


@pytest.mark.usefixtures("set_up_env_var")
def test_github_action_output_multiple_files() -> None:
    result_code = github_action_output(["exercise1", "exercise2"], 0)
    assert GH_OUTPUT.read_text(encoding="UTF-8") == "changed-exercises=exercise1,exercise2\n"
    assert result_code == 0


@pytest.mark.usefixtures("set_up_env_var")
def test_github_action_output_returns_passed_result_code() -> None:
    result_code = github_action_output(["exercise1"], 199)
    assert result_code == 199
