# Dandy

<p align="center">
    <img alt="Build" src="https://img.shields.io/github/actions/workflow/status/stratusadv/dandy/run_tests.yml">
    <img alt="Python Versions" src="https://img.shields.io/pypi/pyversions/dandy">
    <img alt="PyPI Version" src="https://img.shields.io/pypi/v/dandy">
</p>

Dandy is a Python framework for **structured LLM interaction**. It treats "talking to a
language model" as a domain with its own language, invariants, and failure modes — and builds
typed, deterministic scaffolding around the one part that is genuinely probabilistic.

- Define the shape of what you want back as a typed model (an **Intel**); the framework
  validates the model's answer against it and re-prompts it when it gets the shape wrong.
- Compose behavior from named, configurable units (**Bots**) on top of a layered,
  [domain-driven architecture](architecture/layering.md) whose dependency rules are
  machine-enforced.
- Observe everything: every interaction is a recordable stream of **domain events**.

## Start here

| If you... | Read |
|---|---|
| Want the big picture in two minutes | [What is Dandy](introduction/what_is_dandy.md) |
| Want to make a call immediately | [Quick Start](getting_started/quick_start.md) |
| Want to understand the model | [Ubiquitous Language](domain_model/glossary.md) |
| Want to understand the architecture | [Layering and Dependency Rules](architecture/layering.md) |
| Are coming from Dandy 2.x | [Migration: 2.x to 3.0](migration/v2_to_v3.md) |
