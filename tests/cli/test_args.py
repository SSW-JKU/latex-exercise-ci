#!/usr/bin/env python

from argparse import ArgumentParser
from pathlib import Path

import pytest

from latex_build_action.cli.args import create_parser


@pytest.fixture
def parser() -> ArgumentParser:
    return create_parser()


def test_parser_minimal_args(parser: ArgumentParser) -> None:
    args = parser.parse_args(["-c", "no-file.json"])

    assert args.config == Path("no-file.json")
    assert args.workdir == Path()
    assert not args.no_git
    assert not args.abort_on_error
    assert not args.abort_all_on_error
    assert not args.rollback_on_error
    assert not args.rehash_on_error
    assert not args.verbose


def test_parser_short_form_args(parser: ArgumentParser) -> None:
    args = parser.parse_args(["-c", "no-file.json", "-d", "myworkdir", "-v"])

    assert args.config == Path("no-file.json")
    assert args.workdir == Path("myworkdir")
    assert not args.no_git
    assert not args.abort_on_error
    assert not args.abort_all_on_error
    assert not args.rollback_on_error
    assert not args.rehash_on_error
    assert args.verbose


def test_parser_all_args_long_form(parser: ArgumentParser) -> None:
    args = parser.parse_args(
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

    assert args.config == Path("no-file.json")
    assert args.workdir == Path("myworkdir")
    assert args.no_git
    assert args.abort_on_error
    assert args.abort_all_on_error
    assert args.rollback_on_error
    assert args.rehash_on_error
    assert args.verbose
