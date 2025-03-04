import json
from abc import ABC

from pydantic import BaseModel
from pydantic.main import IncEx
from pydantic_core import from_json
from typing_extensions import Generator, Union, List, Generic, TypeVar, Self

T = TypeVar('T')

class BaseIntel(BaseModel, ABC):
    @classmethod
    def model_inc_ex_json_schema(
            cls,
            include: Union[IncEx, None] = None,
            exclude: Union[IncEx, None] = None
    ) -> dict:
        json_schema = cls.model_json_schema()

        # WRITE THIS INTO SMALL FUNCTION IN A JSON SCHEMA FOLDER I THINKS ..................

        return json_schema

    def model_validate_and_copy(self, update: dict) -> Self:
        return self.model_validate(self.model_copy(update=update))
        
    def model_validate_json_and_copy(self, update: str) -> Self:
        return self.model_validate_and_copy(update=from_json(update))
    

class BaseListIntel(BaseIntel, ABC, Generic[T]):
    items: List[T]

    def __getitem__(self, index) -> Union[List[T], T]:
        return self.items[index]

    def __iter__(self) -> Generator[T]:
        for item in self.items:
            yield item

    def __setitem__(self, index, value: T):
        self.items[index] = value

    def append(self, item: T):
        self.items.append(item)
