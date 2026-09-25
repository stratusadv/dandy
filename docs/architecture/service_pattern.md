# The Service Pattern

The mechanism by which Dandy composes adapters into use cases without constructor wiring.
It is also the reason the layer rules need their
[documented seams](layering.md#documented-seams) — so it is worth understanding exactly.

## The three parts

| Part | Base class | Lives in | Role |
|---|---|---|---|
| **Service** | `BaseService` | application or infrastructure | Wraps its owner (`self.obj`), carries a `recorder_event_id`, holds the logic, and implements an abstract `reset()`. |
| **Mixin** | `BaseServiceMixin` | usually infrastructure | Lazily builds and caches the service on first attribute access. |
| **Owner** | `Bot` (or your own class) | application | Composes the mixins; MRO order defines the reset chain. |

## How it works

```python
class LlmServiceMixin(BaseServiceMixin):
    llm_config: str = 'DEFAULT'          # declared as class attributes...
    role: Prompt | str = 'Assistant'     # ...because _required_attrs guards

    @property
    def llm(self) -> LlmService:
        return self._get_service_instance(LlmService)
```

1. `Bot` subclasses declare their configuration as **class attributes** (`llm_config`,
   `role`, `task`, `intel_class`, ...).
2. `BaseServiceMixin._required_attrs` + `__init_subclass__` raise
   `ServiceCriticalError` at class-creation time if a required attribute is still
   `None` — misconfiguration fails early and loudly.
3. First access to `bot.llm` calls `_get_service_instance(LlmService)`, which
   instantiates the service, stores it on the owner, and runs its `__post_init__` hook.
4. `bot.llm` (and `.file`, `.http`, `.intel`, and their sub-services like
   `bot.llm.tools` and `bot.llm.decoder`) always returns the same instance.

## Why composition instead of injection

A `Bot` subclass is *the user-facing unit of the framework*: you write a class with a few
class attributes and it just works. Constructor injection would push all that wiring into
every user's code. The price is that the mixin must name the service class and the
service must name its adapter — hence the frozen seam list. The framework trades
theoretical purity for a public API where zero wiring is the default, and pays for it with
the one enforced exception list.

## The reset chain

`Bot.reset()` walks the MRO and resets every composed service: `llm`, `http`, `intel`,
`file`. For the LLM service, reset clears the message history and re-applies options
from settings — this is what the CLI's `/clear` does.

- Subclasses that override `reset()` must call `super().reset()` — the chain relies on
  it.
- The **decoder service is deliberately excluded** (`DecoderService.reset()` is a no-op);
  decoders are stateless between calls.
- The exact call graph is pinned by `tests/application/bot/test_reset_chain.py`.

## Invariants

1. **No `__getattribute__` overrides in `Bot` subclasses.** The base installs the
   recorder wrapper around `process()` through `__getattribute__` at class-creation
   time; overriding it silently disables auto-recording.
2. **`super().__post_init__()` first**, in any `__post_init__` you write — the
   `ServiceCriticalError` guards depend on it.
3. **Class attributes, not instance state**, for service configuration: the guards run
   at class definition, so instance-level configuration is not visible to them.
