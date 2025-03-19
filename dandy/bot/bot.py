from abc import ABC

from dandy.core.processor.processor import BaseProcessor


class BaseBot(BaseProcessor, ABC):
    def __new__(cls, *args, **kwargs):
        print('hello')

