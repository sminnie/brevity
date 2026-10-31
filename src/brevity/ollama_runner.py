"""Run a pinned, local-only finance pilot without estimating usage or quality."""

import argparse
import hashlib
import http.client
import json
import platform
import random
import statistics
import subprocess
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from brevity.packs import Pack, load_pack
from brevity.translator import compress


MODEL = "qwen2.5:0.5b"
MODEL_DIGEST = "a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67"
REPEATS = 3


def utc_now() -> str:
    """Return the actual UTC clock time, independent of Git timestamps."""
    return datetime.now(timezone.utc).isoformat()


def request_json(path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Call loopback Ollama only, without redirects, proxies, or automatic retries."""
    connection = http.client.HTTPConnection("127.0.0.1", 11434, timeout=180)
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    try:
        connection.request(
            "POST" if payload is not None else "GET", path, body,
            headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        raw = response.read()
        if response.status != 200:
            raise RuntimeError(f"Ollama HTTP {response.status}: {raw.decode('utf-8', errors='replace')[:500]}")
        result = json.loads(raw)
        if not isinstance(result, dict) or "error" in result:
            raise ValueError(f"Invalid Ollama response: {result!r}")
        return result
    finally:
        connection.close()


def build_requests(dataset: dict[str, Any], pack: Pack) -> list[dict[str, Any]]:
    """Prepare all A/B requests with no history, full legends, and balanced order."""
    prompts = dataset["prompts"]
    if len(prompts) != 20 or len({prompt["id"] for prompt in prompts}) != 20:
        raise ValueError("The finance pilot requires twenty uniquely identified prompts.")
    requests: list[dict[str, Any]] = []
    for repeat in range(REPEATS):
        for index, prompt in enumerate(prompts):
            order = ("A", "B") if (index + repeat) % 2 == 0 else ("B", "A")
            for condition in order:
                text = prompt["text"]
                if condition == "B":
                    text = dataset["legend"] + "\n\n" + compress(text, pack)
                requests.append({
                    "id": f"response-{len(requests) + 1:03d}",
                    "prompt_id": prompt["id"],
                    "category": prompt["category"],
                    "short_prompt": prompt["short_prompt"],
                    "repeat": repeat + 1,
                    "condition": condition,
                    "request": {
                        "model": MODEL,
                        "stream": False,
                        "keep_alive": "5m",
                        "options": {"temperature": 0, "seed": repeat, "num_predict": 128, "num_ctx": 2048},
                        "messages": [
                            {"role": "system", "content": dataset["common_instruction"]},
                            {"role": "user", "content": text},
                        ],
                    },
                })
    return requests


def usage_statistics(values: Sequence[Any]) -> dict[str, Any]:
    """Summarize reported counts, leaving totals missing if any count is missing."""
    observed = [value for value in values if type(value) is int and value >= 0]
    return {
        "observed": len(observed),
        "missing": len(values) - len(observed),
        "total": sum(observed) if observed and len(observed) == len(values) else None,
        "mean": statistics.mean(observed) if observed else None,
        "stdev": statistics.stdev(observed) if len(observed) >= 2 else None,
        "min": min(observed) if observed else None,
        "max": max(observed) if observed else None,
    }


def condition_statistics(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize each condition, including incomplete calls and truncated outputs."""
    result: dict[str, Any] = {}
    for condition in ("A", "B"):
        selected = [record for record in records if record["condition"] == condition]
        responses = [record.get("response", {}) for record in selected]
        result[condition] = {
            "calls": len(selected),
            "failed": sum(record["error"] is not None for record in selected),
            "truncated": sum(response.get("done_reason") == "length" for response in responses),
            "input_tokens": usage_statistics([response.get("prompt_eval_count") for response in responses]),
            "output_tokens": usage_statistics([response.get("eval_count") for response in responses]),
            "cached_input_tokens": usage_statistics([response.get("prompt_eval_cached_count") for response in responses]),
        }
    return result


def summarize(records: list[dict[str, Any]], planned: int, validation_error: str | None) -> dict[str, Any]:
    """Report observed usage only, with quality, break-even, and dollar cost unclaimed."""
    conditions = condition_statistics(records)
    failed = sum(record["error"] is not None for record in records)
    complete = len(records) == planned and failed == 0 and validation_error is None
    baseline = conditions["A"]["input_tokens"]["total"]
    shorthand = conditions["B"]["input_tokens"]["total"]
    return {
        "complete": complete,
        "planned_calls": planned,
        "attempted_calls": len(records),
        "completed_calls": len(records) - failed,
        "failed_calls": failed,
        "validation_error": validation_error,
        "conditions": conditions,
        "by_prompt": {
            prompt_id: condition_statistics([record for record in records if record["prompt_id"] == prompt_id])
            for prompt_id in sorted({record["prompt_id"] for record in records})
        },
        "by_category": {
            category: condition_statistics([record for record in records if record["category"] == category])
            for category in sorted({record["category"] for record in records})
        },
        "short_prompts": condition_statistics([record for record in records if record["short_prompt"]]),
        "net_input_tokens_saved": baseline - shorthand if complete and baseline is not None and shorthand is not None else None,
        "cost": None,
        "quality": "pending_manual_scoring",
        "break_even": "not_tested_single_call_pilot",
        "finished_at": utc_now(),
    }


def model_metadata() -> dict[str, Any]:
    """Require the locally installed artifact to match the preregistered model."""
    models = request_json("/api/tags")["models"]
    for model in models:
        if model.get("name") == MODEL:
            if model.get("digest") != MODEL_DIGEST:
                raise ValueError("Installed model digest differs from the pilot protocol.")
            return model
    raise ValueError(f"Required model {MODEL} is not installed; no download will be attempted.")


def snapshot_inputs(root: Path) -> dict[str, Any]:
    """Record exact source and protocol bytes before the first inference request."""
    paths = (
        "prompts/finance.json", "packs/finance.json", "docs/experiment.md",
        "docs/finance-evaluation.md", "docs/ollama-pilot.md",
        "src/brevity/packs.py", "src/brevity/translator.py", "src/brevity/ollama_runner.py",
    )
    snapshots: dict[str, Any] = {}
    for path in paths:
        content = (root / path).read_bytes()
        snapshots[path] = {"sha256": hashlib.sha256(content).hexdigest(), "text": content.decode("utf-8")}
    return snapshots


def write_json(path: Path, value: Any) -> None:
    """Write a new artifact without overwriting any previous run evidence."""
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=True)
        stream.write("\n")


def collect_response(planned: dict[str, Any]) -> dict[str, Any]:
    """Preserve an attempt and its raw response, including failures and missing usage."""
    record = {**planned, "started_at": utc_now(), "response": {}, "error": None}
    try:
        response = request_json("/api/chat", planned["request"])
        record["response"] = response
        if response.get("model") != MODEL or response.get("done") is not True:
            raise ValueError("Response model or completion status does not match the request.")
        if not isinstance(response.get("message", {}).get("content"), str):
            raise ValueError("Response has no assistant text.")
    except (OSError, ValueError, RuntimeError, http.client.HTTPException, KeyboardInterrupt) as error:
        record["error"] = f"{type(error).__name__}: {error}"
    record["finished_at"] = utc_now()
    return record


def scoring_sheet(records: list[dict[str, Any]], dataset: dict[str, Any]) -> list[dict[str, Any]]:
    """Shuffle responses and omit condition labels; leave every manual score blank."""
    prompts = {prompt["id"]: prompt for prompt in dataset["prompts"]}
    sheet: list[dict[str, Any]] = []
    for record in records:
        if record["error"] is not None:
            continue
        prompt = prompts[record["prompt_id"]]
        sheet.append({
            "id": record["id"],
            "prompt_id": prompt["id"],
            "prompt": prompt["text"],
            "response": record["response"]["message"]["content"],
            "truncated": record["response"].get("done_reason") == "length",
            "expected_points": prompt["expected_points"],
            "scores": [None] * len(prompt["expected_points"]),
            "scorer": None,
            "flags": [],
            "notes": "",
        })
    random.Random(20261030).shuffle(sheet)
    return sheet


def run_pilot(root: Path, output: Path) -> dict[str, Any]:
    """Freeze the protocol, run one 120-call local pilot, and save unscored evidence."""
    if output.exists():
        raise FileExistsError(f"Run directory already exists: {output}")
    dataset = json.loads((root / "prompts/finance.json").read_text(encoding="utf-8"))
    planned = build_requests(dataset, load_pack(root / dataset["pack_path"]))
    manifest = {
        "protocol": "finance-ollama-single-call-pilot-v1",
        "started_at": utc_now(),
        "model": model_metadata(),
        "model_details": request_json("/api/show", {"model": MODEL}),
        "ollama": request_json("/api/version"),
        "platform": platform.platform(),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "git_status": subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True),
        "inputs": snapshot_inputs(root),
        "planned_requests": planned,
        "cost": None,
    }
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "manifest.json", manifest)
    records: list[dict[str, Any]] = []
    with (output / "responses.jsonl").open("x", encoding="utf-8") as stream:
        for request in planned:
            record = collect_response(request)
            records.append(record)
            stream.write(json.dumps(record, ensure_ascii=True) + "\n")
            stream.flush()
            if len(records) % 10 == 0 or record["error"] is not None:
                print(f"Recorded {len(records)}/{len(planned)} calls", flush=True)
            if record["error"] is not None:
                break
    validation_error = None
    try:
        model_metadata()
    except (OSError, ValueError, RuntimeError, http.client.HTTPException) as error:
        validation_error = f"{type(error).__name__}: {error}"
    summary = summarize(records, len(planned), validation_error)
    write_json(output / "summary.json", summary)
    write_json(output / "manual-scoring.json", scoring_sheet(records, dataset))
    return summary


def main() -> None:
    """Run from the repository root with an explicitly chosen fresh output directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    summary = run_pilot(Path.cwd(), arguments.output)
    fields = ("complete", "attempted_calls", "failed_calls", "conditions", "net_input_tokens_saved", "quality", "cost")
    print(json.dumps({field: summary[field] for field in fields}, indent=2))
    if not summary["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()