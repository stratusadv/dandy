from __future__ import annotations

import importlib
import inspect
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from random import randint, shuffle

from typing_extensions import List, Type, TYPE_CHECKING, Dict, Union

from dandy.core.path.tools import get_file_path_or_exception
from dandy.intel import BaseIntel
from dandy.llm.exceptions import LlmCriticalException
from dandy.llm.prompt.utils import list_to_str

if TYPE_CHECKING:
    from dandy.llm.prompt import Prompt


@dataclass(kw_only=True)
class BaseSnippet(ABC):
    triple_quote: bool = False
    triple_quote_label: Union[str, None] = None

    def __str__(self):
        return self.to_str()

    def to_str(self):
        if self.triple_quote:
            if self.triple_quote_label:
                return f'""" {self.triple_quote_label}\n{self._to_str()}"""\n'

            return f'"""\n{self._to_str()}"""\n'
        else:
            return self._to_str()

    @abstractmethod
    def _to_str(self) -> str:
        pass


@dataclass(kw_only=True)
class ArraySnippet(BaseSnippet):
    items: List[str]

    def _to_str(self) -> str:
        return '[\n'+',\n'.join(f'"{item}"' for item in self.items) + '\n]\n'


@dataclass(kw_only=True)
class ArrayRandomOrderSnippet(ArraySnippet):
    def _to_str(self) -> str:
        shuffle(self.items)
        return super()._to_str()


@dataclass(kw_only=True)
class DictionarySnippet(BaseSnippet):
    dictionary: Dict

    def _to_str(self) -> str:
        return json.dumps(self.dictionary, indent=4) + '\n'


@dataclass(kw_only=True)
class DividerSnippet(BaseSnippet):
    def _to_str(self) -> str:
        return '----------\n'


@dataclass(kw_only=True)
class FileSnippet(BaseSnippet):
    file_path: Union[str, Path]
    relative_parents: int = 0
    encoding: str = 'utf-8'

    def _to_str(self) -> str:
        self.file_path = get_file_path_or_exception(
            file_path=self.file_path,
        )

        with open(self.file_path, 'r', encoding=self.encoding) as f:
            return f.read() + '\n'


@dataclass(kw_only=True)
class HeadingSnippet(BaseSnippet):
    heading: str

    def _to_str(self) -> str:
        return f'## {self.heading}\n'


@dataclass(kw_only=True)
class LineBreakSnippet(BaseSnippet):
    def _to_str(self) -> str:
        return '\n'


@dataclass(kw_only=True)
class IntelSnippet(BaseSnippet):
    intel: BaseIntel

    def _to_str(self) -> str:
        return self.intel.model_dump_json(indent=4) + '\n'


@dataclass(kw_only=True)
class IntelSchemaSnippet(BaseSnippet):
    intel_class: Type[BaseIntel]

    def _to_str(self) -> str:
        return str(json.dumps(self.intel_class.model_json_schema(), indent=4)) + '\n'


@dataclass(kw_only=True)
class ModuleSourceSnippet(BaseSnippet):
    module_name: str

    def _to_str(self) -> str:
        source = inspect.getsource(
            importlib.import_module(self.module_name)
        )

        return f'\n{source}\n'


@dataclass(kw_only=True)
class ObjectSourceSnippet(BaseSnippet):
    object_module_name: str

    def _to_str(self) -> str:
        module_name = '.'.join(self.object_module_name.split('.')[:-1])
        object_name = self.object_module_name.split('.')[-1]

        module = importlib.import_module(module_name)

        source = inspect.getsource(
            getattr(module, object_name)
        )

        return f'\n{source}\n'


@dataclass(kw_only=True)
class OrderedListSnippet(BaseSnippet):
    items: List

    def _to_str(self) -> str:
        return f'{list_to_str(items=self.items, ordered=True)}'


@dataclass(kw_only=True)
class PromptSnippet(BaseSnippet):
    prompt: Prompt | str

    def _to_str(self) -> str:
        if isinstance(self.prompt, str):
            return self.prompt
        else:
            return self.prompt.to_str()

@dataclass(kw_only=True)
class RandomChoiceSnippet(BaseSnippet):
    choices: List[str]

    def _to_str(self) -> str:
        return f'{self.choices[randint(0, len(self.choices) - 1)]}\n'


@dataclass(kw_only=True)
class SubHeadingSnippet(BaseSnippet):
    sub_heading: str

    def _to_str(self) -> str:
        return f'### {self.sub_heading}\n'


@dataclass(kw_only=True)
class TextSnippet(BaseSnippet):
    text: str
    label: str = ''
    text: str

    def _to_str(self) -> str:
        if self.label != '':
            return f'**{self.label}**: {self.text}\n'
        else:
            return f'{self.text}\n'


@dataclass(kw_only=True)
class TitleSnippet(BaseSnippet):
    title: str

    def _to_str(self) -> str:
        return f'# {self.title}\n'


@dataclass(kw_only=True)
class UnorderedListSnippet(BaseSnippet):
    items: List

    def _to_str(self) -> str:
        return f'{list_to_str(items=self.items, ordered=False)}'


@dataclass(kw_only=True)
class UnorderedRandomListSnippet(UnorderedListSnippet):
    def _to_str(self) -> str:
        shuffle(self.items)
        return super()._to_str()

