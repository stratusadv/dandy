from typing import List, Type, Self, Dict

from pydantic import BaseModel

from dandy.llm.prompt import snippet


CHARACTERS_PER_TOKEN = 4


class Prompt:
    def __init__(
            self,
            tag: str = None
    ):
        self.snippets: List[snippet.Snippet] = []
        self.tag = tag

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

    @property
    def estimated_token_count(self) -> int:
        return int(len(self.to_str()) / CHARACTERS_PER_TOKEN)


    def title(
            self,
            title: str,
            triple_quote: bool = False
    ) -> Self:

        self.snippets.append(
            snippet.TitleSnippet(
                title=title,
                triple_quote=triple_quote
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

    def model_object(
            self,
            model_object: BaseModel,
            triple_quote: bool = False
    ) -> Self:

        self.snippets.append(
            snippet.ModelObject(
                model_object=model_object,
                triple_quote=triple_quote
            )
        )

        return self

    def model_schema(
            self,
            model: Type[BaseModel],
            triple_quote: bool = False
    ) -> Self:

        self.snippets.append(
            snippet.ModelSchema(
                model=model,
                triple_quote=triple_quote
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
            prompt: Self,
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

    def text(
            self,
            text: str,
            label: str = '',
            triple_quote: bool = False
    ) -> Self:

        self.snippets.append(
            snippet.TextSnippet(
                text=text,
                label=label,
                triple_quote=triple_quote
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
