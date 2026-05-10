# Design Notes

## Goals

- Reduce LLM token cost by replacing repeated domain phrases with defined shorthand.
- Add domains through data-only packs, without code changes.
- Measure both token usage and answer quality against an uncompressed baseline.
- Report only observed results, including regressions and limitations.

## Legend-Cost Trade-off

Shorthand requires a legend that maps abbreviations back to their domain phrases. The legend consumes tokens, so shorter text alone does not prove net savings. Evaluation must count the legend wherever it is sent, along with compressed input and model output, and compare total cost with the baseline. Sparse repetition may cost more than it saves, and ambiguous shorthand may reduce answer quality.

## Non-Goals

- This step does not implement translation, pack parsing, an evaluation harness, reports, or a UI.
- This scaffold does not call LLM APIs or require API keys.
- No guaranteed token savings or quality preservation is claimed.
- This project does not train models or change model tokenizers.