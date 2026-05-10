"""Translator contracts using in-memory packs rather than domain data files."""

import json
import re
from pathlib import Path

import pytest

from brevity.packs import Pack, load_pack
from brevity.translator import CollisionError, compress, compress_with_stats, expand


@pytest.fixture
def pack() -> Pack:
    """Provide overlapping finance phrases for deterministic examples."""
    return Pack(
        name="test",
        terms={
            "implied volatility": "IV",
            "implied volatility rank": "IVR",
            "days to expiration": "DTE",
            "interest rate": "IR",
            "credit risk": "CR",
        },
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("implied volatility rank and implied volatility", "IVR and IV"),
        ("(implied volatility), credit risk!", "(IV), CR!"),
        ("IMPLIED VOLATILITY and Credit Risk", "IV and CR"),
        ("credit risk, credit risk, credit risk", "CR, CR, CR"),
        ("", ""),
        ("Nothing matches here.", "Nothing matches here."),
        ("implied volatility ranks", "IV ranks"),
        ("interest rates and credit risks", "interest rates and credit risks"),
        ("xcredit risk credit risky credit risk_suffix", "xcredit risk credit risky credit risk_suffix"),
        ("implied   volatility\nrank", "IVR"),
        ("days\tto\n expiration", "DTE"),
        ("  credit risk,\n\tinterest rate!  ", "  CR,\n\tIR!  "),
    ],
)
def test_compress(text: str, expected: str, pack: Pack) -> None:
    """Match exact word forms while preserving text outside each match."""
    assert compress(text, pack) == expected


def test_overlapping_phrases() -> None:
    """Consume the leftmost phrase once without reusing its overlapping suffix."""
    pack = Pack(name="overlap", terms={"credit risk": "CR", "risk premium": "RP"})
    assert compress("credit risk premium and risk premium", pack) == "CR premium and RP"


def test_literal_regex_characters() -> None:
    """Escape regex syntax, including non-word characters at phrase edges."""
    pack = Pack(name="literal", terms={"risk (net)": "RN", "C++": "CPP", "a.b": "DOT"})
    assert compress("risk (net), C++; a.b and axb", pack) == "RN, CPP; DOT and axb"
    assert compress("XC++ C++x xa.b a.bx", pack) == "XC++ C++x xa.b a.bx"
    assert expand("RN, CPP; DOT", pack) == "risk (net), C++; a.b"


def test_compression_does_not_rematch_inserted_codes() -> None:
    """Inserted codes are not treated as phrases later in the same pass."""
    pack = Pack(name="cascade", terms={"market risk": "MR", "MR": "ALIAS"})
    assert compress("market risk", pack) == "MR"
    assert compress("market risk and MR", pack, strict=False) == "MR and ALIAS"


@pytest.mark.parametrize("code", ["IV", "IVR", "DTE", "IR", "CR"])
def test_collision(code: str, pack: Pack) -> None:
    """Reject existing standalone codes even when adjacent to punctuation."""
    with pytest.raises(CollisionError):
        compress(f"({code}), credit risk", pack)
    with pytest.raises(CollisionError):
        compress_with_stats(f"({code}), credit risk", pack)


def test_non_colliding_tokens(pack: Pack) -> None:
    """Code substrings and lowercase prose do not count as collisions."""
    text = "XIV IVs _IV IV_ iv dte and credit risk"
    assert compress(text, pack) == "XIV IVs _IV IV_ iv dte and CR"


def test_strict_false(pack: Pack) -> None:
    """Explicit opt-out permits existing codes but only counts substitutions."""
    assert compress("IV and implied volatility", pack, strict=False) == "IV and IV"
    assert compress_with_stats("IV and implied volatility", pack, strict=False) == (
        "IV and IV",
        [("implied volatility", "IV", 1)],
    )


def test_stats(pack: Pack) -> None:
    """Count canonical phrases separately, ordered by their first replacement."""
    assert compress_with_stats(
        "CREDIT RISK, implied volatility rank; credit\nrisk, implied volatility", pack
    ) == (
        "CR, IVR; CR, IV",
        [
            ("credit risk", "CR", 2),
            ("implied volatility rank", "IVR", 1),
            ("implied volatility", "IV", 1),
        ],
    )


@pytest.mark.parametrize("text", ["", "No matching terms."])
def test_no_replacement_stats(text: str, pack: Pack) -> None:
    """Return an empty replacement list when nothing is changed."""
    assert compress_with_stats(text, pack) == (text, [])


def test_expand_is_case_sensitive_and_whole_word(pack: Pack) -> None:
    """Expand standalone codes only, leaving lowercase prose and substrings alone."""
    assert expand("(IV), DTE; iv dte Iv XIV IVs _IV IV_", pack) == (
        "(implied volatility), days to expiration; iv dte Iv XIV IVs _IV IV_"
    )


def test_expand_does_not_rematch_inserted_phrases() -> None:
    """Codes appearing in an inserted phrase are not expanded again."""
    pack = Pack(name="cascade", terms={"BETA value": "ALPHA", "original phrase": "BETA"})
    assert expand("ALPHA BETA", pack) == "BETA value original phrase"


def test_literal_codes() -> None:
    """Escape special characters in code matching and collision detection."""
    pack = Pack(name="literal", terms={"net risk": "R+"})
    assert expand("(R+), RRR and XR+", pack) == "(net risk), RRR and XR+"
    with pytest.raises(CollisionError):
        compress("(R+)", pack)


def test_empty_pack() -> None:
    """An empty pack leaves both translation directions unchanged."""
    pack = Pack(name="empty", terms={})
    assert compress_with_stats("unchanged", pack) == ("unchanged", [])
    assert compress("", pack) == ""
    assert expand("unchanged", pack) == "unchanged"
    assert expand("", pack) == ""


@pytest.mark.parametrize(
    "text",
    [
        "Implied volatility increased today.",
        "The implied volatility rank is high.",
        "Compare implied volatility rank with implied volatility.",
        "Count the days to expiration.",
        "The interest rate changed.",
        "Assess credit risk before trading.",
        "Credit risk and CREDIT RISK refer to the same phrase.",
        "Watch (implied volatility), then credit risk!",
        "There are few days\nto   expiration.",
        "An interest\trate shift can affect credit risk.",
        "No relevant terms appear here.",
        "  IMPLIED VOLATILITY RANK;\ncredit risk.  ",
    ],
)
def test_round_trip(text: str, pack: Pack) -> None:
    """Round trips preserve sentences up to phrase case and whitespace."""
    restored = expand(compress(text, pack), pack)
    assert re.sub(r"\s+", " ", restored).casefold() == re.sub(r"\s+", " ", text).casefold()


def test_load_pack(tmp_path: Path) -> None:
    """Load the minimal JSON template schema without a checked-in domain pack."""
    path = tmp_path / "pack.json"
    path.write_text(json.dumps({"name": "test", "terms": {"credit risk": "CR"}}), encoding="utf-8")
    pack = load_pack(path)
    assert pack.name == "test"
    assert compress("credit risk", pack) == "CR"


@pytest.mark.parametrize(
    "terms",
    [
        {"": "EMPTY"},
        {" term": "PADDED"},
        {"term": ""},
        {"term": "two codes"},
        {"first": "SAME", "second": "SAME"},
        {"credit risk": "CR", "CREDIT  RISK": "OTHER"},
    ],
)
def test_invalid_pack(terms: dict[str, str]) -> None:
    """Reject ambiguous or empty entries before compiling a translator regex."""
    with pytest.raises(ValueError):
        Pack(name="invalid", terms=terms)