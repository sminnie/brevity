"""Minimal version-only command-line entry point."""

from brevity import __version__


def main() -> None:
    """Print the package version without calling any external service."""
    print(__version__)


if __name__ == "__main__":
    main()