from abc import abstractmethod, ABC
from pydantic import Field
from enum import Enum
from typing import Any, Type

from pydantic import BaseModel

from dandy.core.processor.processor import BaseProcessor
from dandy.map.exceptions import MapCriticalException

MapType = dict[str, Any]
_KeyedMapType = dict[int, tuple[str, Any]]


class _MapValidator(BaseModel):
    valid_map: MapType


class BaseMap(BaseProcessor, ABC):
    map: MapType
    _keyed_map: _KeyedMapType = {}

    def __new__(cls):
        if cls.map is None:
            raise MapCriticalException(f'{cls.__name__} map is not set.')

        # if _MapValidator(valid_map=cls.map):

        print(cls.map)

        print('hello')

        for i, (choice, value) in enumerate(cls.map.items()):
            cls._keyed_map[i] = (choice, value)

        return super().__new__(cls)


    @classmethod
    def keyed_choices(cls) -> list[str]:
        for i, (choice, value) in enumerate(cls.map.items(), start=1):
            cls._keyed_map[i] = (choice, value)

        return [f'{key}. "{value[0]}"' for key, value in cls._keyed_map.items()]

    @classmethod
    def get_selected_value(cls, choice_key: int) -> Any:
        return cls._keyed_map[choice_key][1]

    @classmethod
    @abstractmethod
    def process(cls, *args, **kwargs) -> Any:
        raise NotImplementedError

    @classmethod
    def as_enum(cls) -> Enum:
        enum_choices = {}
        for key, value in cls._keyed_map.items():
            enum_choices[value[0]] = key

        return Enum(f'{cls.__name__}Enum', enum_choices)
