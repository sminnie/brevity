# brevity

When does domain shorthand reduce LLM cost, and when does it hurt?

**Status: early scaffold.** The translator and evaluation are not yet implemented, and no savings or quality results have been measured. Domains will be added as data files ("packs"), with no code changes.

See the [experiment pre-registration](docs/experiment.md) for hypotheses, comparison conditions, measurement methods, and reporting rules written before any runs.

## Results

No results yet.

## Development

Requires Python 3.10 or newer. No API key is required, and this scaffold makes no LLM API calls.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest
brevity
```

The CLI currently prints only the package version. The optional key placeholders in `.env.example` are unused.

## Planned Structure

```text
src/brevity/
  __init__.py     Package version
  packs.py        Pack-loading stub
  translator.py   Compression and expansion stubs
  cli.py          Version-only entry point
packs/            Domain data packs
prompts/          Evaluation prompts
results/          Measured outputs (raw outputs ignored by Git)
tests/            Smoke test
docs/design.md    Goals, trade-offs, and non-goals
```

An evaluation harness, reports, and a UI are future work, not part of this scaffold.

## Honesty Principle

No fabricated results, ever. Publish only observed measurements, disclose the evaluation setup and limitations, and distinguish planned capabilities from implemented behavior. Token savings must include the shorthand legend's cost; quality preservation must be tested, not assumed.

## License

MIT. Copyright (c) 2026 Minnie Sankhe.