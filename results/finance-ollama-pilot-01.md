# Finance Ollama Pilot 01: Token Overhead, Quality Pending

**Observed result:** shorthand increased input tokens by 1,578 (27.13%) across this single-call pilot, including the full legend on every shorthand request. All twenty tested prompts had positive input-token overhead. This is not evidence of hosted dollar savings, a reuse break-even point, or preserved answer quality.

## Run and Evidence

- Actual run: 2026-10-31 03:30:39 through 03:37:41 UTC, from the run manifest and summary. These are runtime dates, not the rewritten commit dates.
- Provider: local Ollama 0.40.12. Model: `qwen2.5:0.5b`, 494.03M parameters, Q4_K_M quantization; digest `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`.
- Design: [pre-run pilot protocol](../docs/ollama-pilot.md), twenty [finance tasks](../prompts/finance.json), three repeats per condition, temperature 0, seeds 0/1/2, context 2048, output limit 128 tokens, no conversation history, A/B order counterbalanced.
- A: original task. B: full legend plus compressed task. Both use the same system instruction and task facts. Expected answers are not provided to the model.
- All 120 planned calls returned completed API responses, with zero recorded request failures or retries. All input, output, and cache count fields were present. Completed API responses include length-limited answers; completion does not imply an adequate answer.
- Local artifacts are in `results/raw/finance-ollama-pilot-01/`: the pre-run manifest and source snapshots, raw requests and responses, per-prompt usage summary, and shuffled manual-scoring sheet. This directory is Git-ignored and is not published by this note. Public reproducibility requires separately publishing the reviewed raw evidence; this narrative alone is not an independently auditable data release.

## Observed Usage

Counts come directly from Ollama response fields. Means and sample standard deviations below are across all sixty calls per condition; they mix task differences with repeat variation. Ranges are observed minimum to maximum. Percentages are calculated from those counts, not estimated token usage.

| Metric | A: long-form | B: legend + shorthand |
| --- | ---: | ---: |
| Input tokens, total | 5,817 | 7,395 |
| Input tokens, mean / SD | 96.95 / 25.00 | 123.25 / 24.56 |
| Input token range | 55 to 144 | 83 to 172 |
| Output tokens, total | 6,197 | 6,638 |
| Output tokens, mean / SD | 103.28 / 41.95 | 110.63 / 33.73 |
| Output token range | 17 to 128 | 27 to 128 |
| Outputs with `done_reason=length` | 40 of 60 | 46 of 60 |
| Reported cached prompt tokens, total | 4,518 | 5,422 |

Cached counts are recorded separately, not added on top of prompt counts. Internal caching was active, so these are not uncached latency or billing comparisons. Monetary cost is not measured; local compute and electricity are not assumed free. Manual quality scores are not available.

### Input Tokens by Category

| Category | Calls per condition | A total | B total | B minus A |
| --- | ---: | ---: | ---: | ---: |
| Short tasks | 15 | 1,041 | 1,461 | 420 |
| No-match controls | 9 | 849 | 1,110 | 261 |
| Single-match controls | 6 | 846 | 1,014 | 168 |
| Repeated-term tasks | 15 | 1,617 | 1,977 | 360 |
| Mixed tasks | 15 | 1,464 | 1,833 | 369 |

The predeclared short-prompt subset includes finance-01 through finance-07, including two controls. Its input totals were 1,494 for A and 2,088 for B: 594 added tokens (39.76%). This is consistent with H2 on these tested prompts only. Repeated-term examples did not offset legend overhead at the tested repetition density.

### Three-Repeat Variability

Each row shows mean input tokens and mean / sample SD output tokens over three repeats per condition. Every per-prompt input-token SD was zero. Output variation exists despite temperature 0; the repeats use different seeds, and no independence or statistical significance is claimed. Output lengths at the cap are censored, not evidence of stable answer quality.

| Prompt | A input mean | B input mean | A output mean / SD | B output mean / SD |
| --- | ---: | ---: | ---: | ---: |
| finance-01 | 55 | 83 | 19.00 / 3.46 | 30.33 / 2.89 |
| finance-02 | 73 | 101 | 128.00 / 0.00 | 128.00 / 0.00 |
| finance-03 | 79 | 107 | 121.33 / 4.04 | 128.00 / 0.00 |
| finance-04 | 55 | 83 | 26.00 / 0.00 | 33.00 / 0.00 |
| finance-05 | 85 | 113 | 128.00 / 0.00 | 128.00 / 0.00 |
| finance-06 | 78 | 107 | 128.00 / 0.00 | 128.00 / 0.00 |
| finance-07 | 73 | 102 | 128.00 / 0.00 | 128.00 / 0.00 |
| finance-08 | 132 | 161 | 128.00 / 0.00 | 128.00 / 0.00 |
| finance-09 | 144 | 172 | 122.67 / 9.24 | 128.00 / 0.00 |
| finance-10 | 138 | 166 | 128.00 / 0.00 | 128.00 / 0.00 |
| finance-11 | 103 | 127 | 68.67 / 51.38 | 128.00 / 0.00 |
| finance-12 | 97 | 121 | 128.00 / 0.00 | 128.00 / 0.00 |
| finance-13 | 103 | 127 | 128.00 / 0.00 | 108.67 / 16.74 |
| finance-14 | 125 | 149 | 100.67 / 47.34 | 128.00 / 0.00 |
| finance-15 | 111 | 135 | 126.67 / 2.31 | 128.00 / 0.00 |
| finance-16 | 109 | 132 | 128.00 / 0.00 | 128.00 / 0.00 |
| finance-17 | 79 | 106 | 38.33 / 1.15 | 57.00 / 0.00 |
| finance-18 | 91 | 113 | 34.33 / 9.24 | 63.67 / 12.42 |
| finance-19 | 104 | 128 | 128.00 / 0.00 | 128.00 / 0.00 |
| finance-20 | 105 | 132 | 128.00 / 0.00 | 128.00 / 0.00 |

## Where It Breaks

- **Legend overhead:** B used more input tokens for every tested prompt. No-match controls still carry the full legend, as required by the protocol.
- **Output truncation:** 86 of 120 responses reached the 128-token limit. The original run is retained unchanged. Do not claim quality preservation or reliable uncapped output-cost comparisons from these outputs. Any higher-limit run must be preregistered separately, not silently substituted for this one.
- **Errors can occur in either condition:** raw response `response-040` (finance-20, A, repeat 1) introduces assumed values of 20%, 15%, and 25% instead of the supplied equal values. `response-039` (the matched B call) conflates the formula inputs with different domain labels. These are inspection notes for manual review, not assigned rubric scores or a measured quality difference.
- **Unsupported elaboration:** `response-022` (finance-11, B, repeat 1) emits an unrelated nested formula instead of simply ranking supplied values. The matched A output, `response-021`, also starts an incorrect ordering and is truncated. These examples show why correctness must be scored separately from token totals; they do not establish how often shorthand causes errors.
- **Small-model and task limits:** one quantized 494.03M-parameter model on twenty synthetic finance tasks cannot establish effects on other models, domains, or production workloads.

## Remaining Work

Human scoring of the shuffled review sheet is pending. H1's reuse break-even, H3's model-size comparison, and H4's hosted caching comparison remain untested. Any continuation should record a new protocol revision, preserve this negative pilot, and address the output cap before treating a follow-up as a quality comparison.