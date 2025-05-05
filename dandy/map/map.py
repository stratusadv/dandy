from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Union

from pydantic import BaseModel, Field, PrivateAttr
from typing_extensions import Self


class Map(BaseModel):
    valid_map: Dict[str, Any]
    _keyed_map: Dict[str, tuple[str, Any]] = PrivateAttr(default_factory=dict)

    def __init__(self, valid_map: Dict[str, Any], **data: Any) -> None:
        super().__init__(
            valid_map=valid_map,
            **data
        )

    def __getitem__(self, item):
        return self.valid_map[item]

    def as_enum(self) -> Enum:
        enum_choices = {}
        for key, value in self._keyed_map.items():
            enum_choices[value[0]] = key

        return Enum(f'{self.__class__.__name__}Enum', enum_choices)

    def model_post_init(self, __context: Any) -> None:
        self.process_valid_to_keyed()

    @property
    def keyed_choices(self) -> list[str]:
        return [f'{key}. {value[0]}\n' for key, value in self._keyed_map.items()]

    @property
    def keyed_choices_dict(self) -> Dict[str, str]:
        return {key: value[0] for key, value in self._keyed_map.items()}

    @property
    def keyed_choices_str(self) -> str:
        return ''.join(self.keyed_choices)

    def get_selected_value(self, choice_key: str) -> Any:
        return self._keyed_map[choice_key][1]

    def process_valid_to_keyed(self):
        for i, (choice, value) in enumerate(self.valid_map.items(), start=1):
            key = str(i)
            if isinstance(value, dict):
                self._keyed_map[key] = (choice, self.process_valid_to_keyed())
            else:
                self._keyed_map[key] = (choice, value)
