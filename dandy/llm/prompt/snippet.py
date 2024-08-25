from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import randint, shuffle
from typing import List, Type, TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from dandy.llm.prompt import Prompt


@dataclass
class Snippet(ABC):
    def __str__(self):
        return self.print()

    @abstractmethod
    def print(self) -> str:
        pass


@dataclass
class LineBreakSnippet(Snippet):
    def print(self) -> str:
        return '\n'


@dataclass
class DividerSnippet(Snippet):
    def print(self) -> str:
        return '----------\n'


@dataclass
class TitleSnippet(Snippet):
    title: str

    def print(self) -> str:
        return f'{self.title}\n'


@dataclass
class OrderedListSnippet(Snippet):
    items: List[str]

    def print(self) -> str:
        return '\n'.join(f'{i+1}. {item}' for i, item in enumerate(self.items)) + '\n'


@dataclass
class PromptSnippet(Snippet):
    prompt: Prompt

    def print(self) -> str:
        return self.prompt.to_str()

@dataclass
class RandomChoiceSnippet(Snippet):
    choices: List[str]

    def print(self) -> str:
        return f'{self.choices[randint(0, len(self.choices) - 1)]}\n'

@dataclass
class ModelObject(Snippet):
    model_object: BaseModel

    def print(self) -> str:
        return self.model_object.model_dump_json(indent=4) + '\n'


@dataclass
class Model(Snippet):
    model: Type[BaseModel]

    def print(self) -> str:
        return str(json.dumps(self.model.model_json_schema(), indent=4)) + '\n'


@dataclass
class TextSnippet(Snippet):
    text: str
    label: str = ''

    def print(self) -> str:
        if self.label != '':
            return f'{self.label}: {self.text}\n'
        else:
            return f'{self.text}\n'


@dataclass
class UnorderedListSnippet(Snippet):
    items: List[str]

    def print(self) -> str:
        return '\n'.join(f'- {item}' for item in self.items) + '\n'


@dataclass
class UnorderedRandomListSnippet(UnorderedListSnippet):
    def print(self) -> str:
        shuffle(self.items)
        return '\n'.join(f'- {item}' for item in self.items) + '\n'

