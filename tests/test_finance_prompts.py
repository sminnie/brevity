"""Offline integrity checks for finance evaluation inputs, not model results."""

import json
import re
from pathlib import Path
from typing import Any

import pytest

from brevity.packs import load_pack
from brevity.translator import compress_with_stats, expand


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def finance_dataset() -> dict[str, Any]:
    """Read the checked-in finance prompt set without invoking a provider."""
    return json.loads((ROOT / "prompts/finance.json").read_text(encoding="utf-8"))


def test_finance_prompt_schema(finance_dataset: dict[str, Any]) -> None:
    """Require stable identifiers, predeclared strata, and nonempty scoring points."""
    assert finance_dataset["schema_version"] == 1
    assert finance_dataset["status"] == "draft_not_run"
    prompts = finance_dataset["prompts"]
    assert len(prompts) == 20
    assert len({prompt["id"] for prompt in prompts}) == 20
    assert {prompt["category"] for prompt in prompts} == {
        "short", "control_none", "control_few", "repeated", "mixed"
    }
    for prompt in prompts:
        assert isinstance(prompt["id"], str) and prompt["id"].strip()
        assert isinstance(prompt["text"], str) and prompt["text"].strip()
        assert isinstance(prompt["short_prompt"], bool)
        assert isinstance(prompt["expected_replacements"], int)
        assert prompt["expected_replacements"] >= 0
        assert isinstance(prompt["expected_points"], list) and prompt["expected_points"]
        assert all(isinstance(point, str) and point.strip() for point in prompt["expected_points"])


def test_finance_prompt_accounting(finance_dataset: dict[str, Any]) -> None:
    """Check phrase occurrences, control labels, and coverage without counting tokens."""
    pack = load_pack(ROOT / finance_dataset["pack_path"])
    seen: set[str] = set()
    for prompt in finance_dataset["prompts"]:
        compressed, replacements = compress_with_stats(prompt["text"], pack)
        count = sum(count for phrase, code, count in replacements)
        assert count == prompt["expected_replacements"], prompt["id"]
        if prompt["category"] == "control_none":
            assert count == 0 and compressed == prompt["text"]
        elif prompt["category"] == "control_few":
            assert count == 1
        elif prompt["category"] == "repeated":
            assert count >= 5
        seen.update(phrase for phrase, code, count in replacements)
        restored = expand(compressed, pack)
        assert " ".join(restored.split()).casefold() == " ".join(prompt["text"].split()).casefold()
    assert seen == set(pack.terms)
    assert sum(prompt["short_prompt"] for prompt in finance_dataset["prompts"]) == 7


def test_finance_legend(finance_dataset: dict[str, Any]) -> None:
    """Require a complete legend and common instructions that need no translation."""
    pack = load_pack(ROOT / finance_dataset["pack_path"])
    assert finance_dataset["legend"] == "\n".join(
        f"{code} = {phrase}" for phrase, code in pack.terms.items()
    )
    instruction = finance_dataset["common_instruction"]
    assert isinstance(instruction, str) and instruction.strip()
    assert compress_with_stats(instruction, pack) == (instruction, [])
    assert not re.search(r"\b(?:IV|IVR|DTE|IR|CR)\b", instruction)