from pydantic.main import IncEx
from typing_extensions import Type, Union, Dict, Any

from dandy.intel import BaseIntel
from dandy.intel.exceptions import IntelCriticalException


class IntelFactory:
    @staticmethod
    def _raise_invalid_intel_type(intel: Union[BaseIntel, Type[BaseIntel]]):
        raise IntelCriticalException(f'{intel} is not subclass of BaseIntel or an instance of BaseIntel')

    @staticmethod
    def _run_for_intel_class_or_object(
            intel: Union[BaseIntel, Type[BaseIntel]],
            class_func: callable,
            object_func: callable,
            **kwargs,
    ) -> Any:
        if isinstance(intel, BaseIntel):
            return object_func(**kwargs)

        elif issubclass(intel, BaseIntel):
            return class_func(**kwargs)

        else:
            raise IntelFactory._raise_invalid_intel_type(intel)

    @classmethod
    def intel_to_json_inc_ex_schema(
            cls,
            intel: Union[BaseIntel, Type[BaseIntel]],
            include: Union[IncEx, None] = None,
            exclude: Union[IncEx, None] = None,
    ) -> Dict:
        inc_ex_kwargs = {'include': include, 'exclude': exclude}

        return cls._run_for_intel_class_or_object(
            intel=intel,
            class_func=intel.model_json_inc_ex_schema,
            object_func=intel.model_object_json_inc_ex_schema,
            **inc_ex_kwargs
        )

    @classmethod
    def json_to_intel_object(
            cls,
            json: str,
            intel: Union[BaseIntel, Type[BaseIntel]]
    ) -> BaseIntel:

        return cls._run_for_intel_class_or_object(
            intel=intel,
            class_func=intel.model_validate_json,
            object_func=intel.model_validate_json_and_copy,
            json_data=json
        )

