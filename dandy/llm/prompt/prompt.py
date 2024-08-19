from typing import List

from dandy.llm.prompt import snippet


class Prompt:
    def __init__(
            self,
            tag: str = None
    ):
        self.snippet: List[snippet.Snippet] = []
        self.tag = tag

    def __str__(self):
        return self.to_str()

    def to_str(self) -> str:
        prompt_string = ''.join([snippet.print() for snippet in self.snippet])

        if isinstance(self.tag, str):
            return f'<{self.tag}>\n{prompt_string}\n</{self.tag}>\n'
        else:
            return prompt_string

    def divider(self) -> 'Prompt':
        self.snippet.append(snippet.DividerSnippet())
        return self

    def title(self, title: str) -> 'Prompt':
        self.snippet.append(snippet.TitleSnippet(title))
        return self

    def line_break(self):
        self.snippet.append(snippet.LineBreakSnippet())
        return self

    def list(self, items: List[str]) -> 'Prompt':
        self.unordered_list(items)
        return self

    def schema_data(self, schema_data: 'Schema') -> 'Prompt':
        self.snippet.append(snippet.SchemaData(schema_data))
        return self

    def schema_with_types(self, schema: 'Schema') -> 'Prompt':
        self.snippet.append(snippet.SchemaWithTypesSnippet(schema))
        return self

    def ordered_list(self, items: List[str]) -> 'Prompt':
        self.snippet.append(snippet.OrderedListSnippet(items))
        return self

    def prompt(self, prompt: 'Prompt') -> 'Prompt':
        self.snippet.append(snippet.PromptSnippet(prompt))
        return self

    def text(self, text: str, label: str = '') -> 'Prompt':
        self.snippet.append(snippet.TextSnippet(text, label))
        return self

    def unordered_list(self, items: List[str]) -> 'Prompt':
        self.snippet.append(snippet.UnorderedListSnippet(items))
        return self