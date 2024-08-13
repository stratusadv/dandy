import json
from abc import ABC
from dataclasses import asdict, dataclass
from typing import Type, Union, Self, get_type_hints

from dandy.schema.utils import get_json_type


class Schema(ABC):
    def __init_subclass__(cls, **kwargs):
        for attribute_name, attribute_type in get_type_hints(cls).items():
            setattr(cls, attribute_name, attribute_type())

    @classmethod
    def empty(cls: Type[Self]) -> Self:
        default_values = {attribute_name: attribute_type() for attribute_name, attribute_type in get_type_hints(cls).items()}

        return cls(**default_values)

    @classmethod
    def from_dict(cls, dict_data: dict):
        # This may need more logic for deeper structures or empty structures
        return cls(**dict_data)

    @classmethod
    def from_json(cls, json_data: str):
        return cls.from_dict(**json.loads(json_data))

    @classmethod
    def from_prompt_or_none(cls, prompt: 'Prompt') -> Union[Self, None]:
        pass

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_json_nicely(self) -> str:
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def to_json_with_types(cls) -> str:
        json_schema = dict()

        for attribute_name, attribute_type in get_type_hints(cls).items():
            json_schema[attribute_name] = get_json_type(attribute_type)

        return json.dumps(json_schema, indent=4)