from typing import Callable, Type

from pydantic import create_model

from dandy.core.typing.tools import get_typed_kwargs_from_callable_signature, get_typed_kwargs_from_simple_json_schema
from dandy.core.typing.typed_kwargs import TypedKwargs
from dandy.intel.intel import BaseIntel


class IntelClassGenerator:
    @classmethod
    def from_callable_signature(
            cls,
            callable_: Callable
    ) -> Type[BaseIntel]:

        typed_kwargs = get_typed_kwargs_from_callable_signature(
            callable_
        )

        return cls.from_typed_kwargs(
            f'{callable_.__name__}Intel',
            typed_kwargs,
        )

    @classmethod
    def from_simple_json_schema(
            cls,
            simple_json_schema: dict | str,
            class_name: str = 'SimpleJsonSchemaIntel',
    ) -> Type[BaseIntel]:
        typed_kwargs = get_typed_kwargs_from_simple_json_schema(
            simple_json_schema,
        )

        return cls.from_typed_kwargs(
            class_name,
            typed_kwargs,
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
