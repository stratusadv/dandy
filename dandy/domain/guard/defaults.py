from dandy.domain.guard.context_guard import ContextPressureGuard
from dandy.domain.guard.guard import Guard
from dandy.domain.guard.repeat_guard import RepeatGuard


def default_guards() -> list[Guard]:
    """A fresh set of the shipped tool-loop guards.

    The tool loop runs a chain of these by default: the repeat guard steers
    the model out of degenerate repeat loops, and the context-pressure guard
    keeps the conversation inside the window. A fresh instance is built per
    call, so per-loop state resets with the loop unless the caller keeps its
    own instances and reuses them.
    """
    return [RepeatGuard(), ContextPressureGuard()]
