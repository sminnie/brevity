# brevity

When does domain shorthand reduce LLM cost, and when does it hurt?

**Status: experimental prototype.** The translator and a local Ollama pilot runner are implemented. A first finance pilot has completed; manual quality scoring and the full reuse/caching study are still pending. Domains are defined as data files ("packs").

See the [experiment pre-registration](docs/experiment.md) for hypotheses, comparison conditions, measurement methods, and reporting rules written before any runs.

Start with the [finance evaluation preparation](docs/finance-evaluation.md) for the prompt set, scoring criteria, limitations, and decisions required before a paid run.

## Results

The first local finance pilot used **27.13% more input tokens with shorthand**, including the legend. Many outputs hit the configured length limit, and quality remains unscored. See the [observed results and limitations](results/finance-ollama-pilot-01.md). No hosted monetary savings are claimed.

## Development

Requires Python 3.10 or newer. No API key is required. Tests run offline; the [local pilot](docs/ollama-pilot.md) makes Ollama calls only when explicitly invoked.

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
  packs.py        Validated JSON pack loading
  translator.py   Compression, expansion, and replacement statistics
  ollama_runner.py Local finance pilot and usage recording
  cli.py          Version-only entry point
packs/            Domain data packs
prompts/          Evaluation prompts
results/          Measured outputs (raw outputs ignored by Git)
tests/            Package, translator, and finance input checks
docs/design.md    Goals, trade-offs, and non-goals
```

A full multi-provider evaluation harness and a UI are not implemented. The local pilot does not yet test reuse break-even or hosted caching.

## Honesty Principle

No fabricated results, ever. Publish only observed measurements, disclose the evaluation setup and limitations, and distinguish planned capabilities from implemented behavior. Token savings must include the shorthand legend's cost; quality preservation must be tested, not assumed.

## License

MIT. Copyright (c) 2026 Minnie Sankhe.