# The CLI Agent

**Domain concept:** the [CLI agent bounded context](../domain_model/contexts.md#5-the-cli-agent-own-context)
— turns, session state, and an agent toolset, built *on* the core tool-calling
loop.

**Lives in:** `dandy/application/agent/` (the use case: the generic `Agent` core, the
universal toolset in `intelligence/tools/`, and the CLI's `CliAgent` in `cli/` with its
bots and prompts in `cli/intelligence/`) and `dandy/interfaces/cli/` (the TUI and
console script that drive it).

## What it is

The `dandy` console script is a pure agent REPL: every message you type goes through one
pipeline, and one-shot mode (`dandy "fix the failing test"`) runs the same pipeline for a
single turn — the same underlying turn processing and session saving, only a different
front end (argv in, exit code out). Every turn saves the conversation: one-shot saves a
new auto-named session, a failed or stopped turn saves too (trimmed at the last complete
tool round), and `dandy -r "keep going"` runs one request inside the most recently
saved session and re-saves it under the same name. The session commands have one-shot
flags of their own: `dandy -s` (or `--sessions`) lists the saved sessions,
`dandy -s <name>` opens the interactive REPL with that session loaded, and
`dandy -s <name> "keep going"` runs one request inside that named session
(`dandy -r "keep going"` does the same for the most recently saved session, and
bare `dandy -r` opens the REPL on it; `-d`/`--delete`,
`-n`/`--new`, and `-i`/`--init` cover the other commands — run `dandy -h` for
the full table). The one-shot session forms exit with code 1 when the turn (or
the resume) fails, so a script can detect failure; the interactive REPL shows
the error and keeps looping.

```text
your message
  │
  ▼
CliAgent.turn               (dandy/application/agent/cli/cli_agent.py)
  │  1. compact the persistent history if it approaches CONTEXT_SIZE
  │  2. run the core tool-calling loop:
  │       bot.llm.tools.prompt_to_intel(
  │           ..., tools=AGENT_TOOLS,
  │           message_history=self.history,
  │           replace_message_history=True,
  │           max_tool_iterations=max_tool_rounds)  # 200 per turn by default
  ▼
the agent's final answer (rendered as terminal markdown)
```

`CliAgent` is the framework's own child of the base [Agent](agent.md) and a plain
one at that: the turn (compaction, the fit check, the tool loop) and session save/load
all come from the base class unchanged.

Because each turn reuses the persistent `MessageHistory`, the agent remembers the
conversation; `replace_message_history=True` attaches *your* history object so the
conversation accumulates in it.

## Project instructions (AGENTS.md)

When the project root contains an `AGENTS.md` file, its content is folded into the
`CodingBot` guidelines as a **Project Instructions** section, so it
is part of the system message for every turn (and for one-shot mode). The file is read
at agent construction, and the welcome banner shows a line for it (`found (15.3 KB) -
loaded into the agent system prompt` or `not found - run /init to create one`).

To create or refresh the file, the CLI has an **init pass**: type `/init` in the REPL
or run `dandy --init` as a one-shot. The pass runs a dedicated `InitBot`
(`dandy/application/agent/cli/intelligence/bots/init_bot.py`) in its own fresh conversation: it explores
the project with the normal agent tools, reads the manifest, README, task runners, and
test layout, then writes the complete `AGENTS.md` to the project root. When the file
already exists, its full current content is inlined into the pass's prompt as the
starting point (kept claims verified, stale ones corrected), and the result replaces
the file. When the pass writes the file, the running agent re-reads it and syncs its
system prompt (the current conversation's system message included), so the new
instructions apply to the next turn without `/new`. The init pass never touches your
conversation's history; `dandy --init` exits with code 1 when no file was written.

## The toolset

`AGENT_TOOLS` is the core's [tool calling](tool_calling.md) machinery pointed at a
project-aware toolset (`dandy/application/agent/intelligence/tools/`):

- **File tools** — `read_file`, `write_file`, `edit_file`, `delete_file`,
  `create_directory`, `list_directory`, plus `search_files` (grep-style, skipping
  `.git`/`.dandy`/`node_modules`/`.venv`/`__pycache__`, capped output).
- **Commands** — `run_command` (no user confirmation), `git_status`, `git_diff`.
- **Clock** — `get_time` (the local date and time, or the date and time in a
  named IANA timezone such as `UTC` or `America/New_York`).
- **Questions** — `question`, on the CLI agent only (the init pass does
  not ask): the model pauses the turn, shows you a question with
  optional numbered choices, and waits for your answer (a choice number or
  free text), which it receives as the tool result.

Every path resolves against the session's `project_base_path` and refuses paths that
escape it; every `handle()` returns a string and never raises, so the model can always
react to what went wrong. A `QuestionTool` without an `ask_user` callback (for example,
a headless `CliAgent`) answers its own question with a "no user available, assume
and proceed" note instead of blocking.

## Skills

The coding agent loads [skills](skill.md) from two directories at process start:

| Directory | Scope |
|---|---|
| `~/.config/dandy/skills/` | Global: every project on your machine |
| `<project>/.dandy/skills/` | Project: this project only |

Each skill is a **folder holding a `SKILL.md`** (the Anthropic Agent Skills
convention):

```markdown
---
name: deploy
description: Deploy the app. Use when the user asks to ship or release.
active: false
---
Always deploy with `just deploy`, never push tags by hand.
```

- The frontmatter supplies `name` (defaults to the folder name), `description`, and
  `active` (defaults to `true`; a passive skill needs a `description`). Unknown keys
  are ignored; the markdown body is the skill `prompt`. File skills are prompt-only —
  they carry no typed methods.
- **Project overrides global by name**: when both directories hold a skill with the
  same final name, the project one wins.
- Active skills put their prompt in the system message from the first turn; passive
  ones show only `name: description` until the model calls the built-in
  `activate_skill` tool. The loader (`dandy/application/skill/loader.py`) registers
  them through the normal `SkillService` path, so activation works exactly as for
  code-defined skills.
- The welcome banner shows a `Skills` line with the loaded count (active vs
  passive). Malformed files (missing frontmatter fence, passive without a
  description, ...) are skipped with one `Skill skipped` notice per file — they
  never crash the CLI.
- Skills are loaded once at process start for both the REPL and one-shot mode.
  `/new` keeps the registration but re-arms passive activation; a **resumed**
  session replays its saved system message, so skill changes only apply after `/new`
  (the same staleness as AGENTS.md in a resumed session).

## Context management

The agent reads the coding config's `CONTEXT_SIZE` and compacts its own history before
every LLM call to 70% of it ([Options and Context](options_and_context.md)), so a
long-running tool loop cannot overflow the window. The tool loop also compacts before
every round, and both report progress through the TUI's story.

## The TUI

`dandy/interfaces/cli/` renders the agent: a `blessed` terminal, a `Printer` that feeds
final answers through a dependency-free `MarkdownRenderer` (headings, lists, code blocks,
tables), and a running "story" of tool beats ("Reading src/foo.py lines 1-10",
"Running pytest -q").

- Every command has a one-letter short: `/i` (`/init`) creates or refreshes the
  project `AGENTS.md` (see [Project instructions](#project-instructions-agentsmd));
  `/n [name]` (`/new [name]`) starts a fresh conversation (optionally pre-naming
  its session file); `/s [name]` (`/sessions [name]`) lists saved sessions, and
  with a name loads that one; `/r [name]` (`/resume [name]`) loads a session —
  the most recently saved one if no name is given — and keeps the current agent
  state; `/d <name>` (`/delete <name>`) removes one;
  `/q` (`/quit`) or `/exit` stop the loop.
- Commands are discoverable at the prompt: when you type `/` as the first
  character, a grey tail on the input line itself lists every command matching
  what you have typed so far, by full name or by short (it follows your
  keystrokes and backspaces, and disappears once you add a space or the prefix
  stops matching), and pressing **tab** completes the command to its full name
  (the unique match, or the longest common prefix when several match).
- Pressing **escape twice** stops a running turn (the agent, tool loop, and
  any running command are interrupted and the prompt returns); at the prompt,
  pressing **escape twice** exits the REPL — and the same rule applies while
  an agent question is on screen: double escape skips the answer and stops
  the run.
- `DEBUG = True` in settings prints one line per tool-round event to stdout.
- **Desktop notifications**: when a request completes (or the `AGENTS.md`
  init pass finishes) and whenever the agent parks a question on screen, the
  CLI asks the terminal for a desktop notification with raw OSC sequences —
  OSC 777 (`xterm`-family terminals such as GNOME Terminal, Kitty, and
  Alacritty) and OSC 9 (tmux and iTerm2), BEL-terminated, from
  `dandy/interfaces/cli/tui/notify.py`. The message is the completion line or
  the question text, folded to one line and capped at 100 characters.
  Terminals that ignore both sequences are unaffected (no visible output, no
  sound), and the notification never blocks or crashes the run.
- File paths are clickable: a tool beat's description, the final answer's prose
  (paragraphs, headings, list items, table cells, blockquotes, and inline code
  spans), and the file-change sections below the final answer (one
  `Added Files` / `Modified Files` / `Removed Files` section per non-empty
  action when file tools ran, each file a clickable link under a bold blue
  heading with a thin blue border) all render them as OSC 8 `file://` links
  (resolved against the project root), so clicking one opens the file with the
  OS default handler. Fenced code blocks are never linked.

## Sessions

The REPL's conversation is persisted automatically: after every turn the agent's
history is saved under the project at `.dandy/agent/sessions/<name>.json` (the
agent-neutral `agent/` directory, not `cli/`, so any agent over the same project
shares the location). The first turn names the session after your request
(`YYYY-MM-DD-HH-MM-<slug>`, e.g. `2026-10-31-14-05-fix-the-login-bug`; collisions get `-2`,
`-3`, ...), and later turns update the same file. The welcome banner always shows
a session-status line (how many are saved and how to resume the latest).

In a git project, dandy makes sure `.dandy/` is in the project's `.gitignore`
(adding the entry if it is missing), so saved sessions never show up as
untracked files in `git status`. Non-git directories are left untouched.

When the CLI hits an error — a failed turn, a failed init pass, or an
unhandled crash at startup — it appends a timestamped entry with the full
traceback to `.dandy/logs/errors.log` in the project, and trims the log to
the newest 10000 lines after each write, so it stays small. Because the log
lives under `.dandy/`, it is gitignored along with the sessions.

A saved session carries the full message history plus metadata: created/updated
timestamps, the last request, the model and config name, and an estimated token
count. `/resume [name]` (or the short `/s <name>`) loads the history back into the
agent — the most recently saved session if no name is given — so the next turn
continues exactly where that conversation left off; the command line does the
same with `dandy -s <name>` (by name) or `dandy -r` (the most recently saved
session) — with a request it runs one turn in that session and exits, without
one it opens the REPL on it. `/delete <name>` (or `/d <name>`, and one-shot `dandy -d <name>`) removes
the file. The store is plain JSON per session, so you can inspect or copy session
files by hand.

Under the hood the persistence is agent-neutral: the base [Agent](agent.md) owns
`save_session()` / `load_session()`, and `SessionStore`
(`dandy/application/agent/session_store.py`) reads, writes, lists, and names the
session files. `DandyCliSession` (`dandy/application/agent/session.py`) is the
REPL's own input state: just the project base path and the local `.dandy`
directory — the CLI builds it from the current working directory; a headless
driver would do the same.
