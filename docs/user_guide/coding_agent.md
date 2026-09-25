# The Coding Agent

**Domain concept:** the [coding agent bounded context](../domain_model/contexts.md#5-the-coding-agent-own-context)
— turns, plans, session state, and an agent toolset, built *on* the core tool-calling
loop.

**Lives in:** `dandy/application/agent/` (the use case) and `dandy/interfaces/cli/` (the
TUI and console script that drive it).

## What it is

The `dandy` console script is a pure agent REPL: every message you type goes through one
pipeline, and one-shot mode (`dandy "fix the failing test"`) runs the same pipeline for a
single turn.

```text
your message
  │
  ▼
CodingAgent.chat            (dandy/application/agent/coding_agent.py)
  │  1. optional planning turn:
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

- `/clear` resets the history; `/quit` / `/exit` stop the loop.
- Pressing **escape twice** exits.
- `DEBUG = True` in settings prints one line per tool-round event to stdout.

## The session

`DandyCliSession` (`dandy/application/agent/session.py`) is the use case's input state:
the project base path and the local `.dandy` directory. The CLI builds it from the
current working directory; a headless driver would do the same.
