# How Agents Work

The agent subsystem is where Dandy's single-shot [Bots](../user_guide/bots.md) become
stateful, looping, project-aware workers: a base `Agent` that owns a conversation and
drives the [tool-calling loop](../user_guide/tool_calling.md), and the CLI's
`CodingAgent`, the framework's own built-in agent.

**Lives in:** `dandy/application/agent/` (the use case: `agent.py`, `coding_agent.py`,
the bots in `bots/`, the project toolset in `tools/`, sessions in `session.py` /
`session_store.py` / `intel.py`) and `dandy/interfaces/cli/` (the front end that drives
it). It is its own [bounded context](../domain_model/contexts.md#5-the-coding-agent-own-context)
that consumes the core LLM context — the core stays free of CLI concerns.

## The vocabulary

| Term | Meaning |
|---|---|
| **run** | one autonomous drive: a request in, turns until the request is complete, the final result out |
| **turn** | one exchange: a message in, the agent works (possibly across many tool rounds), a final answer out; the conversation persists |
| **tool round** | one cycle of the model calling tools and the framework feeding results back |

A `run` is made of `turn`s; a `turn` is made of `tool round`s. Interactive use — a
human feeding one message at a time, like the CLI REPL — is a sequence of `turn`s;
the [coding agent](../user_guide/coding_agent.md)'s `turn` is one such interactive turn.

## Anatomy of a turn

`Agent.turn(message)` (`dandy/application/agent/agent.py`) is the whole exchange:

```text
turn(message)
  │  1. stop-signal check (double-escape) → RunStoppedError
  │  2. _prepare_message(message)          ← subclass hook (a plain pass-through
  │                                          for the coding agent)
  │  3. _compact_history_for_next_message  ← history over 80% of the window?
  │                                          compact down to 70% (minus the
  │                                          incoming message's tokens)
  │  4. _ensure_history_fits               ← still over the whole window?
  │                                          AgentRecoverableError, no request sent
  ▼
bot.llm.tools.prompt_to_intel(
    prompt=message,
    tools=self.tools,
    intel_class=self.intel_class,
    message_history=self.history,          ← the persistent conversation
    replace_message_history=True,          ← rounds accumulate into it
    max_tool_iterations=self.max_tool_rounds,
)
  │  5. the tool loop: model → tool calls → results → model → ...
  ▼
The turn's result Intel
```

The conversation accumulates in `self.history` across turns; the incoming message is
only sent on the first LLM call of the turn, and every tool round after that runs on
the conversation alone.

## The base Agent

`Agent` (exported from the `dandy` root) wraps a Bot and owns the conversation:

```python
Agent(
    bot,                          # the Bot that performs the work
    tools=None,                    # the tool set every turn may call
    skills=None,                   # skills registered on the bot at construction
    max_turns=None,                # the run() budget; None = unbounded
    max_tool_rounds=200,           # AGENT_MAX_TOOL_ROUNDS_DEFAULT; None = no cap
    intel_class=None,              # per-turn result model; default AgentTurnIntel
)
```

- **`turn(message)`** — one exchange, as diagrammed above. Returns the turn's result
  Intel (`AgentTurnIntel` by default: `text` + `done`).
- **`run(request)`** — drives turns until completion: the first turn receives the
  request, later turns receive a continuation nudge. A turn is done when its result's
  `done` field is true or an `is_done` callback says so. `max_turns` exhausted →
  `AgentRecoverableError`; no `done` field and no `is_done` → `AgentCriticalError`
  (fail fast — an agent that cannot tell when it is finished should not be running).
- **`clear()`** — fresh `MessageHistory`, `last_request = None`, `bot.reset()`.
  Subclasses call `super().clear()` first and then reset their own extras.

### Context management

The agent resolves its window once at construction: the bot's LLM config
`CONTEXT_SIZE`, falling back to `AGENT_MAX_CONTEXT_TOKENS_DEFAULT` (65536). Before
every turn it compacts the history with the shared `compact_message_history`
([Options and Context](../user_guide/options_and_context.md)):

- **Trigger:** the history's estimated token count exceeds 80% of the window
  (`AGENT_COMPACTION_TRIGGER_RATIO`) minus the incoming message's estimate.
- **Target:** compact down to 70% of the window (`AGENT_COMPACTION_TARGET_RATIO`)
  minus the incoming message's estimate — the incoming prompt is part of the next
  request, so its tokens are reserved up front.
- **Fit check:** if history plus message still exceeds the *whole* window after
  compaction, `turn` raises `AgentRecoverableError` instead of sending a request the
  provider would 400.

The trigger sits above the target on purpose: a loop whose rounds keep re-adding about
what compaction just dropped does not re-compact on every round. The tool loop
compacts its own accumulated conversation before every round as well, so an uncapped
tool-calling session can never overflow the window from either side.

### The tool round

The mechanics of the loop itself — execute-and-loop, the repeated-call guard, the
8000-character result cap, per-round compaction — belong to the core and are covered
in [Tool Calling](../user_guide/tool_calling.md). The agent's contribution is the
cap: `max_tool_rounds` (default `AGENT_MAX_TOOL_ROUNDS_DEFAULT = 200`) is passed as
`max_tool_iterations`, so a model that keeps requesting tools without ever giving a
final answer burns a bounded number of rounds. Pass `max_tool_rounds=None` to a
specific agent to disable the cap.

### Sessions

Every agent can snapshot its conversation and restore it later, so a conversation can
outlive the process:

- **`save_session()`** returns an `AgentSession` — the full message history plus
  metadata (last request, model name, config name, estimated token count). Before
  snapshotting it drops an incomplete trailing tool round (a tool-call declaration
  whose results never arrived is invalid on the wire), so a crash mid-round never
  leaves a session that 400s at resume.
- **`load_session(session)`** restores the history into a fresh `MessageHistory` and
  resets the bot, so the next `turn` continues exactly where the saved conversation
  left off.

The file side is `SessionStore` (`dandy/application/agent/session_store.py`): one JSON
record per named session under a directory, each record pairing the `AgentSession`
with a name and created/updated timestamps. `for_project(path)` targets
`<path>/.dandy/agent/sessions/` — agent-neutral, so any agent over the same project
shares the location. It also gives `list_sessions()`, `latest()`, `delete(name)`, and
`new_name(text)`, which derives a fresh non-colliding `YYYY-MM-DD-<slug>` name (40-char
slug, `-2`/`-3` on collision) from a piece of request text. The CLI keeps this state
out of version control: before any mode it ensures a git project's `.gitignore`
contains `.dandy/` (`ensure_dandy_gitignore` in `dandy/interfaces/cli/utils.py`),
appending the entry when missing; non-git directories are untouched.

## The CodingAgent

`CodingAgent` (`dandy/application/agent/coding_agent.py`) is the CLI's child of
`Agent`: `bot=CodingBot()`, `tools=AGENT_TOOLS` plus the `question` tool,
`intel_class=DefaultIntel`. It is a plain child — the turn (compaction, the fit check,
the tool loop) and session save/load come from the base class unchanged. Two methods
manage the project's `AGENTS.md`:

- **`reload_agents_md()`** — re-reads the file and re-syncs it into the running
  conversation: rebuilds the bot's guidelines, the connector's system message, and the
  history's leading system message, so a regenerated file applies to the next turn
  without a `/new`.
- **`run_init_pass()`** — a fresh `InitBot` conversation that explores the project and
  writes (or refreshes) `AGENTS.md` at the project root, inlining the existing file
  into its prompt when one exists. It verifies the file was actually written (returns
  `None` otherwise) and, on success, calls `reload_agents_md()` so the new content is
  already in the system prompt.

## The bots

Three `Bot` subclasses in `dandy/application/agent/bots/`, each a plain class-attribute
configuration of the [service pattern](service_pattern.md):

| Bot | Role | LLM config | Purpose |
|---|---|---|---|
| `CodingBot` | Senior Software Engineer | `CODING` | the workhorse: implements the request with `AGENT_TOOLS` |
| `InitBot` | Project Documentation Engineer | `CODING` | the AGENTS.md generation pass |
| `SessionNamingBot` | Session Naming Assistant | `SIMPLE` | 8–10 word session titles (`SessionNameIntel`) |

Config names resolve through `get_cli_llm_config` (the settings `CLI_CONFIG` map,
falling back to `DEFAULT`). `CodingBot` folds the project's
`AGENTS.md` into its guidelines as a **Project Instructions** section
(`dandy/application/agent/agents_md.py`: `read_agents_md` + `agents_md_section`), so
the file is part of the system message for every turn. `InitBot` deliberately does not
— it is the bot that *writes* the file.

## The toolset

`AGENT_TOOLS` (`dandy/application/agent/tools/`) is the core tool-calling machinery
pointed at a project-aware toolset:

```python
AGENT_TOOLS = [*CODE_EDITING_TOOLS, *SEARCH_TOOLS, *COMMAND_TOOLS, *GIT_TOOLS]
```

| Group | Tools |
|---|---|
| `CODE_EDITING_TOOLS` | `list_directory`, `read_file`, `write_file`, `edit_file`, `delete_file`, `create_directory` |
| `SEARCH_TOOLS` | `search_files` (grep-style; skips `.git`/`.dandy`/`node_modules`/`.venv`/`__pycache__`, 1 MB file and 300-char line caps, 8000-char result cap) |
| `COMMAND_TOOLS` | `run_command` (shell, 30 s default timeout, no user confirmation) |
| `GIT_TOOLS` | `git_status` (`git status --short`), `git_diff` |

Three rules make the toolset safe to run unattended:

- **Sandboxed paths.** Every path resolves against the session's `project_base_path`
  via `resolve_project_path` (`tools/paths.py`) and refuses paths that escape it;
  results are reported as project-relative paths.
- **No raises.** Every `handle()` is wrapped in the `tool_error` decorator
  (`tools/tool_errors.py`), so an unexpected error comes back to the model as an
  `Error ...: ...` string it can react to instead of killing the loop.
- **Shared subprocess primitive.** `run_command` and the git tools call
  `self.run_subprocess(...)` (the shared kernel's subprocess helper): exit-code line,
  8000-character output cap, and `stop_signal` polling so a double-escape interrupts a
  running command.

Every tool also sets an `action_label` (and some an `action_ascii_char`) plus an
`action_output(**args)` override, which is what the TUI's story renders — "Reading
src/foo.py lines 1-10", "Executing pytest -q" — so the user sees exactly what each
round is doing.

## Sessions on disk

The pieces, from `dandy/application/agent/intel.py` and `session.py`:

- **`AgentSession`** — the snapshot: `messages`, `last_request`, `model`, `config`,
  `token_count`.
- **`SessionRecord`** — the on-disk shape: a named, timestamped `AgentSession`
  (one JSON file per session under `.dandy/agent/sessions/`).
- **`SessionNameIntel`** — the AI-generated title used to name a new session.
- **`DandyCliSession`** (`session.py`) — the module-level `session` singleton holding
  `project_base_path` (set by the CLI entry point from the working directory) and
  derived paths (`agents_md_path`, the `.dandy` directory). This is the sandbox root
  the tools resolve against.

## The CLI wiring

`DandyCli` (`dandy/interfaces/cli/cli.py`) is the front end: it owns a `CodingAgent`,
a `SessionNamingBot`, and a `SessionStore.for_project(session.project_base_path)`.
Every non-command message is exactly one `agent.turn`:

```text
user input
  │  '/' → command handler
  ▼
process_agent_input
  │  stop_signal.clear()
  │  agent.turn(user_input, progress_callback=story update, verbose_callback=DEBUG)
  │      success → final answer through MarkdownRenderer
  │      RunStoppedError → "Run stopped."
  │      other error → printed, turn marked failed
  ▼
finally: _save_session_after_turn
  │  first turn: name the session — SessionNamingBot title (falls back to the
  │  request text), then SessionStore.new_name → YYYY-MM-DD-<slug>
  │  every turn: store.save(active_name, agent.save_session())
  ▼
next prompt
```

The save is in a `finally` block on purpose: a turn saves regardless of outcome
(success, stop, or error), so the conversation always survives the process.

- **Commands:** `/init` (the AGENTS.md generation pass), `/new [name]` (fresh
  conversation, optionally pre-naming its session), `/sessions` (a table of
  name/updated/messages/tokens/model), `/resume <name>`, `/delete <name>`,
  `/quit`/`/exit` (anything else reports "Unknown command").
- **One-shot mode:** `dandy "<request>"` runs the same `process_user_input` path for a
  single turn (auto-saving a new session named from the request); the process exits
  with code 1 when the turn failed. `dandy --continue "<request>"` loads the most
  recently saved session, runs the one turn inside it, and re-saves it under the same
  name. `dandy --init` runs the AGENTS.md pass and exits 1 when the file was not
  written.
- **Stopping:** pressing **escape twice** sets the shared `stop_signal`; the agent,
  the tool loop, the LLM connector, and any running subprocess all poll it at safe
  checkpoints and stop. At the prompt, escape twice exits the REPL.
- **The TUI:** story beats from the `progress_callback` render the running narrative
  (compaction, each tool execution); the final answer renders through the
  dependency-free `MarkdownRenderer`. `DEBUG = True` in settings adds one verbose line
  per tool-round event.

## Where to read next

- [Agent](../user_guide/agent.md) — the user-facing API for `turn`, `run`, and
  sessions.
- [The Coding Agent](../user_guide/coding_agent.md) — the CLI from the user's side:
  commands, the TUI, sessions.
- [Tool Calling](../user_guide/tool_calling.md) — the execute-and-loop mechanics the
  agent's tool rounds run on.
- [Options and Context](../user_guide/options_and_context.md) — `CONTEXT_SIZE`,
  token estimation, and compaction.
- [Anatomy of an LLM Call](data_flow.md) — what happens inside each LLM call of a
  tool round.
- [Bounded Contexts](../domain_model/contexts.md#5-the-coding-agent-own-context) —
  why the coding agent is its own context.
