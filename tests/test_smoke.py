"""Smoke test for the initial package scaffold."""

import brevity


def test_package_version() -> None:
    """The package imports and exposes the expected initial version."""
    assert brevity.__version__ == "0.1.0"