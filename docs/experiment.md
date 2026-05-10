# When does domain shorthand reduce LLM cost, and when does it hurt?

Pre-registration, written before any experimental runs. No results yet. Freeze the prompt set, packs, model selections, settings, scoring rubric, and dated price table before collecting results; record subsequent changes as amendments, not retroactive hypotheses.

## Question and Why It Matters

Repeated domain phrases consume tokens. Replacing them with shorthand might reduce input length, but the shorthand must be taught to the model through a legend, which also consumes tokens. Does the measured reduction outweigh that overhead, and does answer quality suffer? Neither savings nor quality preservation is assumed.

## Hypotheses

- **H1:** Net input-token savings, including the legend, are positive only when each legend is reused across enough calls: a break-even point exists. Positive savings on the first call would contradict the required-reuse claim; no crossing in the tested reuse conditions would leave a break-even point unobserved, not justify inventing one.
- **H2:** Shorthand on short single prompts is net-negative or near zero. Before runs, label the short-prompt subset; define near zero as an absolute net input-token change of at most 1% of baseline input tokens. Positive savings above that band would contradict H2 for those prompts.
- **H3:** Shorthand lowers answer quality on some prompts, with a larger decrease on smaller models. A smaller model means a documented lower-parameter model in a comparable model family, not merely a cheaper model. Preselect the comparison before runs; if size information is unavailable, mark the size claim untested. No observed quality loss, or equal or smaller losses on the smaller model, would count against the corresponding prediction.
- **H4:** Prompt caching of a long-form prefix may match or beat shorthand on cost for repeated prefixes. This is tested, not assumed. When caching is supported, compare measured total costs; higher cached-baseline costs would count against this prediction for that setup.

## Conditions Compared

Use the same underlying prompts, expected answers, model, and generation settings within every comparison. Repeat the comparison separately for each selected model.

- **A: Long-form baseline.** Use the original domain phrases without shorthand.
- **B: Legend + shorthand.** Supply the phrase-to-shorthand legend and the corresponding shorthand prompt, preserving the task and information in A.
- **C (optional): Cached long-form baseline.** Use the same long-form content with provider prompt caching where supported. Record cache eligibility, writes, hits, misses, and expiry; unsupported caching is untested, not a failed result.

Keep A and B uncached where the provider permits. If caching is automatic or cannot be disabled, disclose the actual cache usage and do not label those runs uncached. Include cache setup and warm-up costs in C rather than reporting only warm hits.

## Metrics

- **Input and output tokens:** Use provider usage fields only, never estimates or local tokenizer counts. Preserve provider-reported cached-input, cache-write, and other separately billed usage categories where applicable. Flag missing usage; do not fill gaps with guessed counts or costs.
- **Net input-token savings:** Compare A's total input tokens with B's over the same workload, including every billed occurrence of the legend. Report the difference and its fraction of A's total. Cached tokens remain input tokens even when charged at a different rate; follow the provider's field definitions to avoid double-counting.
- **Cost:** Apply a configurable, user-filled price table to observed usage. Record the current rates, currency, billing units, provider, exact model, source, effective date, and date entered before runs. Include input, output, cache-read, and cache-write rates where relevant. Leave monetary cost unreported if required prices or usage are missing. These are calculated costs under the stated table, not claimed invoice totals.
- **Quality:** Score manually against each prompt's predeclared `expected_points`, using the rubric below. Report paired differences between conditions, not just aggregate scores.
- **Break-even calls:** Report input-token break-even and monetary break-even separately. For each model and workload, identify the first tested call count with positive cumulative savings, including setup and legend costs. If a crossing falls between tested counts, report that interval rather than an invented exact number. If none is observed, say so; do not extrapolate.

## Method

1. Before runs, freeze the actual prompts, `expected_points`, domain pack, legend, model identifiers and versions, output limits, dated prices, and condition settings. Include control prompts with few or no matching terms and a prelabelled short single-prompt subset. Record the pack and prompt revisions.
2. Use temperature 0 or the lowest available value, with identical settings within each model comparison. Record unsupported controls and any provider defaults. Low temperature does not guarantee identical answers.
3. Vary reuse by sending a legend with workloads of **1, 5, and 20 follow-up prompts**. Use matched long-form workloads for A and C. Keep non-legend conversation content and history policy equivalent between conditions; reset between independent repetitions. Record the exact request structure and whether prior turns are resubmitted.
4. Count actual provider usage for every call, including any separate setup request. A legend shown once in a conversation may still be billed on later calls when history is resent. Do not divide its cost by the number of calls unless the measured billing actually supports that accounting. Report each tested reuse count independently.
5. Run at least **3 independent repeats per prompt per condition per reuse setting**. Repeat complete workloads so every prompt has the required repetitions. Balance condition order and record it. Log failures and retries, their available usage and costs, and any exclusions; never select only favorable responses.
6. Report the mean, standard deviation, and minimum/maximum across repeats for tokens, calculated cost, and quality. Show per-prompt paired differences and aggregates, separating controls, short prompts, reuse settings, and models. Report missing observations and completed repeat counts. Small samples describe variability, not broad statistical certainty.

## Quality

Write each prompt's `expected_points` before running it. Score each point manually: 0 for absent or incorrect, 1 for partially correct, and 2 for fully correct. Divide the sum by the maximum possible score for a normalized prompt score. Prompts must have at least one expected point. Document scoring decisions and separately flag contradictions, unsupported claims, and shorthand confusion rather than hiding them in an average.

Have scorers review outputs in a shuffled order with condition labels hidden where feasible; note when shorthand itself reveals the condition. Use the same rubric for A, B, and C. Record disagreements and how they were resolved when more than one scorer is available; disclose single-scorer subjectivity otherwise.

An optional LLM judge is secondary only and must never be presented as ground truth or replace manual scores. If later used, disclose its model, prompt, settings, disagreements with manual scores, and usage and cost separately from the experiment's primary generation costs.

## Reporting Rules

- Publish negative and mixed results as prominently as positive ones. Evaluate every hypothesis, including untested or inconclusive outcomes.
- Include a **Where it breaks** section with observed failures, affected prompts, and examples, including any quality regression or legend overhead that erased savings.
- State model names, exact versions or provider identifiers, run dates, settings, prompt and pack revisions, cache behavior, price-table date, repeat counts, and limitations. Disclose when a provider does not expose a fixed model version.
- Separate token reductions, calculated monetary savings, and quality outcomes. Lower input-token counts alone do not establish lower total cost or acceptable quality.
- Publish the manual rubric, expected points, and observed measurements needed to interpret the findings. Never fabricate results, conceal missing usage, or present an LLM judge as authoritative.
- Never extrapolate beyond the tested prompts, workloads, models, settings, and domains. Record deviations from this pre-registration explicitly.

## Out of Scope

Claims about production savings and other domains until tested are out of scope. This document specifies a future experiment; it does not implement translation or evaluation, run an experiment, or establish that shorthand helps.