"""Minimal domain packs loaded from JSON objects with name and terms fields."""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType


@dataclass(frozen=True)
class Pack:
    """A named, immutable mapping of exact domain phrases to unique codes."""

    name: str
    terms: Mapping[str, str]

    def __post_init__(self) -> None:
        """Validate entries and freeze a copy so later mutation cannot change them."""
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Pack name must be a nonempty string.")
        if not isinstance(self.terms, Mapping):
            raise ValueError("Pack terms must be a phrase-to-code mapping.")
        phrases: set[str] = set()
        codes: set[str] = set()
        for phrase, code in self.terms.items():
            _validate_entry(phrase, code)
            normalized = " ".join(phrase.split()).casefold()
            if normalized in phrases or code in codes:
                raise ValueError("Pack phrases and codes must be unique.")
            phrases.add(normalized)
            codes.add(code)
        object.__setattr__(self, "terms", MappingProxyType(dict(self.terms)))


def _validate_entry(phrase: str, code: str) -> None:
    """Reject empty phrases, surrounding whitespace, and multi-token codes."""
    if not isinstance(phrase, str) or not phrase or phrase != phrase.strip():
        raise ValueError("Phrases must be nonempty strings without surrounding whitespace.")
    if not isinstance(code, str) or not code or any(character.isspace() for character in code):
        raise ValueError("Codes must be nonempty strings without whitespace.")


def load_pack(path: str | Path) -> Pack:
    """Load a JSON object containing a name and a phrase-to-code terms mapping."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "name" not in data or "terms" not in data:
        raise ValueError("Pack JSON must be an object with name and terms fields.")
    return Pack(name=data["name"], terms=data["terms"])