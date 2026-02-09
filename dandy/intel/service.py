from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Type

from dandy.core.service.service import BaseService
from dandy.intel.factory import IntelFactory

if TYPE_CHECKING:
    from dandy.intel.intel import BaseIntel


class IntelService(BaseService['dandy.intel.mixin.IntelServiceMixin']):

    @staticmethod
    def intel_class_from_callable_signature(
        callable_: Callable,
    ) -> Type[BaseIntel]:
        return IntelFactory.callable_signature_to_intel_class(callable_)

    @staticmethod
    def intel_class_from_simple_json_schema(
        simple_json_schema: dict | str,
    ) -> type[BaseIntel]:
        return IntelFactory.simple_json_schema_to_intel_class(simple_json_schema)

    @staticmethod
    def json_str_to_intel_object(
        json_str: str,
        intel: BaseIntel | type[BaseIntel],
    ) -> BaseIntel:
        return IntelFactory.json_str_to_intel_object(json_str=json_str, intel=intel)

    def reset(self):
        pass
