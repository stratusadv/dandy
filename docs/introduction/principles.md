# Design Principles

Five commitments. The architecture exists to make them true, and the tests and
import-linter contracts exist to keep them true.

## 1. The answer is an object, never a string

Every LLM response is validated against a user-defined pydantic model (an
[Intel](../domain_model/glossary.md#glossary)) before it is returned. Wrong shape means a
re-prompt with the validation errors, not a silent parse failure. The model is the only
untyped boundary in your system.

## 2. Deterministic scaffolding around a probabilistic core

Everything Dandy does around the HTTP call — prompt assembly, schema generation, retry
policy, history compaction, validation, event emission — is deterministic and unit-tested
hermetically. The test suite passes with zero API keys; the probabilistic part is isolated
behind a single connector adapter and skipped, not faked, in tests.

## 3. A hard line between layers

The package is a shared kernel plus four layers with explicit dependency rules
([Layering and Dependency Rules](../architecture/layering.md)). The domain never imports an
adapter. The rules are enforced by `import-linter` contracts in CI, and every deliberate
exception is a **documented seam** listed in the contracts. Architecture is a CI gate, not
a code review opinion.

## 4. The domain language is the code

The public API uses the domain's own words — `Intel`, `Prompt`, `Bot`, `Decoder`,
`Recording`, `Event`, `Diligence` — and the code's organization mirrors the strategic
design ([Bounded Contexts](../domain_model/contexts.md)). If a concept in the
[glossary](../domain_model/glossary.md) does not have a home in the code, or a class does
not have a home in the glossary, something is misplaced.

## 5. Small on purpose

The runtime footprint is four packages (`pydantic`, `requests`, `blessed`,
`python-dotenv`). There is no ORM, no async runtime, no plugin system, no telemetry. The
framework is a small set of well-organized parts you can read end to end; the
[architecture pages](../architecture/layering.md) are long enough to explain the whole
system and short enough to fit on one screen at a time.
