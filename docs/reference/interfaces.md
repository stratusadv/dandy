# Interfaces Layer

Interfaces are where the framework meets its users. Today there is one: the command-line
interface, a terminal REPL over the [CLI agent](../user_guide/cli_agent.md) built
on `blessed` (no other TUI dependencies).

The interfaces layer may depend on every other layer; nothing may depend on it. If you
build a new interface (an HTTP API, a notebook, a GUI), it goes here and talks to the
application layer through the same seams the CLI uses.

## Entry point

`dandy` on the command line. `dandy "do a thing"` runs one turn; `dandy --continue
"do a thing"` runs one turn inside the latest saved session; `dandy -s` lists the
saved sessions, `dandy -s <name>` opens the REPL on that session, and
`dandy -s <name> "do a thing"` runs one turn inside it; `dandy` alone opens the
interactive REPL; `-h` and `-v` are handled before any settings load. Every
command has a long and a short one-shot flag (the `-h` table is generated from
the [command registry](#the-command-registry)).

::: dandy.interfaces.cli.main.main

## The CLI loop

`DandyCli` is the agent REPL: it owns the `CliAgent`, a `SessionStore`
(`SessionStore.for_project(...)`) over the project's `.dandy/agent/sessions/`, and the
TUI, and processes each typed message as an agent turn. The REPL auto-saves the
conversation after every turn; the commands are `/new [name]` (fresh conversation,
optionally pre-named), `/sessions [name]` (list saved sessions, or load one by
name), `/resume <name>`, `/delete <name>`, and `/quit` (or `/exit`), and every
command also has a one-letter short (`/n`, `/s`, `/r`, `/d`, `/q` — `/i` for
`/init`); escape twice stops a running turn and, at the prompt, exits the REPL.
The welcome banner shows a session-status line.

::: dandy.interfaces.cli.cli.DandyCli

::: dandy.interfaces.cli.tui.banner.session_banner_line

::: dandy.interfaces.cli.utils.check_or_create_settings

### The command registry

One table drives both surfaces: `CLI_COMMANDS` in `dandy/interfaces/cli/commands.py`
— a frozen `CliCommand` entry per command (name, one-letter short, long and
short one-shot flag, argument rule, description) — feeds the REPL dispatch (name
or short), tab completion, the one-shot flag parser (`parse_one_shot` in
`dandy/interfaces/cli/one_shot.py`), and the `-h` usage text, so the REPL and the
one-shot flags cannot drift.

::: dandy.interfaces.cli.commands.CliCommand

::: dandy.interfaces.cli.commands.CLI_COMMANDS

::: dandy.interfaces.cli.commands.resolve

::: dandy.interfaces.cli.commands.commands_matching_prefix

::: dandy.interfaces.cli.commands.flag_lookup

::: dandy.interfaces.cli.one_shot.parse_one_shot

::: dandy.interfaces.cli.one_shot.OneShotPlan

## The TUI

::: dandy.interfaces.cli.tui.tui.Tui

::: dandy.interfaces.cli.tui.printer.Printer

::: dandy.interfaces.cli.tui.story_progress.StoryProgress

::: dandy.interfaces.cli.tui.markdown.MarkdownRenderer
    options:
        members:
            - render
