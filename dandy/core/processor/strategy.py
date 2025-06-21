from __future__ import annotations

from abc import ABC

from typing_extensions import Type, Sequence, TYPE_CHECKING

from dandy.core.exceptions import DandyCriticalException
from dandy.core.processor.controller import BaseProcessorController
from dandy.core.processor.processor import BaseProcessor

if TYPE_CHECKING:
    pass


class BaseProcessorsStrategy(ABC):
    _processor_controller: Type[BaseProcessorController]

    def __init__(
            self,
            processors: Sequence[Type[BaseProcessor]]
    ):
        self.processors = processors

        if self._processor_controller is None:
            raise DandyCriticalException(f'{self.__name__}._processor_controller is not set')

        for processor_class in self.processors:
            if not issubclass(processor_class, BaseProcessor):
                raise DandyCriticalException(
                    'All resources must be sub classed from the "BaseProcessor" sub class.'
                )

            if processor_class.description is None:
                raise DandyCriticalException(
                    f'{processor_class.__name__} did not have the class attribute "description". All "processors" must have a "description" class attribute to be used with a "ProcessorStrategy".'
                )

    def as_dict(self) -> dict:
        processor_strategy_dict = {}

        for index, processor in enumerate(self.processors):
            processor_strategy_dict[index] = processor.description

        return processor_strategy_dict

    def get_processor_from_key(self, key: int) -> BaseProcessorController:
        return self._processor_controller(self.processors[int(key)])

    def get_processor_module_and_qualname_from_key(self, key: int) -> str:
        processor = self.get_processor_from_key(key).processor
        return f'{processor.__module__}.{processor.__qualname__}'
