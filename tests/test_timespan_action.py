import argparse

from mplugin import TimespanAction

"""Test the TimeSpanAction class"""

parser = argparse.ArgumentParser()
parser.add_argument("--timeout", action=TimespanAction, type=str)


def test_seconds() -> None:
    """Test TimeSpanAction with seconds."""

    args = parser.parse_args(["--timeout", "5s"])
    assert args.timeout == 5


def test_minutes() -> None:
    """Test TimeSpanAction with minutes."""
    args = parser.parse_args(["--timeout", "2min"])
    assert args.timeout == 120


def test_hours() -> None:
    """Test TimeSpanAction with hours."""
    args = parser.parse_args(["--timeout", "1h"])
    assert args.timeout == 3600


def test_combined() -> None:
    """Test TimeSpanAction with combined timespan."""
    args = parser.parse_args(["--timeout", "1h30m"])
    assert args.timeout == 5400


def test_float() -> None:
    """Test TimeSpanAction with float value."""
    args = parser.parse_args(["--timeout", "1.5h"])
    assert args.timeout == 5400


def test_with_spaces() -> None:
    """Test TimeSpanAction with spaces."""
    args = parser.parse_args(["--timeout", "2 hours 30 minutes"])
    assert args.timeout == 9000


def test_nargs_raises_error() -> None:
    """Test that TimeSpanAction raises error when nargs is provided."""
    try:
        TimespanAction(["--timeout"], "timeout", nargs="*")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "nargs not allowed" in str(e)
