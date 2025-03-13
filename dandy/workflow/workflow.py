from abc import ABC

from dandy.core.processor.processor import BaseProcessor


class BaseWorkflow(BaseProcessor, ABC):
    ...