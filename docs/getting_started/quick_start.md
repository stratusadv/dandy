# Quick Start

## 1. A settings module

Dandy has no constructor configuration. It loads one settings module at import time —
the module named by `DANDY_SETTINGS_MODULE`, defaulting to `dandy_settings` in your
working directory.

```python title="dandy_settings.py"
import os
from pathlib import Path

BASE_PATH = Path.resolve(Path(__file__)).parent

LLM_CONFIGS = {
    'DEFAULT': {
        'HOST': os.getenv('OPENAI_HOST', 'https://api.openai.com'),
        'PORT': int(os.getenv('OPENAI_PORT', 443)),
        'API_KEY': os.getenv('OPENAI_API_KEY'),
        'MODEL': 'gpt-4o-mini',
    }
}
```

`BASE_PATH` and a `DEFAULT` entry in `LLM_CONFIGS` are the only two things required.
Everything else falls back to framework defaults — see
[Configuration](configuration.md).

## 2. A plain call

```python
from dandy import Bot

response_intel = Bot().process('What is the capital of Canada?')
print(response_intel.text)
```

`Bot().process` returns a `DefaultIntel`; `.text` holds the model's answer.

## 3. A typed call

The framework's point: make the answer a contract.

```python
from dandy import BaseIntel, Bot


class CapitalIntel(BaseIntel):
    country: str
    capital: str


intel = Bot().process('What is the capital of Canada?', intel_class=CapitalIntel)
print(intel.capital)  # 'Ottawa'
```

If the model returns the wrong shape, Dandy re-prompts it with the validation errors
(until `prompt_retry_count` is exhausted) rather than handing you an untrusted string.

## 4. A named bot

When the same kind of work repeats, give it a name — a [Bot](../user_guide/bots.md)
captures the how: endpoint config, role, task, guidelines, and return type.

```python
from dandy import Bot, Prompt


class CapitalBot(Bot):
    role = Prompt().text('You answer geography questions with one line.')
    task = 'Return the capital of the requested country.'
    intel_class = CapitalIntel


bot = CapitalBot()
intel = bot.process('France')
print(intel.capital)  # 'Paris'
```

## Next

- [Configuration](configuration.md) — named configs, `CONTEXT_SIZE`, JSON fallback.
- [Intel](../user_guide/intel.md) — the contract in detail.
- [The DDD layout](../architecture/layering.md) — where all of this lives.
