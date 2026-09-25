# 0001. Adopt DDD layering

Status: Accepted
Date: 2026-09-25

## Context

The 2.x layout was flat: `dandy/bot`, `dandy/llm`, `dandy/intel`, `dandy/core`,
`dandy/http`, `dandy/file`, `dandy/cache`, `dandy/recorder`, `dandy/cli`.
Dependencies ran in every direction: the LLM package mixed pure value objects
(`Prompt`, `Message`, `LlmOptions`) with HTTP adapter code (the connector, the
endpoint config); `dandy/core` was a grab-bag that everything imported and that
imported back. There was no mechanical answer to "where does this code go?", so
the answer became "wherever the last person put similar code".

## Decision

Physically reorganize the package into a shared kernel plus four layers:
`dandy/domain` (pure value objects and policy), `dandy/application` (use cases:
`Bot`, the LLM/tool/decoder/diligence services, the coding agent),
`dandy/infrastructure` (adapters: LLM connector and config, HTTP, file, cache,
recorder, futures), `dandy/interfaces` (the CLI), and `dandy/shared` (the shared
kernel: service/connector ABCs, settings, exceptions, file and media
primitives). Breaking import changes were accepted; the release is 3.0.0.

## Consequences

- Ownership is unambiguous: each layer states what it may import, and the
  ["Where do I put new code?"](../architecture/layering.md) table answers
  placement in seconds.
- Every internal import path changed; a [migration guide](../migration/v2_to_v3.md)
  with the old-to-new map was published. The public API re-exported from the
  `dandy` root did not change.
- It enabled mechanical enforcement of the layering (see
  [0002](0002-enforce-layering-with-import-linter.md)).
- Cost: one breaking release, a large one-time rename, and tests reorganized to
  mirror the layout.
