import argparse

import pytest

from mplugin import setup_argparser


def test_basic_creation() -> None:
    parser = setup_argparser("test")
    assert isinstance(parser, argparse.ArgumentParser)
    assert parser.prog == "check_test"


def test_name_already_prefixed() -> None:
    parser = setup_argparser("check_test")
    assert parser.prog == "check_test"


def test_version_in_description() -> None:
    parser = setup_argparser("test", version="1.0.0")
    assert parser.description
    assert "version 1.0.0" in parser.description


def test_license_in_description() -> None:
    parser = setup_argparser("test", license="MIT")
    assert parser.description
    assert "Licensed under the MIT." in parser.description


def test_repository_in_description() -> None:
    parser = setup_argparser("test", repository="https://github.com/test/repo")
    assert parser.description
    assert "Repository: https://github.com/test/repo." in parser.description


def test_copyright_in_description() -> None:
    parser = setup_argparser("test", copyright="Copyright 2024")
    assert parser.description
    assert "Copyright 2024" in parser.description


def test_description_appended() -> None:
    parser = setup_argparser("test", description="A test plugin")
    assert parser.description
    assert "A test plugin" in parser.description


def test_epilog() -> None:
    parser = setup_argparser("test", epilog="Some epilog text")
    assert parser.epilog == "Some epilog text"


def test_verbose_flag() -> None:
    parser = setup_argparser("test", verbose=True)
    args = parser.parse_args(["-v"])
    assert args.verbose == 1


def test_verbose_multiple() -> None:
    parser = setup_argparser("test", verbose=True)
    args = parser.parse_args(["-vvv"])
    assert args.verbose == 3


def test_verbose_default() -> None:
    parser = setup_argparser("test", verbose=True)
    args = parser.parse_args([])
    assert args.verbose == 0


def test_no_verbose_by_default() -> None:
    parser = setup_argparser("test", verbose=False)
    with pytest.raises(SystemExit):
        parser.parse_args(["-v"])


def test_all_parameters() -> None:
    parser = setup_argparser(
        name="test",
        version="1.2.3",
        license="GPL",
        repository="https://example.com",
        copyright="Copyright 2024",
        description="Test description",
        epilog="Test epilog",
        verbose=True,
    )
    assert parser.prog == "check_test"
    assert parser.description
    assert "version 1.2.3" in parser.description
    assert "GPL" in parser.description
    assert "https://example.com" in parser.description
    assert "Copyright 2024" in parser.description
    assert "Test description" in parser.description
    assert parser.epilog == "Test epilog"


def test_formatter_class() -> None:
    parser = setup_argparser("test")
    assert isinstance(
        parser.formatter_class(prog="prog"),
        argparse.RawDescriptionHelpFormatter,
    )


def test_custom_exit_code() -> None:
    parser = setup_argparser("test", version="1.0")
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--version"])
    assert exc_info.value.code == 3
