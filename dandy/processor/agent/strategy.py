from typing import Type

from dandy.processor.agent.controller import ProcessorController
from dandy.processor.controller import BaseProcessorController
from dandy.processor.strategy import BaseProcessorsStrategy


class ProcessorsStrategy(BaseProcessorsStrategy):
    _processor_controller: Type[BaseProcessorController] = ProcessorController
