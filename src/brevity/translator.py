"""Translation interfaces; compression and expansion are not implemented yet."""

from collections.abc import Mapping


def compress(text: str, pack: Mapping[str, str]) -> str:
    """Replace domain phrases using a phrase-to-shorthand pack."""
    raise NotImplementedError("Compression is not implemented yet.")


def expand(text: str, pack: Mapping[str, str]) -> str:
    """Restore domain phrases using a phrase-to-shorthand pack."""
    raise NotImplementedError("Expansion is not implemented yet.")