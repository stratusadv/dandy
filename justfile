set windows-shell := ["powershell.exe", "-c"]
set shell := ["sh", "-c"]

RESEARCH_PROMPT := "Can you design a really unique python library in a single code snippet."
ACTIVATE_VENV := if os() == "linux" { "source .venv/bin/activate" } else { ".venv/Scripts/activate" }

default:
	just --list

build-venv:
	uv venv .venv/
	{{ACTIVATE_VENV}}
	uv pip install -e .[development,documentation]

run-tests:
	{{ACTIVATE_VENV}}
	python -m unittest discover -v ./tests

run-doc-tests:
	{{ACTIVATE_VENV}}
	mkdocs build --strict
