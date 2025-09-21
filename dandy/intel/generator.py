import inspect
from typing import Any

from pydantic import create_model
from typing import Callable, Type, Dict, Tuple

from dandy.core.typing.typed_kwargs import TypedKwargs
from dandy.core.typing.typing import TypedKwargsDict
from dandy.intel.exceptions import IntelCriticalException
from dandy.intel.intel import BaseIntel


class IntelClassGenerator:
    @classmethod
    def from_callable_signature(
            cls,
            callable_: Callable
    ) -> Type[BaseIntel]:
        signature = inspect.signature(callable_)

        typed_kwarg_dict = {}

        for name, param in signature.parameters.items():
            if param.annotation is inspect._empty:
                message = f'Parameter {name} of {callable_} has no annotation'
                raise IntelCriticalException(message)

            typed_kwarg_dict[name] = (param.annotation, ...)

        return cls.from_typed_kwargs(
            f'{callable_.__name__}Intel',
            TypedKwargs(typed_kwarg_dict)
        )

    @staticmethod
    def from_typed_kwargs(
            intel_class_name: str,
            typed_kwargs: TypedKwargs
    ) -> Type[BaseIntel]:
        return create_model(
            intel_class_name,
            __base__=BaseIntel,
            **typed_kwargs
        )

