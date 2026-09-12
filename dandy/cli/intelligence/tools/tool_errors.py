from collections.abc import Callable
from functools import wraps
from typing import ParamSpec

from dandy.intel.intel import BaseIntel

_ToolResult = str | BaseIntel

_P = ParamSpec('_P')


def tool_error(operation: str) -> Callable[[Callable[_P, _ToolResult]], Callable[_P, _ToolResult]]:
    """Decorate a tool handle so any unexpected error returns an error message."""

    def decorator(handle_method: Callable[_P, _ToolResult]) -> Callable[_P, _ToolResult]:
        @wraps(handle_method)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _ToolResult:
            try:
                return handle_method(*args, **kwargs)
            except Exception as error:
                return f'Error {operation}: {error}'

        return wrapper

    return decorator
