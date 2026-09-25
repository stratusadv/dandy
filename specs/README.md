# Specs

A spec is the working design for one feature or epic: the *how*, written
before the code. It is a different artifact from an
[ADR](../docs/adr/README.md): an ADR records one decision and is immutable;
a spec tracks one feature until it is built and may evolve while it is a
draft.

## Conventions

- **One spec per feature or epic**, named by topic (not numbered):
  `tool-calling-loop.md`.
- Every spec starts from the template below and carries a `Status` header.
- The `ADRs:` line links the decisions the spec realizes, so the *what/why*
  and the *how* stay connected.
- **Lifecycle:** `Draft` (evolves freely) → `In review` → `Implemented`
  (frozen; keep it, it records why the code looks the way it does) or
  `Abandoned` (keep it, it records what was tried and why it stopped).
- Specs are working material. They live at the repo root, not under `docs/`,
  and are not published on the docs site.

## Template

```markdown
# <Feature> spec

Status: Draft
ADRs: 0001, 0004

## Problem

What is missing or wrong, in a paragraph.

## Design

Data model, public API, flow. Code and diagrams welcome.

## Open questions

What is still undecided, and what decides it.

## Non-goals

What this explicitly does not do.
```

## The dividing line

An ADR answers *what did we decide and why*; a spec answers *how will this
feature work*. If you cannot state the decision in one sentence, you are
writing a spec, not an ADR. If a spec grows into mostly trade-offs, extract
the decisions into ADRs and leave the mechanics behind.
