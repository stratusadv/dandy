set windows-shell := ["powershell.exe", "-c"]
set shell := ["sh", "-c"]
set dotenv-load := true
set dotenv-filename := "development.env"

export PYTHONPATH := if os() == "linux" { env_var_or_default("PYTHONPATH_APPEND", "") + ":." } else { env_var_or_default("PYTHONPATH_APPEND", "") + ";." }
PYTHON := if os() == "linux" { ".venv/bin/python" } else { ".venv/Scripts/python.exe" }

default:
    just --list

opencode:
    ./.venv/Scripts/activate.bat
    opencode

python *ARGS:
    {{ PYTHON }} {{ ARGS }}

test:
    {{ PYTHON }} -m pytest .

test-app app:
    {{ PYTHON }} -m pytest {{ app }}

test-coverage:
    {{ PYTHON }} -m pytest . --cov=django_spire --cov-report=term-missing

test-coverage-app app:
    {{ PYTHON }} -m pytest {{ app }} --cov={{ app }} --cov-report=term-missing

test-failed:
    {{ PYTHON }} -m pytest --ff --lf

venv:
    uv venv --clear .venv
    uv sync --all-extras --upgrade

venv-upgrade:
    uv sync --all-extras --upgrade

cli:
    {{ PYTHON }} ./dandy/cli/main.py

docs:
    mkdocs serve

docs-tests:
    mkdocs build --strict
