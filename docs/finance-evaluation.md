# Finance Evaluation Preparation

Status: inputs prepared; the full experiment is not complete. A narrower [local Ollama pilot](ollama-pilot.md) has run with [observed usage and limitations](../results/finance-ollama-pilot-01.md); manual quality scoring remains pending. Follow the [pre-registration](experiment.md).

## Inputs

- [Finance pack](../packs/finance.json): five phrase-to-code mappings. These are examples to test, not proven token-efficient codes.
- [Finance prompts](../prompts/finance.json): twenty synthetic tasks with stable IDs, a full legend, common instructions, and manual `expected_points`. Expected points are scoring criteria, not observed model answers. These tasks are not investment advice or a representative sample of professional finance work.
- [Offline checks](../tests/test_finance_prompts.py): schema, legend completeness, control labels, phrase-replacement counts, and translation round trips. Passing these checks does not establish model quality or token savings.

The categories are five short tasks, three no-match controls, two single-match controls, five repeated-term tasks, and five mixed tasks. The predeclared short-prompt subset is finance-01 through finance-07, including two controls. This is a qualitative subset label, not a token-length measurement.

Mixed tasks exercise overlapping phrases, exact word forms, whitespace and capitalization, insufficient information, and a zero-denominator calculation. Repeated-term tasks deliberately favor repetition; report them separately so they cannot conceal overhead on short prompts or controls. The sample is small, synthetic, and skewed toward arithmetic, extraction, and basic definitions.

`expected_replacements` counts phrase substitutions in the task text only. It is not a token count. Do not infer savings from it or from character length.

## Matched Inputs and Scoring

Use the same common instruction and task facts for all conditions. A receives the original task text. B receives the complete legend plus the compressed task text. Do not compress the legend, and do not send `expected_points`, category labels, or replacement counts to the model. For no-match controls, B still receives the legend; otherwise its overhead would be hidden. C, if supported and selected, receives the same long-form content as A through the documented caching configuration.

Score each expected point as 0, 1, or 2 using the pre-registration's rubric. Accept equivalent correct wording and mathematically equivalent answers. Record contradictions, unsupported claims, and shorthand confusion separately. Freeze any scoring clarifications before running; later changes must be recorded as amendments.

For each reuse setting, evaluate all twenty tasks, not just the first 1 or 5. Partition the fixed ID order into workloads of 1, 5, or 20 prompts and repeat the entire set at least three times per condition. This keeps the task mix constant across reuse settings. Fix condition ordering and conversation/history handling before runs. Reset each workload between independent repetitions.

Grouping calls does not make legend tokens free. If the provider bills the legend on every follow-up, count every occurrence. Whether the legend is resent, retained in conversation history, or cached must be explicit. A stateless per-call protocol without caching may show no amortization at all; report that outcome without subtracting hypothetical savings.

## Before a Paid Run

The following are deliberately not selected yet; this dataset is not a complete frozen run configuration:

1. Provider and exact model IDs/versions. H3 needs a documented size comparison; otherwise its smaller-model claim remains untested.
2. Temperature 0 or the lowest supported setting, output limits, the exact rendered messages and separators, condition order, and retry policy.
3. History transport for each reuse setting, cache eligibility and behavior, and whether optional condition C is feasible. Do not pad only one condition to meet a cache threshold.
4. A user-filled price table with current input/output and applicable cache rates, billing units, currency, source, and effective/entry dates. No prices are guessed here.
5. An approved spending cap and request limit, including setup, retries, and cache warm-up. With twenty prompts, three repeats, three reuse settings, and A/B, the planned minimum is 360 generation calls per model; adding C makes it 540. These are planned call counts, not measured usage or costs.
6. Prompt, pack, legend, and rubric revisions recorded alongside the final run configuration. Record actual run dates; rewritten Git timestamps are not evidence of pre-registration timing.

Only after these choices are fixed should provider integration and paid execution proceed. Keep all missing usage explicitly missing, and publish negative and mixed outcomes as prominently as positive ones.