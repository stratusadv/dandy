from typing import List

from dandy.llm import snippet


class Prompt:
    def __init__(self):
        self.snippet: List[snippet.Snippet] = []

    def __str__(self):
        return self.print()

    def print(self) -> str:
        return ''.join([snippet.print() for snippet in self.snippet])

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


def schema_prompt(llm_schema: 'Schema') -> Prompt:
    return (
        Prompt()
        .title('Return a well formatted response exactly in the following valid JSON schema')
        .schema_with_types(llm_schema)
    )