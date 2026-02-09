from typing import Any, Callable, Dict, Type

from pydantic.main import IncEx, create_model

from dandy.core.typing.tools import (
    get_typed_kwargs_from_callable_signature,
    get_typed_kwargs_from_simple_json_schema,
)
from dandy.core.typing.typed_kwargs import TypedKwargs
from dandy.intel.exceptions import IntelCriticalError
from dandy.intel.intel import BaseIntel


class IntelFactory:
    @staticmethod
    def _run_for_intel_class_or_object(
        intel: BaseIntel | Type[BaseIntel],
        class_func: Callable,
        object_func: Callable,
        **kwargs,
    ) -> Any:
        if isinstance(intel, BaseIntel):
            return object_func(**kwargs)

        if issubclass(intel, BaseIntel):
            return class_func(**kwargs)

        message = f'{intel} is not subclass of BaseIntel or an instance of BaseIntel'
        raise IntelCriticalError(message)

    @classmethod
    def intel_to_json_inc_ex_schema(
        cls,
        intel: BaseIntel | Type[BaseIntel],
        include: IncEx | None = None,
        exclude: IncEx | None = None,
    ) -> Dict:
        inc_ex_kwargs = {'include': include, 'exclude': exclude}

        json_schema = cls._run_for_intel_class_or_object(
            intel=intel,
            class_func=intel.model_json_inc_ex_schema,
            object_func=intel.model_object_json_inc_ex_schema,
            **inc_ex_kwargs,
        )

        cls._validate_json_schema_or_error(json_schema)

        return json_schema

    @classmethod
    def json_str_to_intel_object(
        cls, json_str: str, intel: BaseIntel | Type[BaseIntel]
    ) -> BaseIntel:
        return cls._run_for_intel_class_or_object(
            intel=intel,
            class_func=intel.model_validate_json,
            object_func=intel.model_validate_json_and_copy,
            json_data=json_str,
        )

    @classmethod
    def _validate_json_schema_or_error(cls, json_schema: Dict):
        required_attributes = ('allOf', 'anyOf', 'not', 'oneOf', 'type', '$ref')

        for property_ in json_schema['properties']:
            for required_attribute in required_attributes:
                if required_attribute in json_schema['properties'][property_]:
                    break

            else:
                message = f'JSON Schema property "{property_}" did not have one of f{required_attributes}.'
                raise IntelCriticalError(message) from None

    @classmethod
    def callable_signature_to_intel_class(cls, callable_: Callable) -> Type[BaseIntel]:

        typed_kwargs = get_typed_kwargs_from_callable_signature(callable_)

        return cls.typed_kwargs_to_intel_class(
            f'{callable_.__name__}Intel',
            typed_kwargs,
        )

    @classmethod
    def simple_json_schema_to_intel_class(
        cls,
        simple_json_schema: dict | str,
        class_name: str = 'SimpleJsonSchemaIntel',
    ) -> Type[BaseIntel]:
        typed_kwargs = get_typed_kwargs_from_simple_json_schema(
            simple_json_schema,
        )

        return cls.typed_kwargs_to_intel_class(
            class_name,
            typed_kwargs,
        )

    @staticmethod
    def typed_kwargs_to_intel_class(
        intel_class_name: str, typed_kwargs: TypedKwargs
    ) -> Type[BaseIntel]:
        return create_model(intel_class_name, __base__=BaseIntel, **typed_kwargs)
