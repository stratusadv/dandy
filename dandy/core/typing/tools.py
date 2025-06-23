import inspect
from typing import Callable

from dandy.core.exceptions import DandyCriticalException
from dandy.core.typing.typing import TypedKwargsDict


def get_typed_kwargs_dict_from_callable(
        callable_: Callable,
        return_defaulted: bool = True,
) -> TypedKwargsDict:
    signature = inspect.signature(callable_)

    typed_kwargs_dict = {}

    for name, param in signature.parameters.items():
        if param.annotation is inspect._empty:
            raise DandyCriticalException(f'Parameter {name} of {cls.__qualname__} has no typed annotation')

        if param.default is inspect._empty:
            typed_kwargs_dict[name] = (param.annotation, ...)

        elif return_defaulted and param.default is not inspect._empty:
            typed_kwargs_dict[name] = (param.annotation, param.default)

    return typed_kwargs_dict