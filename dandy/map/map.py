from enum import Enum
from typing import Any

from pydantic import BaseModel

MapType = dict[str, Any]
_KeyedMapType = dict[int, tuple[str, Any]]


class Map(BaseModel):
    valid_map: MapType
    _keyed_map: _KeyedMapType = {}

    def model_post_init(self, __context: Any) -> None:
        for i, (choice, value) in enumerate(self.valid_map.items()):
            self._keyed_map[i] = (choice, value)

    def keyed_choices(self) -> list[str]:
        return [f'{key}. "{value[0]}"' for key, value in self._keyed_map.items()]

    def get_selected_value(self, choice_key: int) -> Any:
        return self._keyed_map[choice_key][1]

    def as_enum(self) -> Enum:
        enum_choices = {}
        for key, value in self._keyed_map.items():
            enum_choices[value[0]] = key

        return Enum(f'{self.__class__.__name__}Enum', enum_choices)
