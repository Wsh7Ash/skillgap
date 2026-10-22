# skillgap

Find the coverage gaps and ambiguities in an agent skill corpus *before*
production does. `skillgap` replays a set of example user inputs against your
skills' declared triggers and flags the two routing failures that are invisible
until real traffic hits:

- **gap** — an example that matches *no* skill (an intent you serve poorly or not at all)
- **ambiguity** — an example that matches *more than one* skill (routing is unclear)

It also lists skills that no example ever triggers (possibly dead or
over-specific). Offline, deterministic, dependency-free.

## How matching works

A skill triggers if any of its trigger phrases appears in the input after
normalization (lowercased, whitespace collapsed), matched on whole words so a
trigger like `ploy` does not fire inside `deploy`. Multi-word triggers like
`ship to production` work as phrases.

## Install

```
pip install -e .
```

## Usage

```
skillgap corpus.json --examples examples.txt
```

`corpus.json`:

```json
[
  {"name": "deploy",  "triggers": ["deploy", "ship to production"]},
  {"name": "rollback","triggers": ["rollback", "revert"]}
]
```

`examples.txt` is one example input per line (or pipe them via stdin). Pass
`--fail-on-issues` to exit `1` when any gap or ambiguous example is found, so it
drops into CI as a regression gate.

## Python API

```python
from skillgap import Skill, evaluate, render_report

skills = [Skill("deploy", triggers=["deploy"])]
results = evaluate(["please deploy this", "weather?"], skills)
print(render_report(results, skills))
```

## License

MIT
