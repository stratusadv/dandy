from abc import abstractmethod, ABCMeta
from typing import Any


class BaseHandler(metaclass=ABCMeta):
    pass


class ProcessHandler(BaseHandler, metaclass=ABCMeta):
    @abstractmethod
    def process_input_data(self) -> Any: ...


class ValidateHandler(BaseHandler, metaclass=ABCMeta):
    @abstractmethod
    def validate_input_data(self, input_data: Any) -> bool: ...


class RunHandler(ProcessHandler, ValidateHandler, metaclass=ABCMeta):
    @classmethod
    def run(cls, input_data: Any) -> Any:
        self = cls()
        self.input_data = input_data

        if self.validate_input_data(input_data):
            return self.process_input_data()
        else:
            raise ValueError('Input data validation failed')

