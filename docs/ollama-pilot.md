# Local Finance Pilot: Pre-Run Protocol

This supplement is written before local inference. It narrows the [experiment](experiment.md) to a single-call pilot, not the full reuse or cross-model study. The [finance preparation](finance-evaluation.md) defines the prompt strata and manual rubric. Actual timestamps and exact input snapshots will be recorded in each run manifest; rewritten Git dates do not establish preparation time.

## Fixed Configuration

- Provider: local Ollama at `127.0.0.1:11434`, without proxies, remote services, model downloads, or API keys.
- Model: `qwen2.5:0.5b`; digest `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`. The installed artifact reports 494.03M parameters and Q4_K_M quantization. Capture `/api/show`, the tag metadata, and the installed Ollama version before running; reject a mismatched digest.
- Inputs: all twenty finance tasks and the full five-entry legend. Expected points are never sent to the model.
- Conditions: A is the original task; B is the full legend, two newline characters, then the compressed task. Both receive the identical common system instruction.
- Sampling: temperature 0, seeds 0/1/2 for repeat 1/2/3, output limit 128 tokens, context size 2048, non-streaming responses, model keep-alive 5 minutes. All other model defaults are captured in metadata. Record truncated responses rather than silently increasing the limit after seeing results.
- Schedule: three complete repetitions in fixed prompt ID order. A runs first when zero-based prompt index plus zero-based repeat index is even; otherwise B runs first. Each repetition has ten A-first and ten B-first pairs.
- Workload: one task per fresh chat; no prior messages or assistant responses are reused. Every B request includes the complete legend, including no-match controls. Planned generation calls: 20 prompts times 3 repeats times 2 conditions = 120.
- Transport: sequential loopback requests; 180-second timeout per HTTP operation; stop on the first request error or interruption. No automatic retries or replacement runs. Save all available evidence, including an incomplete-run summary.

## Measurements and Limits

Use only Ollama's `prompt_eval_count` and `eval_count` for input and output token counts. Preserve every raw response, including timing, completion reason, and `prompt_eval_cached_count` where supplied. Missing or invalid usage remains missing. Totals are withheld for groups with missing usage; means and spread explicitly report their observation counts. Include output truncation counts.

Report A/B totals, per-call mean, sample standard deviation, minimum and maximum, plus per-prompt and category breakdowns. Aggregate variability across different tasks is not repeat variability; use each prompt's three repeats for that comparison. Net input tokens saved means A minus B including the full legend; negative values indicate added tokens. It is not a monetary saving.

Ollama may reuse internal caches. Capture exposed cache fields and do not call this an uncached latency benchmark. Local token counts do not describe hosted billing or electricity cost. Monetary cost remains null: local execution is not evidence of zero resource cost, and no hosted price table is applied.

This pilot can inform H2 and reveal candidate H3 failures for manual review. It does not test H1's reuse break-even, H3's model-size comparison, or H4's hosted prefix caching. The installed Qwen and Llama models differ in family and quantization, so comparing them would not isolate model size. No generalization to larger models, other domains, or production savings is permitted.

## Manual Quality Review

Generate a separate review sheet with shuffled response order (shuffle seed 20261030), original prompts, expected points, and blank 0/1/2 scores. Omit condition labels and usage from this sheet; retain the ID-to-condition mapping in raw records. A reviewer with access to raw records could unblind it, and shorthand in the responses may also reveal the condition. Disclose these limitations.

The coding assistant does not fill the manual scores. Quality remains pending until a human reviews the responses, records contradictions and unsupported claims, and identifies their scoring decisions. Do not infer quality preservation from a successful HTTP response, passing unit tests, or identical token counts. No secondary LLM judge is used.

## Artifacts and Execution

From the repository root, run the offline tests first, then explicitly start the local pilot with a new output directory:

```sh
.venv/bin/python -m pytest
.venv/bin/python -m brevity.ollama_runner --output results/raw/finance-ollama-pilot-01
```

The runner writes a manifest before its first generation call, snapshots source and protocol contents with SHA-256 hashes, and appends each raw response immediately. It writes an observed-usage summary and an unscored manual-review sheet afterward. It refuses to overwrite an existing run. Raw artifacts remain in the Git-ignored `results/raw/` directory; any public results must link to separately reviewed evidence and prominently include failures, missing observations, truncation, and the pending quality assessment.