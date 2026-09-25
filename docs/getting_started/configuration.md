# Configuration

All runtime configuration flows from one place: the **settings module**, loaded once at
import time by the `DandySettings` singleton (`dandy/shared/conf/settings.py`).

## The settings module

The module named by `DANDY_SETTINGS_MODULE` (default: `dandy_settings` in the working
directory) must define `BASE_PATH`; everything else falls back to
`dandy/shared/conf/default_settings.py`.

```python title="dandy_settings.py"
import os
from pathlib import Path

BASE_PATH = Path.resolve(Path(__file__)).parent

LLM_CONFIGS = {
    'DEFAULT': {
        'HOST': 'https://api.openai.com',
        'PORT': 443,
        'API_KEY': os.getenv('OPENAI_API_KEY'),
        'MODEL': 'gpt-4o-mini',
        'CONTEXT_SIZE': 128000,
    },
    'THINKING': {
        'MODEL': 'stratus.thinking',
        # HOST / PORT / API_KEY inherited from DEFAULT
    },
}

CLI_CONFIG = {'CODING': 'DEFAULT'}
ALLOW_RECORDING_TO_FILE = True
DEBUG = False
```

| Setting | Required | Meaning |
|---|---|---|
| `BASE_PATH` | yes | Project root, as a `Path`. |
| `LLM_CONFIGS` | yes (`DEFAULT` entry) | Named endpoint configs: `HOST`, `PORT`, `API_KEY`, `MODEL`, optional `CONTEXT_SIZE` and `OPTIONS`. Non-`DEFAULT` entries inherit missing credentials from `DEFAULT`. |
| `CONTEXT_SIZE` | no | The model's context window in tokens. Drives `max_completion_tokens` (20% of the window) and agent history compaction (70% target). See [Options and Context](../user_guide/options_and_context.md). |
| `CLI_CONFIG` | no | Maps CLI task names to `LLM_CONFIGS` entries (e.g. `CODING`). Used by the `dandy` console script. |
| `ALLOW_RECORDING_TO_FILE` | no (`False`) | Persist recordings to `{BASE_PATH}/.dandy/recordings/`. |
| `DEBUG` | no (`False`) | Installs a warning handler that prints full stack traces for LLM retry/validation issues. |
| `CACHE_SQLITE_DATABASE_PATH` | no | Where `SqliteCache` stores its database. |

## Provider requirements

`LlmConfig` fixes the request path to `v1/chat/completions`: **OpenAI-compatible chat
completions only**. Any host implementing that endpoint works — OpenAI, vLLM, litellm,
local gateways. Response parsing reads `choices[0].message.content` (and
`choices[0].message.tool_calls` when tools are in play).

## The `dandy.json` fallback

If no settings module imports, the framework tries JSON before the CLI scaffolds a `.py`:
`.dandy/dandy.json` in the working directory, then `~/.config/dandy/dandy.json`. Top-level
keys, config names, and config fields are read case-insensitively (upper-cased on load);
`OPTIONS` sub-keys stay lowercase because they are `LlmOptions` field names;
`BASE_PATH` / `CACHE_SQLITE_DATABASE_PATH` strings become absolute paths; a missing
`BASE_PATH` defaults to the working directory.

The CLI's `check_or_create_settings` probes the same locations and, if nothing is found,
creates a `dandy_settings.py` from the bundled defaults and tells you which
`DANDY_SETTINGS_MODULE` value to export.

## Environment variables

The settings module conventionally reads secrets from the environment (see above). The
`dandy` CLI additionally loads `dandy.env`, `development.env`, `dev.env`, or `.env` from
the working directory before importing your settings module.

!!! note

    The settings singleton loads once per process. The CLI reloads from the environment
    on startup; in your own code, restart the process after changing environment
    variables.
