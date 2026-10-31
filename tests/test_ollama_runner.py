"""Offline runner tests using synthetic responses, never live model results."""

import json
from pathlib import Path
from typing import Any

import pytest

from brevity import ollama_runner as runner
from brevity.packs import load_pack


ROOT = Path(__file__).resolve().parents[1]


def dataset() -> dict[str, Any]:
    """Load the real finance inputs for request-construction checks."""
    return json.loads((ROOT / "prompts/finance.json").read_text(encoding="utf-8"))


def test_request_schedule() -> None:
    """Cover all prompts three times in both conditions with balanced order."""
    inputs = dataset()
    requests = runner.build_requests(inputs, load_pack(ROOT / inputs["pack_path"]))
    assert len(requests) == 120
    for repeat in (1, 2, 3):
        batch = [request for request in requests if request["repeat"] == repeat]
        assert len(batch) == 40
        assert sum(request["condition"] == "A" for request in batch[::2]) == 10
        assert {request["prompt_id"] for request in batch} == {
            prompt["id"] for prompt in inputs["prompts"]
        }
    for request in requests:
        payload = request["request"]
        assert payload["model"] == runner.MODEL
        assert payload["stream"] is False
        assert payload["options"]["temperature"] == 0
        assert payload["options"]["num_predict"] == 128
        assert len(payload["messages"]) == 2
        assert payload["messages"][0]["content"] == inputs["common_instruction"]
        assert "expected_points" not in json.dumps(payload)
        if request["condition"] == "B":
            assert payload["messages"][1]["content"].startswith(inputs["legend"] + "\n\n")


def test_no_match_control_keeps_legend() -> None:
    """Do not remove shorthand teaching overhead when a task has no matches."""
    inputs = dataset()
    requests = runner.build_requests(inputs, load_pack(ROOT / inputs["pack_path"]))
    baseline, shorthand = sorted(
        [item for item in requests if item["prompt_id"] == "finance-06" and item["repeat"] == 1],
        key=lambda item: item["condition"],
    )
    assert shorthand["request"]["messages"][1]["content"] == (
        inputs["legend"] + "\n\n" + baseline["request"]["messages"][1]["content"]
    )


@pytest.fixture
def fake_api(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """Replace all HTTP access with clearly synthetic local test responses."""
    calls: list[dict[str, Any]] = []

    def request(path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Return deterministic fixtures for metadata and inference endpoints."""
        if path == "/api/version":
            return {"version": "test-fixture"}
        if path == "/api/tags":
            return {"models": [{"name": runner.MODEL, "digest": runner.MODEL_DIGEST}]}
        if path == "/api/show":
            return {"details": {"parameter_size": "test-fixture"}}
        assert path == "/api/chat" and payload is not None
        calls.append(payload)
        return {
            "model": runner.MODEL,
            "done": True,
            "done_reason": "stop",
            "message": {"role": "assistant", "content": "Synthetic test response."},
            "prompt_eval_count": 42,
            "eval_count": 7,
        }

    monkeypatch.setattr(runner, "request_json", request)
    return calls


def test_run_freezes_inputs_and_leaves_quality_unscored(
    tmp_path: Path, fake_api: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Persist inputs before inference and retain raw usage without invented scores."""
    output = tmp_path / "pilot"
    original = runner.request_json

    def checked_request(path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Require the pre-run manifest to exist before the first model call."""
        if path == "/api/chat":
            manifest = json.loads((output / "manifest.json").read_text())
            assert len(manifest["planned_requests"]) == 120
            assert manifest["inputs"]["prompts/finance.json"]["sha256"]
        return original(path, payload)

    monkeypatch.setattr(runner, "request_json", checked_request)
    summary = runner.run_pilot(ROOT, output)
    assert len(fake_api) == 120
    assert summary["complete"] is True
    assert summary["conditions"]["A"]["input_tokens"]["total"] == 60 * 42
    assert summary["net_input_tokens_saved"] == 0
    assert summary["cost"] is None
    assert summary["quality"] == "pending_manual_scoring"
    raw = [json.loads(line) for line in (output / "responses.jsonl").read_text().splitlines()]
    assert len(raw) == 120 and raw[0]["response"]["prompt_eval_count"] == 42
    scoring = json.loads((output / "manual-scoring.json").read_text())
    assert len(scoring) == 120
    for item in scoring:
        assert "condition" not in item
        assert item["scores"] == [None] * len(item["expected_points"])


def test_existing_output_is_not_overwritten(tmp_path: Path, fake_api: list[dict[str, Any]]) -> None:
    """A repeated invocation cannot silently overwrite a previous run."""
    with pytest.raises(FileExistsError):
        runner.run_pilot(ROOT, tmp_path)
    assert fake_api == []


def test_failure_stops_without_retry(
    tmp_path: Path, fake_api: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Retain failed attempts and leave missing counts unfilled."""
    original = runner.request_json

    def failing_request(path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Simulate one transport error after successful metadata calls."""
        if path == "/api/chat":
            raise TimeoutError("synthetic timeout")
        return original(path, payload)

    monkeypatch.setattr(runner, "request_json", failing_request)
    summary = runner.run_pilot(ROOT, tmp_path / "failed")
    assert summary["attempted_calls"] == 1
    assert summary["failed_calls"] == 1
    assert summary["complete"] is False
    assert summary["net_input_tokens_saved"] is None
    assert summary["conditions"]["A"]["input_tokens"]["total"] is None


def test_model_digest_must_match(
    tmp_path: Path, fake_api: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Refuse a different model artifact before making inference calls."""
    original = runner.request_json

    def changed_model(path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Return a mismatched tag digest rather than a changed response."""
        if path == "/api/tags":
            return {"models": [{"name": runner.MODEL, "digest": "different"}]}
        return original(path, payload)

    monkeypatch.setattr(runner, "request_json", changed_model)
    with pytest.raises(ValueError, match="digest"):
        runner.run_pilot(ROOT, tmp_path / "mismatch")
    assert fake_api == []


@pytest.mark.parametrize("missing", [None, -1, True, "42"])
def test_missing_usage_is_not_estimated(missing: Any) -> None:
    """Incomplete or invalid usage cannot produce a complete token total."""
    summary = runner.usage_statistics([42, missing])
    assert summary["observed"] == 1
    assert summary["missing"] == 1
    assert summary["total"] is None
    assert summary["mean"] == 42