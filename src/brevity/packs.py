"""Domain pack-loading interface; loading is not implemented yet."""

from pathlib import Path


def load_pack(path: str | Path) -> dict[str, str]:
    """Load a phrase-to-shorthand mapping from a domain data file."""
    raise NotImplementedError("Pack loading is not implemented yet.")