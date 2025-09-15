from abc import ABC, abstractmethod
from argparse import ArgumentParser
from dataclasses import dataclass

from dandy.processor.processor import BaseProcessor


@dataclass
class BaseCommand(BaseProcessor, ABC):
    @abstractmethod
    def add_arguments(self, parser: ArgumentParser):
        pass

    @property
    @abstractmethod
    def help(self) -> str:
        pass

    @abstractmethod
    def process(self, *args, **kwargs):
        pass

