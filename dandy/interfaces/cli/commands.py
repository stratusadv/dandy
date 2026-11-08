from dataclasses import dataclass


@dataclass(frozen=True)
class CliCommand:
    """One CLI command as used by both the REPL (`/name`) and one-shot mode (flags).

    `argument` is 'none', 'optional', or 'required' and names the session
    name the command works on; `flag`/`short_flag` are the one-shot forms
    (absent for commands that have no one-shot meaning, like quit).
    """

    name: str
    short: str
    flag: str | None
    short_flag: str | None
    argument: str
    description: str


CLI_COMMANDS = (
    CliCommand('init', 'i', '--init', '-i', 'none', 'Create or refresh the project AGENTS.md'),
    CliCommand(
        'new', 'n', '--new', '-n', 'optional', 'Start a new conversation, optionally pre-named'
    ),
    CliCommand(
        'sessions',
        's',
        '--sessions',
        '-s',
        'optional',
        'List saved sessions, or resume one by name',
    ),
    CliCommand('resume', 'r', '--resume', '-r', 'required', 'Resume a saved session by name'),
    CliCommand('delete', 'd', '--delete', '-d', 'required', 'Delete a saved session by name'),
    CliCommand('quit', 'q', None, None, 'none', 'Exit the assistant'),
)


def resolve(name_or_short: str) -> CliCommand | None:
    """Resolve a REPL command word (full name or one-letter short) to its entry."""
    word = name_or_short.lower()
    for command in CLI_COMMANDS:
        if word in (command.name, command.short):
            return command
    return None


def commands_matching_prefix(prefix: str) -> list[CliCommand]:
    """Every command whose full name or one-letter short starts with the prefix."""
    lowered = prefix.lower()
    return [
        command
        for command in CLI_COMMANDS
        if command.name.startswith(lowered) or command.short.startswith(lowered)
    ]


def flag_lookup(flag: str) -> CliCommand | None:
    """Resolve a one-shot long or short flag to its command, or None."""
    for command in CLI_COMMANDS:
        if flag in (command.flag, command.short_flag):
            return command
    return None


def command_choices() -> str:
    """The REPL command list for help text, as '/name (or /short)' with the /exit alias."""
    choices = ', '.join(f'/{command.name} (or /{command.short})' for command in CLI_COMMANDS)
    return f'{choices}, /exit'


def flag_usage(command: CliCommand) -> str | None:
    """The one-shot flag forms of a command for the usage text, or None without them."""
    if command.flag is None:
        return None

    if command.argument == 'required':
        return f'{command.flag} <name>, {command.short_flag} <name>'
    if command.argument == 'optional':
        return f'{command.flag} [name], {command.short_flag} [name]'
    return f'{command.flag}, {command.short_flag}'
