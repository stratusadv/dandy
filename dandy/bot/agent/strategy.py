from typing import Type, Sequence

from dandy.core.exceptions import DandyCriticalException
from dandy.processor.agent.controller import ProcessorController
from dandy.processor.processor import BaseProcessor


class ProcessorsStrategy:
    def __init__(self, processors: Sequence[Type[BaseProcessor]]):
        self.processors = processors

        for processor_class in self.processors:
            if not issubclass(processor_class, BaseProcessor):
                message = 'All resources must be sub classed from the "BaseProcessor" sub class.'
                raise DandyCriticalException(message)

            if processor_class.get_description() is None:
                message = (
                    f'{processor_class.__name__} did not have the class attribute "description". '
                    f'All "processors" must have a "description" class attribute to be used with a "ProcessorStrategy".'
                )
                raise DandyCriticalException(message)

    def as_dict(self) -> dict[int, type[BaseProcessor]]:
        processor_strategy_dict = {}

        for index, processor in enumerate(self.processors):
            processor_strategy_dict[index] = processor.get_description()

        return processor_strategy_dict

    def get_processor_controller_from_key(self, key: int) -> ProcessorController:
        return ProcessorController(self.processors[int(key)])

    def get_processor_module_and_qualname_from_key(self, key: int) -> str:
        processor_class = self.get_processor_controller_from_key(key).processor_class
        return f'{processor_class.__module__}.{processor_class.__qualname__}'
