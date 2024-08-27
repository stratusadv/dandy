from abc import ABC, abstractmethod
from typing import Type, Union, Any

from pydantic import BaseModel, ValidationError


class BaseHandler(ABC):
    @classmethod
    def run(cls, input_data: Any) -> Any:
        self = cls()

        if self.validate_input_data(input_data):
            return self.process()
        else:
            raise ValueError('Input data validation failed')

    @abstractmethod
    def process(self) -> Any: ...

    @abstractmethod
    def validate_input_data(self, input_data: Any) -> bool: ...
