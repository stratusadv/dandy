# What is Dandy

Language models are probabilistic. The software around them does not have to be.

Dandy is a Python framework that draws a hard line between the two: the **domain logic** —
what you are asking for, what shape the answer must have, what invariants a conversation
must keep, how failures are classified — is written as ordinary, testable Python. The
**probabilistic boundary** — the HTTP round trip to a model endpoint — is isolated in a
single adapter that the rest of the system never touches directly.

## The problem, precisely

Ask a model "what is the capital of Canada?" and you get a string. To use that string you
must: parse it, hope the parse worked, retry when it did not, keep the conversation
coherent across many calls, size it to fit the model's context window, log it for later
review, and do all of that against whichever OpenAI-compatible endpoint you are currently
on. Frameworks that stop at "a requests wrapper with retries" push all of that back into
your application code, where it is untyped and invisible.

Dandy's answer: **the answer to an LLM call is a validated object, never a string you have
to trust.** Everything else — prompts, history, options, tool calls, recording, caching —
is modeled the same way: named concepts with invariants, organized into layers with
enforced dependency rules.

## One example

```python
from dandy import BaseIntel, Bot


class CapitalIntel(BaseIntel):
    country: str
    capital: str


intel = Bot().process('What is the capital of Canada?', intel_class=CapitalIntel)
print(intel.capital)  # 'Ottawa'
```

That one line is: a use case (`Bot.process`), a value-object contract (`CapitalIntel`),
schema generation, a system-prompted request, an HTTP adapter call, response validation,
and a validation-error retry loop — with every piece living in exactly one layer and
every layer boundary checked by an import-linter contract.

## Where to read next

- [Design Principles](principles.md) — the small set of commitments the architecture
  exists to enforce.
- [Ubiquitous Language](../domain_model/glossary.md) — the domain's vocabulary. This is
  the page to read before anything else if you want to think in Dandy's terms.
- [Bounded Contexts](../domain_model/contexts.md) — how the framework divides the
  strategic space: core, supporting, and generic subdomains.
- [Layering and Dependency Rules](../architecture/layering.md) — the physical
  architecture and the contracts that keep it honest.
