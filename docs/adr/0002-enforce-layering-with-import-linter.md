# 0002. Enforce the layering with import-linter

Status: Accepted
Date: 2026-09-25

## Context

A layering convention that is not mechanically enforced will rot: the first
"temporary" cross-layer import becomes permanent, and the layering document
becomes a fiction. Alternatives considered were a hand-rolled CI script
(grep-style import scanning) and code review discipline alone. A custom script
would re-implement import resolution badly (aliases, `from x import y`,
conditionals); review discipline is not a gate.

## Decision

Enforce the layering with [import-linter](https://github.com/seddonym/import-linter)
declaratively in `pyproject.toml` (`[tool.importlinter]`), run by
`just lint-imports` and by CI after the test suite. Six contracts:

1. Domain layer must not import outer layers
2. Shared kernel must not import any layer
3. Application layer must not import interface layer
4. Infrastructure layer must not import application or interface layers
5. Application layer imports infrastructure only at documented seams
6. Interface layer imports infrastructure only at documented seams

Contracts 5 and 6 are allow-list contracts: every permitted cross-layer import
is an individual, exact `source.module -> imported.module` edge in
`ignore_imports` (the [documented seams](../architecture/layering.md#documented-seams)).

## Consequences

- A new cross-layer import fails CI until the design is fixed or the exact edge
  is added with a reason; the seams list is a visible, reviewable artifact.
- The contracts are transitive: ignoring an entry edge and ignoring a seam edge
  are different decisions, and each is listed deliberately.
- The layering page and the contracts can no longer drift apart silently.
- Cost: some edges exist only for type-checking annotations and are noise in
  the list; a legitimate new seam requires touching `pyproject.toml` in the
  same PR as the code.
