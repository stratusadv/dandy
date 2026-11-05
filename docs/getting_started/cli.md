# The CLI

The `dandy` console script is a pure agent REPL: install it once on your machine and
use it in any project directory. Every message you type goes to the coding agent,
which reads and writes your code, runs your tests, and saves the conversation
automatically. This page is the getting-started path — [The CLI Agent](../user_guide/cli_agent.md)
explains how it works under the hood.

## Install

The recommended way is [uv](https://docs.astral.sh/uv/)'s tool installer:

```bash
uv tool install dandy
```

`uv tool` builds an isolated environment for the package and puts the `dandy` command
on your PATH — it never touches your projects' Python environments, which is exactly
right for a CLI you run from everywhere.

```bash
uv tool upgrade dandy      # when a new version ships
uv tool uninstall dandy    # remove it
dandy -v                   # verify: prints "Dandy 3.0.0a1"
```

Prefer other installers? `pipx install dandy` or `pip install dandy` give you the
same `dandy` command ([Installation](installation.md) covers from-source too).

## First run

```bash
cd your/project
dandy
```

On startup the CLI, in order:

1. loads environment variables from the first of `dandy.env`, `development.env`,
   `dev.env`, or `.env` found in the project;
2. resolves your settings — a `DANDY_SETTINGS_MODULE` module (default name
   `dandy_settings`), then `<project>/.dandy/dandy.json`, then
   `~/.config/dandy/dandy.json`; if none exist it scaffolds a `dandy_settings.py`
   from the bundled defaults, tells you to fill in `BASE_PATH` and `LLM_CONFIGS`,
   and exits;
3. appends `.dandy/` to the project's `.gitignore` when it is a git repo;
4. prints the welcome banner and opens the prompt.

The banner shows what it resolved, so you always know which model you are talking
to:

```text
Version      : 3.0.0a1
Model        : gpt-6-luna
Project Dir  : /home/nathanj/projects/api
AGENTS.md    : found (12.4 KB) - loaded into the agent system prompt
Sessions     : 3 saved, latest: 2026-11-05-14-20-fix-auth - resume it with /resume 2026-11-05-14-20-fix-auth
```

## Configure it

The full settings reference is [Configuration](configuration.md); for CLI use the
practical shape is:

### One global config (recommended for system-wide use)

Write `~/.config/dandy/dandy.json` once, and every project without its own settings
picks it up (on Windows the path is `%USERPROFILE%\.config\dandy\dandy.json`):

```json
{
  "llm_configs": {
    "DEFAULT": {
      "host": "https://api.openai.com",
      "port": 443,
      "api_key": "sk-...",
      "model": "gpt-6-luna",
      "context_size": 1050000,
      "options": { "reasoning_effort": "none" }
    },
    "THINKING": { "model": "gpt-6-sol" }
  },
  "cli_config": { "CODING": "DEFAULT" }
}
```

Keys are read case-insensitively (upper-cased on load); `OPTIONS` sub-keys stay
lowercase because they are OpenAI parameter names. The loader does not expand
environment variables, so either keep the API key out of the file (per-project
`dandy.env` or settings module) or `chmod 600` the JSON. The GPT-6 generation only
supports function calling over `v1/chat/completions` with `reasoning_effort` set to
`"none"`, and the agent runs entirely on tool calls — so keep that option on whatever
config the CLI uses. Point `CODING` at a stronger model (e.g. `gpt-6-sol`) when you
want the flagship for coding work.

### Per-project overrides

Two levels sit above the global file, in order of precedence:

- `<project>/.dandy/dandy.json` — same JSON shape, project-scoped.
- `dandy_settings.py` — a real Python module (imported via `DANDY_SETTINGS_MODULE`,
  default name `dandy_settings`); it can read env vars, so it is the right home for
  secrets:

```python title="dandy_settings.py"
import os
from pathlib import Path

BASE_PATH = Path.resolve(Path(__file__)).parent

LLM_CONFIGS = {
    'DEFAULT': {
        'HOST': os.getenv('AI_API_HOST', 'https://api.openai.com'),
        'PORT': int(os.getenv('AI_API_PORT', 443)),
        'API_KEY': os.getenv('AI_API_KEY'),
        'MODEL': 'gpt-6-luna',
        'CONTEXT_SIZE': 1050000,
        'OPTIONS': {'reasoning_effort': 'none', 'temperature': None, 'top_p': None},
    },
    'THINKING': {'MODEL': 'gpt-6-sol'},
}

CLI_CONFIG = {'CODING': 'DEFAULT'}
DEBUG = False   # True adds a "↳" trace line per tool round
```

### Picking the model

`CLI_CONFIG` maps the CLI's `CODING` task to an `LLM_CONFIGS` entry (unknown or
missing names fall back to `DEFAULT`). Point it at a stronger model for a particular
project and the banner's `Model` line confirms the switch.

## Use it

| Invocation | What it does |
|---|---|
| `dandy` | interactive REPL: every message is one agent turn |
| `dandy "fix the failing auth test"` | one turn, then exit; auto-saves a session named from the request |
| `dandy --continue "keep going"` | one turn inside the most recently saved session, re-saved under the same name |
| `dandy --init` | explores the project and writes/refreshes `AGENTS.md` |

One-shot modes exit with code `1` when the turn failed, so they script cleanly.
In the REPL:

- `/init` — create or refresh `AGENTS.md` (folded into the agent's system prompt)
- `/new [name]` — start a fresh conversation, optionally pre-named
- `/sessions` — table of saved conversations (name, updated, messages, tokens)
- `/resume <name>` — load one back into the agent
- `/delete <name>` — remove a saved conversation
- `/quit` — exit; **escape twice** stops a running turn, or exits at the prompt

While it works, the CLI prints a running story (`Executing ↳ pytest -q`,
`Reading ↳ src/foo.py lines 1-60`, ...), renders the final answer as markdown with
clickable file links, and lists Added/Modified/Removed files when it changed any.
Every turn — success, stop, or error — saves the conversation (trimmed at the last
complete tool round) so a crash never leaves a session that fails on resume.

## Where it keeps state

Everything lives under `<project>/.dandy/`, gitignored by default:

```text
.dandy/
 ├── agent/sessions/<name>.json    one file per saved conversation
 ├── recordings/                   optional recording renders
 ├── logs/errors.log               failures with full tracebacks (trimmed to 10000 lines)
 └── dandy.json                    optional project-scoped settings
```
