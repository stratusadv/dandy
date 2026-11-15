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
    repl: bool = False


def _is_known_flag(arg: str) -> bool:
    return flag_lookup(arg) is not None


def _scan_flags(tokens: list[str]) -> tuple[CliCommand | None, str | None, list[str]] | None:
    """Split one-shot tokens into (command, name, leftover tokens).

    A token is a flag only when it exactly equals a known long/short flag;
    everything else stays in the leftovers, so free-form requests may safely
    contain dashes. A 'request' argument (the resume flag) consumes no name:
    its leftover tokens become the request. Returns None for conflicting
    flag usage.
    """
    command: CliCommand | None = None
    name: str | None = None
    rest: list[str] = []

    index = 0

    while index < len(tokens):
        arg = tokens[index]

        matched = flag_lookup(arg)

        if matched is None:
            rest.append(arg)
            index += 1
            continue

        if command is not None:
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

    return command, name, rest


def _plan_for(command: CliCommand | None, name: str | None, request: str) -> OneShotPlan | None:
    """Turn scanned flag parts into an action plan, or None for bad combos."""
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

    command, name, rest = scanned

    return _plan_for(command, name, ' '.join(rest))
