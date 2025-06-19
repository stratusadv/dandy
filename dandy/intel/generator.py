import inspect

from pydantic import create_model
from typing_extensions import Callable, Type

from dandy.intel.exceptions import IntelCriticalException
from dandy.intel.intel import BaseIntel


class IntelClassGenerator:
    @staticmethod
    def from_callable_signature(call: Callable) -> Type[BaseIntel]:
        signature = inspect.signature(call)

        intel_attributes = {}

        for name, param in signature.parameters.items():
            if param.annotation is inspect._empty:
                raise IntelCriticalException(f'Parameter {name} of {call} has no annotation')

            intel_attributes[name] = (param.annotation, ...)

        return create_model(
            f'{call.__name__}Intel',
            __base__=BaseIntel,
            **intel_attributes
        )