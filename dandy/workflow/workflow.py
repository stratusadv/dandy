from abc import ABC

from dandy.processor.processor import BaseProcessor


class Workflow(BaseProcessor, ABC):
    ...