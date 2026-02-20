set windows-shell := ["powershell.exe", "-c"]
set shell := ["sh", "-c"]
set dotenv-load
set dotenv-filename := "development.env"

RESEARCH_PROMPT := "Can you design a really unique python library in a single code snippet."
PYTHON := if os() == "linux" { ".venv/bin/python" } else { ".venv/Scripts/python.exe" }

default:
	just --list

build-venv:
	uv venv .venv/
	uv pip install -e .[development,documentation]

run-cli:
	{{PYTHON}} ./dandy/cli/main.py

run-tests:
	python -m unittest discover -v ./tests

run-doc-tests:
	mkdocs build --strict
