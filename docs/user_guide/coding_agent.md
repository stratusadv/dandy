# The Coding Agent

**Domain concept:** the [coding agent bounded context](../domain_model/contexts.md#5-the-coding-agent-own-context)
— turns, plans, session state, and an agent toolset, built *on* the core tool-calling
loop.

**Lives in:** `dandy/application/agent/` (the use case) and `dandy/interfaces/cli/` (the
TUI and console script that drive it).

## What it is

The `dandy` console script is a pure agent REPL: every message you type goes through one
pipeline, and one-shot mode (`dandy "fix the failing test"`) runs the same pipeline for a
single turn. One-shot is stateless: it answers the request but creates no session file;
`dandy --continue "keep going"` runs one request inside the most recently saved session
and reports which one it used.

```text
your message
  │
  ▼
CodingAgent.turn              (dandy/application/agent/coding_agent.py)
  │  1. optional planning turn (a base-Agent hook):
  │       PlanningBot (THINKING config) writes an Implementation Plan
  │       that is folded into the coding prompt
  │  2. compact the persistent history if it approaches CONTEXT_SIZE
  │  3. run the core tool-calling loop:
  │       bot.llm.tools.prompt_to_intel(
  │           ..., tools=AGENT_TOOLS,
  │           message_history=self.history,
  │           replace_message_history=True,
  │           max_tool_iterations=None)      # uncapped
  ▼
the agent's final answer (rendered as terminal markdown)
```

`CodingAgent` is the framework's own child of the base [Agent](agent.md): the planning
pass is an override of the base `Agent`'s `_prepare_message` hook, so everything else
(compaction, the fit check, session save/load) comes from the base class unchanged.

Because each turn reuses the persistent `MessageHistory`, the agent remembers the
conversation; `replace_message_history=True` attaches *your* history object so the
conversation accumulates in it.

## The toolset

`AGENT_TOOLS` is the core's [tool calling](tool_calling.md) machinery pointed at a
project-aware toolset (`dandy/application/agent/tools/`):

- **File tools** — `read_file`, `write_file`, `edit_file`, `delete_file`,
  `create_directory`, `list_directory`, plus `search_files` (grep-style, skipping
  `.git`/`.dandy`/`node_modules`/`.venv`/`__pycache__`, capped output).
- **Commands** — `run_command` (no user confirmation), `git_status`, `git_diff`.

Every path resolves against the session's `project_base_path` and refuses paths that
escape it; every `handle()` returns a string and never raises, so the model can always
react to what went wrong.

## Context management

The agent reads the coding config's `CONTEXT_SIZE` and compacts its own history before
every LLM call to 70% of it ([Options and Context](options_and_context.md)), so an
uncapped tool loop cannot overflow the window. The tool loop also compacts before every
round, and both report progress through the TUI's story.

## The TUI

`dandy/interfaces/cli/` renders the agent: a `blessed` terminal, a `Printer` that feeds
final answers through a dependency-free `MarkdownRenderer` (headings, lists, code blocks,
tables), and a running "story" of tool beats ("Reading src/foo.py lines 1-10",
"Running pytest -q").

- `/new [name]` starts a fresh conversation (optionally pre-naming its session file);
  `/sessions` lists saved sessions; `/resume <name>` loads one and keeps the current
  agent state; `/delete <name>` removes one; `/quit` / `/exit` stop the loop.
- Pressing **escape twice** exits.
- `DEBUG = True` in settings prints one line per tool-round event to stdout.

## Sessions

The REPL's conversation is persisted automatically: after every turn the agent's
history is saved under the project at `.dandy/agent/sessions/<name>.json` (the
agent-neutral `agent/` directory, not `cli/`, so any agent over the same project
shares the location). The first turn names the session after your request
(`YYYY-MM-DD-<slug>`, e.g. `2026-10-31-fix-the-login-bug`; collisions get `-2`,
`-3`, ...), and later turns update the same file. The welcome banner always shows
a session-status line (how many are saved and how to resume the latest).

A saved session carries the full message history plus metadata: created/updated
timestamps, the last request, the model and config name, and an estimated token
count. `/resume <name>` loads the history back into the agent, so the next turn
continues exactly where that conversation left off; `/delete <name>` removes the
file. The store is plain JSON per session, so you can inspect or copy session
files by hand.

Under the hood the persistence is agent-neutral: the base [Agent](agent.md) owns
`save_session()` / `load_session()`, and `SessionStore`
(`dandy/application/agent/session_store.py`) reads, writes, lists, and names the
session files. `DandyCliSession` (`dandy/application/agent/session.py`) is the
REPL's own input state: just the project base path and the local `.dandy`
directory — the CLI builds it from the current working directory; a headless
driver would do the same.
