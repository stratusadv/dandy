from abc import abstractmethod, ABC
from typing import Any

from pydantic import BaseModel

from dandy.core.processor.processor import BaseProcessor

MapType = dict[str, tuple[str, Any]]


class _MapValidator(BaseModel):
    valid_map: MapType


class BaseMap(BaseProcessor, ABC):
    def __init__(self, map_dict: MapType):
        self.map = _MapValidator(valid_map=map_dict).model_dump()

    def choices(self) -> list[str]:
        return [choice[0] for choice in self.map.values()]

    def choices_with_descriptions(self) -> list[str]:
        return [f'{choice[0]} - "{choice[1]}"' for choice in self.map.values()]

    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        ...
