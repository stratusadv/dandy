from dataclasses import dataclass
from pathlib import Path

from typing_extensions import List, Type, Self, Dict
from typing_extensions import Union

from dandy.intel import BaseIntel
from dandy.llm.prompt import snippet
from dandy.llm.tokens.utils import get_estimated_token_count_for_string


@dataclass
class Prompt:
    input: Union[Self, str, None] = None,
    tag: Union[str, None] = None,

    def __post_init__(
            self,
    ):
        self.snippets: List[snippet.BaseSnippet] = []

        if isinstance(self.input, Prompt):
            self.text(text=self.input.to_str())

        if isinstance(self.input, str):
            self.text(text=self.input)

    def __str__(self) -> str:
        return self.to_str()

    def to_str(self) -> str:
        prompt_string = ''.join([_.to_str() for _ in self.snippets])

        if isinstance(self.tag, str):
            return f'<{self.tag}>\n{prompt_string}\n</{self.tag}>\n'
        else:
            return prompt_string

    def dict(
            self,
            dictionary: Dict,
            triple_quote: bool = False
    ) -> Self:

        self.snippets.append(
            snippet.DictionarySnippet(
                dictionary=dictionary,
                triple_quote=triple_quote
            )
        )

        return self

    def divider(self) -> Self:
        self.snippets.append(snippet.DividerSnippet())

        return self

    def array(self, items: List[str]) -> Self:
        self.snippets.append(snippet.ArraySnippet(items=items))

        return self

    def array_random_order(self, items: List[str]) -> Self:
        self.snippets.append(snippet.ArrayRandomOrderSnippet(items=items))

        return self

    @property
    def estimated_token_count(self) -> int:
        return get_estimated_token_count_for_string(self.to_str())


    def file(
            self,
            file_path: Union[str, Path],
            encoding: str = 'utf-8',
            triple_quote: bool = False
    ) -> Self:

        self.snippets.append(
            snippet.FileSnippet(
                file_path=file_path,
                encoding=encoding,
                triple_quote=triple_quote
            )
        )

        return self

    def heading(
            self,
            heading: str,
    ) -> Self:

        self.snippets.append(
            snippet.HeadingSnippet(
                heading=heading,
            )
        )

        return self

    def line_break(self) -> Self:
        self.snippets.append(snippet.LineBreakSnippet())

        return self

    def list(
            self,
            items: List[str],
            triple_quote: bool = False
    ) -> Self:

        self.unordered_list(
            items=items,
            triple_quote=triple_quote
        )

        return self

    def intel(
            self,
            intel: BaseIntel,
            triple_quote: bool = False
    ) -> Self:

        self.snippets.append(
            snippet.IntelSnippet(
                intel=intel,
                triple_quote=triple_quote
            )
        )

        return self

    def intel_schema(
            self,
            intel_class: Type[BaseIntel],
            triple_quote: bool = False
    ) -> Self:

        self.snippets.append(
            snippet.IntelSchemaSnippet(
                intel_class=intel_class,
                triple_quote=triple_quote
            )
        )

        return self

    def module_source(
            self,
            module_name: str,
            triple_quote: bool = True
    ) -> Self:

        self.snippets.append(
            snippet.ModuleSourceSnippet(
                module_name=module_name,
                triple_quote=triple_quote,
                triple_quote_label=module_name
            )
        )

        return self

    def object_source(
            self,
            object_module_name: str,
            triple_quote: bool = True
    ) -> Self:

        self.snippets.append(
            snippet.ObjectSourceSnippet(
                object_module_name=object_module_name,
                triple_quote=triple_quote,
                triple_quote_label=object_module_name
            )
        )

        return self

    def ordered_list(
            self,
            items: List[str],
            triple_quote: bool = False
    ) -> Self:

        self.snippets.append(
            snippet.OrderedListSnippet(
                items=items,
                triple_quote=triple_quote
            )
        )

        return self

    def prompt(
            self,
            prompt: Self | str,
            triple_quote: bool = False
    ) -> Self:

        self.snippets.append(
            snippet.PromptSnippet(
                prompt=prompt,
                triple_quote=triple_quote
            )
        )

        return self

    def random_choice(
            self,
            choices: List[str],
            triple_quote: bool = False
    ) -> Self:

        self.snippets.append(
            snippet.RandomChoiceSnippet(
                choices=choices,
                triple_quote=triple_quote,
            )
        )

        return self

    def sub_heading(
            self,
            sub_heading: str,
    ) -> Self:

        self.snippets.append(
            snippet.SubHeadingSnippet(
                sub_heading=sub_heading,
            )
        )

        return self

    def text(
            self,
            text: str = '',
            label: str = '',
            triple_quote: bool = False,
            triple_quote_label: Union[str, None] = None,
    ) -> Self:

        self.snippets.append(
            snippet.TextSnippet(
                text=text,
                label=label,
                triple_quote=triple_quote,
                triple_quote_label=triple_quote_label,
            )
        )

        return self

    def title(
            self,
            title: str,
    ) -> Self:

        self.snippets.append(
            snippet.TitleSnippet(
                title=title,
            )
        )

        return self

    def unordered_list(
            self,
            items: List[str],
            triple_quote: bool = False
    ) -> Self:

        self.snippets.append(
            snippet.UnorderedListSnippet(
                items=items,
                triple_quote=triple_quote
            )
        )

        return self

    def unordered_random_list(
            self,
            items: List[str],
            triple_quote: bool = False
    ) -> Self:

        self.snippets.append(
            snippet.UnorderedRandomListSnippet(
                items=items,
                triple_quote=triple_quote
            )
        )

        return self
