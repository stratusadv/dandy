import json
from abc import ABC
from dataclasses import asdict, dataclass
from typing import Type, Union, Self, get_type_hints

@dataclass
class LlmStructure(ABC):
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
    def from_prompt_or_none(cls, prompt: 'LlmPrompt') -> Union[Self, None]:
        pass

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_json_nicely(self) -> str:
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def to_json_with_types(cls) -> str:
        return "Need to write this properly"