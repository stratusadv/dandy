# Architecture Decision Records

An ADR captures one decision: the context that forced it, the decision itself,
and its consequences. It is written when the decision is made and is immutable
after it is accepted.

## Conventions

- **One decision per file**, named `NNNN-kebab-slug.md`. Numbers are sequential,
  zero-padded to four digits. A number is never reused, not even for an
  abandoned decision.
- **Immutable.** Once `Status: Accepted`, the file is not edited. To change a
  decision, write a new ADR with `Supersedes: NNNN` and set `Superseded by: NNNN`
  on the old one. `Status: Abandoned` marks a proposal that was rejected.
- **Small.** Target 30-50 lines. An ADR that grows into a full design has become
  a spec (working feature designs live in `specs/` at the repo root, not on
  this site); split it.
- **Selective.** Only record decisions that are hard to reverse, surprising
  without context, or the product of a real trade-off. Not every choice is an
  ADR.

## Template

```markdown
# NNNN. Short decision title

Status: Proposed | Accepted | Deprecated | Superseded
Date: YYYY-MM-DD
Supersedes: NNNN (optional)
Superseded by: NNNN (optional)

## Context

The forces at play. A paragraph: what was true, what was painful, what options
existed.

## Decision

What we decided. A sentence or two, stated as a fact.

## Consequences

What got easier, what got harder, what we now owe. Bullets, including the cost.
```

## Index

Newest first.

| # | Decision | Status |
|---|---|---|
| [0005](0005-rebuild-docs-ddd-first.md) | Rebuild the docs site DDD-first | Accepted |
| [0004](0004-tool-handle-signature-as-schema.md) | Tool handle signature is the schema | Accepted |
| [0003](0003-hermetic-tests-by-default.md) | Hermetic test suite by default | Accepted |
| [0002](0002-enforce-layering-with-import-linter.md) | Enforce the layering with import-linter | Accepted |
| [0001](0001-adopt-ddd-layering.md) | Adopt DDD layering | Accepted |

!!! note

    ADRs 0001-0005 were backfilled on 2026-09-25 to record decisions already made
    during the v3.0.0 restructure; they predate the directory existing.
