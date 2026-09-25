# Intel

**Domain concept:** [Intel](../domain_model/glossary.md#glossary) — the contract for what
an LLM answer must look like.

**Lives in:** `dandy/domain/intel/` (pure pydantic, the core of the domain layer).

## Defining an Intel

```python
from dandy import BaseIntel


class CapitalIntel(BaseIntel):
    country: str
    capital: str


class CapitalListIntel(BaseListIntel[CapitalIntel]):
    capitals: list[CapitalIntel]
```

Intel objects are value objects: validated on construction, compared by value, safe to
share. A missing required field raises a `ValidationError`; an optional field
(`x: str | None = None`) simply is not there.

## Using an Intel

Pass `intel_class` to any `process` / `prompt_to_intel` call:

```python
from dandy import Bot

intel = Bot().process('Capital of Canada?', intel_class=CapitalIntel)
print(intel.capital)  # 'Ottawa'
```

The framework generates a JSON schema from your class, demands exactly that shape, and —
on a wrong-shape response — re-prompts the model with the validation errors until
`prompt_retry_count` (default 2) is exhausted.

## Trimming the schema

Tell the model to produce *less* than the full class:

```python
intel = bot.process(
    'Capital of Canada?',
    intel_class=CapitalIntel,
    include_fields={'capital'},   # or exclude_fields={'country'}
)
```

- `include_fields` / `exclude_fields` on a call trim the generated schema.
- `model_inc_ex_class_copy(include=..., exclude=...)` builds a runtime subclass with only
  (or except) the listed fields — for reusing one Intel across several bots. Nested dicts
  drill into nested Intel. Passing both include and exclude is an `IntelCriticalError`,
  as are unknown field names.

## File round-trips

```python
intel = CapitalIntel.create_from_file('capital.json')
intel.save_to_file('capital.json')
```

## Other helpers

| Helper | What it does |
|---|---|
| `model_to_kwargs()` | Fields as a keyword dict. |
| `model_json_inc_ex_schema` | The (trimmed) JSON schema as JSON. |
| `model_validate_and_copy(data)` | Validate a dict and copy into a new instance. |
| `model_validate_json_and_copy(raw)` | Same, from a JSON string. |
