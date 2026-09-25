# Prompts

**Domain concept:** [Prompt](../domain_model/glossary.md#glossary) — the structured,
composable outgoing message.

**Lives in:** `dandy/domain/llm/prompt/` (pure string construction).

## Building

Every builder method returns `self`, so prompts compose like querysets:

```python
from dandy import Prompt

prompt = (
    Prompt()
    .heading('Request')
    .text('Tell me about clowns.')
    .unordered_list(['funny', 'scary'])
    .line_break()
)

print(prompt.to_str())
```

Output (verified):

```text
## Request
Tell me about clowns.
- funny
- scary
```

## The builders

| Method | Renders |
|---|---|
| `text(...)` | plain text |
| `heading(...)`, `sub_heading(...)`, `title(...)` | markdown headings |
| `list(...)`, `unordered_list(...)`, `ordered_list(...)` | lists |
| `array(...)`, `array_random_order(...)`, `unordered_random_list(...)` | arrays |
| `dict(...)` | key/value block |
| `divider()`, `line_break()` (alias `lb`) | spacing |
| `file(path)`, `directory_list(path)` | a file's contents / a directory listing |
| `intel(obj)`, `intel_schema(intel_class)` | an Intel object / its JSON schema |
| `module_source(path)`, `object_source(obj)` | source code |
| `prompt(other)` | another Prompt or string |
| `random_choice(...)` | a random selection |

Most accept `triple_backtick` (plus an optional label) to fence the content as code.

## Tags

```python
Prompt(tag='request').text('Hi there.').to_str()
# <request>Hi there.</request>
```

## Strings are always acceptable

Anywhere a `Prompt` is accepted, a plain string is accepted. Prompts are for structure,
not ceremony.

!!! tip

    `Prompt.estimated_token_count` uses the framework's dependency-free token heuristic —
    check a prompt fits a small window before you send it.
