# 0005. Rebuild the docs site DDD-first

Status: Accepted
Date: 2026-09-25

## Context

The previous site was organized as a pile of tutorials written against the
flat 2.x layout. After the v3.0.0 restructure those pages described a package
that no longer existed, and their tutorial-first ordering taught the mechanics
before the model: for a framework whose identity is a domain model, that is
the cart before the horse. Updating the old site in place would have preserved
its structure and its blind spots.

## Decision

Rebuild the site from scratch, in the order a domain-driven project would
present itself: ubiquitous language (glossary) → bounded contexts (with
subdomain classification) → tactical patterns mapped to the real classes →
architecture (layering, the enforced rules, the service pattern, the anatomy
of an LLM call) → getting started → a user guide with one page per domain
concept → a hand-written API reference with one page per layer
(mkdocstrings) → migration guide → changelog. The old site is preserved
untouched in `archived_docs/` as read-only reference material.

The build is deliberately plain: Material theme, search, and
`mkdocstrings[python]` (plus a mermaid fence); no markdown-exec, so the
strict build runs hermetically and never executes example code against a live
LLM. The stack is the slim `documentation` extra
(`mkdocs`, `mkdocs-material`, `mkdocstrings[python]`), and `mkdocs build
--strict` is a CI gate in a dedicated `documentation-testing` job.

## Consequences

- The docs are a first-class, build-gated artifact: broken links, missing
  anchors, and unresolvable API symbols fail CI.
- Every user-guide page names its domain concept and its layer, and
  cross-references the glossary, so the ubiquitous language stays consistent
  across the site.
- The reference pages list members explicitly, so the API reference is a
  curated surface rather than a full dump; it must be updated when public
  symbols are added or renamed.
- Cost: hand-maintenance. A public-API change that is not reflected in
  `docs/` ships with stale docs (enforced by convention and review, not
  mechanically).
