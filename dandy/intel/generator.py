import inspect
from typing import Any

from pydantic import create_model
from typing_extensions import Callable, Type, Dict, Tuple

from dandy.intel.exceptions import IntelCriticalException
from dandy.intel.intel import BaseIntel


class IntelClassGenerator:
    @classmethod
    def from_callable_signature(
            cls,
            call: Callable
    ) -> Type[BaseIntel]:
        signature = inspect.signature(call)

        intel_attributes = {}

        for name, param in signature.parameters.items():
            if param.annotation is inspect._empty:
                raise IntelCriticalException(f'Parameter {name} of {call} has no annotation')

            intel_attributes[name] = (param.annotation, ...)

        return cls.from_attributes_dict(
            f'{call.__name__}Intel',
            **intel_attributes
        )

    @staticmethod
    def from_attributes_dict(
            intel_class_name: str,
            attributes_dict: Dict[str, type | Tuple[type, Any]]
    ) -> Type[BaseIntel]:
        return create_model(
            intel_class_name,
            __base__=BaseIntel,
            **attributes_dict
        )

