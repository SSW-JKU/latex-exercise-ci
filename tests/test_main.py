import logging
from argparse import Namespace
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pytest_mock import MockerFixture

from latex_build_action.main import main, setup_logger

if TYPE_CHECKING:
    from latex_build_action.config import Config

type VerboseValue = int | bool | str | None

verbose_value_log_level: list[tuple[VerboseValue, int]] = [
    (1, logging.DEBUG),
    (True, logging.DEBUG),
    ("True", logging.DEBUG),
    ("verbose", logging.DEBUG),
    (0, logging.INFO),
    (False, logging.INFO),
    ("", logging.INFO),
    (None, logging.INFO),
]


@pytest.mark.parametrize(("verbose", "log_level"), verbose_value_log_level)
def test_setup_logger_sets_log_level(mocker: MockerFixture, verbose: VerboseValue, log_level: int) -> None:
    basic_config_fn = mocker.patch("logging.basicConfig")

    setup_logger(Namespace(verbose=verbose))

    basic_config_fn.assert_called_with(format="%(levelname)s: %(message)s", level=log_level)


def test_main_fails_on_missing_config_arg() -> None:
    with pytest.raises(SystemExit):
        main()


def test_main_parses_args_executes_action_and_sets_exit_code(mocker: MockerFixture) -> None:
    args: Namespace = Namespace(config=Path(), verbose=False)
    parse_args_fn = mocker.patch("argparse.ArgumentParser.parse_args")
    parse_args_fn.return_value = args

    config: Config = mocker.stub(name="_mock_Config")
    config_fn = mocker.patch("latex_build_action.config.Config.from_args")
    config_fn.return_value = config

    result_code = 199
    run_action_fn = mocker.patch("latex_build_action.main.run_action")
    run_action_fn.return_value = result_code

    sys_exit_fn = mocker.patch("sys.exit")

    main()

    parse_args_fn.assert_called_once()
    config_fn.assert_called_once_with(args)
    run_action_fn.assert_called_once_with(config)
    sys_exit_fn.assert_called_once_with(result_code)
