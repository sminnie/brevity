# Repository Instructions

- Treat brevity as an experiment, not a product pitch. Follow the [experiment pre-registration](../docs/experiment.md).
- Never fabricate or estimate results. Use provider usage fields for token counts; report missing usage as missing. Calculate costs only from observed usage and a dated, user-filled price table.
- Token savings always include the legend's cost, including every billed reuse.
- Never commit keys or other secrets. Never run `git push`.
- Use type hints, docstrings, and small functions.
- Run pytest before every commit, including documentation-only commits: `.venv/bin/python -m pytest`. Do not commit if tests fail.
- Do the requested step only. Stop and summarize when done.