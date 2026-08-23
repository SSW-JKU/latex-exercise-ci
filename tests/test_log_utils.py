from logging import Logger
from pathlib import Path
from unittest.mock import Mock, call

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture

from latex_build_action.log_utils import print_build_log


@pytest.fixture
def logger(mocker: MockerFixture) -> Mock:
    logger: Mock = mocker.Mock(spec=Logger)
    return logger


def test_print_build_log_noop_if_no_file(logger: Mock, mocker: MockerFixture) -> None:
    log_path: Mock = mocker.Mock(name="_mock_Path", spec=Path)
    log_path.is_file.return_value = False

    print_build_log(logger, log_path)

    log_path.open.assert_not_called()
    logger.info.assert_not_called()


def test_print_build_log_noop_if_empty_file(logger: Mock, fs: FakeFilesystem) -> None:
    log_path = Path("test", "logfile.log")
    fs.create_file(log_path, contents="")
    print_build_log(logger, log_path)

    logger.info.assert_not_called()


def test_print_build_log_prints_all_log_lines(logger: Mock, fs: FakeFilesystem) -> None:
    log_path = Path("test", "logfile.log")
    fs.create_file(log_path, contents="line1\nline2\nline3")
    print_build_log(logger, log_path)

    logger.info.assert_has_calls([call("line1"), call("line2"), call("line3")])
