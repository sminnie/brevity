"""Single-pass shorthand translation with exact word forms, not stems or plurals.

Phrase matching ignores case and accepts any internal whitespace run. Match edges
cannot touch a Unicode word character (a letter, digit, or underscore). Literal
punctuation inside phrases is supported; surrounding text is preserved. Expansion
restores the pack's canonical phrase spelling and whitespace, not the original's.
"""

import re
from collections.abc import Sequence

from brevity.packs import Pack


class CollisionError(ValueError):
    """The original input contains an exact-case standalone shorthand code."""


def _compile_pattern(values: Sequence[str], *, phrases: bool = False) -> re.Pattern[str]:
    """Compile literal alternatives with word edges and optional phrase whitespace."""
    alternatives: list[str] = []
    for index, value in enumerate(values):
        pattern = r"\s+".join(re.escape(word) for word in value.split()) if phrases else re.escape(value)
        alternatives.append(f"(?P<term_{index}>{pattern})")
    return re.compile(
        r"(?<!\w)(?:" + "|".join(alternatives) + r")(?!\w)",
        flags=re.IGNORECASE if phrases else 0,
    )


def compress(text: str, pack: Pack, *, strict: bool = True) -> str:
    """Replace longest exact phrases first in one case-insensitive regex pass.

    Existing exact-case code tokens raise CollisionError unless strict=False.
    Opting out allows ambiguous text and can make round trips lossy. No plural
    or stem matching is performed, though a shorter exact phrase may still match.
    """
    return compress_with_stats(text, pack, strict=strict)[0]


def compress_with_stats(
    text: str, pack: Pack, *, strict: bool = True
) -> tuple[str, list[tuple[str, str, int]]]:
    """Compress and count canonical (phrase, code, count) entries in first-use order.

    Only actual substitutions are counted; unchanged codes are not replacements.
    These counts are not token measurements. Collision handling matches compress.
    """
    if not text or not pack.terms:
        return text, []
    if strict:
        collision = _compile_pattern(list(pack.terms.values())).search(text)
        if collision is not None:
            raise CollisionError(f"Input already contains code {collision.group(0)!r}.")
    entries = sorted(pack.terms.items(), key=lambda entry: len(" ".join(entry[0].split())), reverse=True)
    pattern = _compile_pattern([phrase for phrase, code in entries], phrases=True)
    counts: dict[str, int] = {}

    def replace(match: re.Match[str]) -> str:
        """Select the matched alternative and count its canonical phrase once."""
        assert match.lastindex is not None
        phrase, code = entries[match.lastindex - 1]
        counts[phrase] = counts.get(phrase, 0) + 1
        return code

    compressed = pattern.sub(replace, text)
    return compressed, [(phrase, pack.terms[phrase], count) for phrase, count in counts.items()]


def expand(text: str, pack: Pack) -> str:
    """Expand whole-word, case-sensitive codes in one pass without re-matching output."""
    if not text or not pack.terms:
        return text
    phrases_by_code = {code: phrase for phrase, code in pack.terms.items()}
    codes = sorted(phrases_by_code, key=len, reverse=True)
    pattern = _compile_pattern(codes)

    def replace(match: re.Match[str]) -> str:
        """Restore the canonical phrase for the exact code found in the input."""
        return phrases_by_code[match.group(0)]

    return pattern.sub(replace, text)