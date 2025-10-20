from pydantic.main import IncEx
from typing import Type, Dict, Any, Callable

from dandy.intel.intel import BaseIntel
from dandy.intel.exceptions import IntelCriticalException


class IntelFactory:
    @staticmethod
    def _raise_invalid_intel_type(intel: BaseIntel | Type[BaseIntel]):
        message = f'{intel} is not subclass of BaseIntel or an instance of BaseIntel'
        raise IntelCriticalException(message)

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

        raise IntelFactory._raise_invalid_intel_type(intel)

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
                raise IntelCriticalException(message) from None
