from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import randint, shuffle
from typing import List, Type, TYPE_CHECKING, Dict

from pydantic import BaseModel

if TYPE_CHECKING:
    from dandy.llm.prompt import Prompt


@dataclass(kw_only=True)
class Snippet(ABC):
    triple_quote: bool = False

    def __str__(self):
        return self.to_str()

    def to_str(self):
        if self.triple_quote:
            return f'"""\n{self._to_str()}\"""\n'
        else:
            return self._to_str()

    @abstractmethod
    def _to_str(self) -> str:
        pass


@dataclass(kw_only=True)
class DictionarySnippet(Snippet):
    dictionary: Dict

    def _to_str(self) -> str:
        return json.dumps(self.dictionary, indent=4)


@dataclass(kw_only=True)
class DividerSnippet(Snippet):
    def _to_str(self) -> str:
        return '----------\n'


@dataclass(kw_only=True)
class LineBreakSnippet(Snippet):
    def _to_str(self) -> str:
        return '\n'


@dataclass(kw_only=True)
class ModelObject(Snippet):
    model_object: BaseModel

    def _to_str(self) -> str:
        return self.model_object.model_dump_json(indent=4) + '\n'


@dataclass(kw_only=True)
class ModelSchema(Snippet):
    model: Type[BaseModel]

    def _to_str(self) -> str:
        return str(json.dumps(self.model.model_json_schema(), indent=4)) + '\n'


@dataclass(kw_only=True)
class OrderedListSnippet(Snippet):
    items: List[str]

    def _to_str(self) -> str:
        return '\n'.join(f'{i+1}. {item}' for i, item in enumerate(self.items)) + '\n'


@dataclass(kw_only=True)
class PromptSnippet(Snippet):
    prompt: Prompt

    def _to_str(self) -> str:
        return self.prompt.to_str()

@dataclass(kw_only=True)
class RandomChoiceSnippet(Snippet):
    choices: List[str]

    def _to_str(self) -> str:
        return f'{self.choices[randint(0, len(self.choices) - 1)]}\n'


@dataclass(kw_only=True)
class TextSnippet(Snippet):
    text: str
    label: str = ''

    def _to_str(self) -> str:
        if self.label != '':
            return f'{self.label}: {self.text}\n'
        else:
            return f'{self.text}\n'


@dataclass(kw_only=True)
class TitleSnippet(Snippet):
    title: str

    def _to_str(self) -> str:
        return f'{self.title.capitalize()}\n'


@dataclass(kw_only=True)
class UnorderedListSnippet(Snippet):
    items: List[str]

    def _to_str(self) -> str:
        return '\n'.join(f'- {item}' for item in self.items) + '\n'


@dataclass(kw_only=True)
class UnorderedRandomListSnippet(UnorderedListSnippet):
    def _to_str(self) -> str:
        shuffle(self.items)
        return '\n'.join(f'- {item}' for item in self.items) + '\n'

