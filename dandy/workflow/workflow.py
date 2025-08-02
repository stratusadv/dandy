from abc import ABC

from dandy.processor import BaseProcessor


class BaseWorkflow(BaseProcessor, ABC):
    ...