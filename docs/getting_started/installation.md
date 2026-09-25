# Installation

## Requirements

- Python **3.11+** (classifiers cover 3.11–3.14).
- An API key for any OpenAI-compatible chat-completions endpoint.

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
python -c "import dandy; print(dandy.__version__)"
```
