from pathlib import Path

from unittest import TestCase

from dandy.intel import BaseIntel
from dandy.llm import Prompt

class TestPrompt(TestCase):
    def test_prompt(self):
        new_prompt = (
            Prompt()
            .text('Hello World')
        )

        self.assertEqual(new_prompt.to_str(), 'Hello World\n')
        self.assertEqual(str(new_prompt), new_prompt.to_str())

    def test_prompt_snippets(self):
        class PersonIntel(BaseIntel):
            name: str
            age: int

        person_intel = PersonIntel(name='John', age=30)

        another_prompt = (
            Prompt()
            .text('Hello from another prompt')
        )

        new_prompt = (
            Prompt()
            .dict(dictionary={'key': 'value'})
            .divider()
            .array(items=['item1', 'item2'])
            .array_random_order(items=['item1', 'item2'])
            .file(file_path=Path(__file__).parent / 'test_document.md')
            .file(file_path=Path(Path(__file__).parent.parent.parent.resolve(), 'assets/documents/complex_markdown.md'))
            .heading(heading='Heading Followed by a line break')
            .line_break()
            .list(items=['item1 after a line break', 'item2'])
            .intel(intel=person_intel)
            .intel_schema(intel_class=PersonIntel)
            .module_source(module_name='dandy.llm.bot.llm_bot')
            .object_source(object_module_name='dandy.llm.bot.llm_bot.BaseLlmBot')
            .ordered_list(items=['item1', 'item2'])
            .prompt(prompt=another_prompt)
            .random_choice(choices=['choice1', 'choice2'])
            .sub_heading(sub_heading='Sub Heading')
            .text('Hello World')
            .title(title='Title')
            .unordered_list(items=['item1', 'item2'])
            .unordered_random_list(items=['item1', 'item2'])
        )

        self.assertTrue(new_prompt.to_str() != '')

    def test_prompt_pydantic_typing(self):
        CUSTOM_PROMPT_STR = 'Hello from custom prompt'

        class PersonIntel(BaseIntel):
            name: str
            age: int
            custom_prompt: Prompt

        person_intel = PersonIntel(
            name='John',
            age=30,
            custom_prompt=Prompt(CUSTOM_PROMPT_STR)
        )

        self.assertTrue(person_intel.custom_prompt.to_str() == f'{CUSTOM_PROMPT_STR}\n')