# Interfaces Layer

Interfaces are where the framework meets its users. Today there is one: the command-line
interface, a terminal REPL over the [coding agent](../user_guide/coding_agent.md) built
on `blessed` (no other TUI dependencies).

The interfaces layer may depend on every other layer; nothing may depend on it. If you
build a new interface (an HTTP API, a notebook, a GUI), it goes here and talks to the
application layer through the same seams the CLI uses.

## Entry point

`dandy` on the command line. `dandy "do a thing"` runs one turn; `dandy --continue
"do a thing"` runs one turn inside the latest saved session; `dandy` opens the
interactive REPL; `-h` and `-v` are handled before any settings load.

::: dandy.interfaces.cli.main.main

## The CLI loop

`DandyCli` is the agent REPL: it owns the `CodingAgent`, a `SessionStore`
(`SessionStore.for_project(...)`) over the project's `.dandy/agent/sessions/`, and the
TUI, and processes each typed message as an agent turn. The REPL auto-saves the
conversation after every turn; the commands are `/new [name]` (fresh conversation,
optionally pre-named), `/sessions` (list saved sessions), `/resume <name>`,
`/delete <name>`, and `/quit` (or `/exit`); escape twice to exit. The welcome banner
shows a session-status line.

::: dandy.interfaces.cli.cli.DandyCli

::: dandy.interfaces.cli.tui.printer.session_banner_line

::: dandy.interfaces.cli.utils.check_or_create_settings

## The TUI

::: dandy.interfaces.cli.tui.tui.Tui

::: dandy.interfaces.cli.tui.printer.Printer

::: dandy.interfaces.cli.tui.markdown.MarkdownRenderer
    options:
        members:
            - render
