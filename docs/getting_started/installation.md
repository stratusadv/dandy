# Installation

## Requirements

- Python **3.11+** (classifiers cover 3.11–3.14).
- An API key for any OpenAI-compatible chat-completions endpoint.

## Prerequisites

- **Pydantic** — Dandy's [Intel](../user_guide/intel.md) classes are pydantic models,
  and validation is where most of the framework's behavior comes from. A working
  familiarity with pydantic v2 (fields, defaults, `BaseModel`) pays off immediately:
  [pydantic.dev](https://docs.pydantic.dev/latest/).
- **Typing** — signatures carry meaning: tool parameters and Intel schemas are derived
  from type annotations, so `int` vs `str | None` changes what the model may return
  ([typing reference](https://docs.python.org/3/library/typing.html)).
- **Classes** — Bots, Intels, and Skills are all small class hierarchies with
  class-attribute configuration ([classes tutorial](https://docs.python.org/3/tutorial/classes.html)).

## From PyPI

```bash
pip install dandy
```

The runtime footprint is deliberately four packages: `pydantic`, `requests`, `blessed`
(CLI TUI), `python-dotenv`.

## From source

```bash
git clone https://github.com/stratusadv/dandy.git
cd dandy
just venv     # uv venv + uv sync --all-extras
```

or `pip install -e .` without the project tooling.

## Verify

```bash
python -c "from dandy.shared.constants import __VERSION__; print(__VERSION__)"
```
