import inspect
from typing import Callable

from dandy.core.exceptions import DandyCriticalException
from dandy.core.typing.typed_kwargs import TypedKwargs


def get_typed_kwargs_from_callable(
        callable_: Callable,
        return_defaulted: bool = True,
) -> TypedKwargs:
    signature = inspect.signature(callable_)

    typed_kwargs_dict = {}

    for name, param in signature.parameters.items():
        # if name == 'self':
        #     continue

        if param.annotation is inspect._empty:
            message = f'Parameter {name} of {callable_.__qualname__} has no typed annotation'
            raise DandyCriticalException(message)

        if param.default is inspect._empty:
            typed_kwargs_dict[name] = (param.annotation, ...)

        elif return_defaulted and param.default is not inspect._empty:
            typed_kwargs_dict[name] = (param.annotation, param.default)

    return TypedKwargs(typed_kwargs_dict)