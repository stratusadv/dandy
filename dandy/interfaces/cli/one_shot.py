from dataclasses import dataclass

from dandy.interfaces.cli.commands import CliCommand, flag_lookup


@dataclass(frozen=True)
class OneShotPlan:
    """One parsed one-shot dandy call.

    `command` is the registry name behind the action flag found (None for a
    plain request or a bare call), `name` is the session name the flag
    consumed, and `request` is everything left over, joined for the agent.
    `repl` marks the flows that fall through into the interactive loop
    instead of running a single turn.
    """

    command: str | None = None
    name: str | None = None
    request: str = ''
    continue_latest: bool = False
    repl: bool = False


def _is_known_flag(arg: str) -> bool:
    return arg == '--continue' or flag_lookup(arg) is not None


def _scan_flags(tokens: list[str]) -> tuple[CliCommand | None, bool, str | None, list[str]] | None:
    """Split one-shot tokens into (command, continue flag, name, leftover tokens).

    A token is a flag only when it exactly equals a known long/short flag or
    `--continue`; everything else stays in the leftovers, so free-form
    requests may safely contain dashes. Returns None for conflicting or
    incomplete flag usage.
    """
    command: CliCommand | None = None
    continue_latest = False
    name: str | None = None
    rest: list[str] = []

    index = 0

    while index < len(tokens):
        arg = tokens[index]

        if arg == '--continue':
            if command is not None or continue_latest:
                return None
            continue_latest = True
            index += 1
            continue

        matched = flag_lookup(arg)

        if matched is None:
            rest.append(arg)
            index += 1
            continue

        if command is not None or continue_latest:
            return None

        command = matched
        index += 1

        if matched.argument == 'required':
            if index >= len(tokens) or _is_known_flag(tokens[index]):
                return None
            name = tokens[index]
            index += 1
        elif matched.argument == 'optional':
            if index < len(tokens) and not _is_known_flag(tokens[index]):
                name = tokens[index]
                index += 1

    return command, continue_latest, name, rest


def _plan_for(
    command: CliCommand | None, continue_latest: bool, name: str | None, request: str
) -> OneShotPlan | None:
    """Turn scanned flag parts into an action plan, or None for bad combos."""
    if continue_latest:
        return OneShotPlan(request=request, continue_latest=True) if request else None

    if command is None:
        return OneShotPlan(request=request, repl=not request)

    if command.name == 'init':
        return OneShotPlan(command='init') if not request else None

    if command.name == 'delete':
        return OneShotPlan(command='delete', name=name) if not request else None

    if command.name == 'sessions' and name is None:
        return OneShotPlan(command='sessions')

    return OneShotPlan(command=command.name, name=name, request=request, repl=not request)


def parse_one_shot(tokens: list[str]) -> OneShotPlan | None:
    """Parse one-shot argv tokens into an action plan, or None to print usage."""
    scanned = _scan_flags(tokens)

    if scanned is None:
        return None

    command, continue_latest, name, rest = scanned

    return _plan_for(command, continue_latest, name, ' '.join(rest))
