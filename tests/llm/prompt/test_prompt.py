import pathlib

from unittest import TestCase

from pydantic import BaseModel

from dandy.llm import Prompt

class TestPrompt(TestCase):
    def test_prompt(self):
        new_prompt = (
            Prompt()
            .text('Hello World')
        )

        self.assertEqual(new_prompt.to_str(), 'Hello World\n')

    def test_prompt_snippets(self):
        class Person(BaseModel):
            name: str
            age: int

        person = Person(name='John', age=30)

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
            .file(file_path=pathlib.Path(__file__).parent / 'test_document.md')
            .heading(heading='Heading Followed by a line break')
            .line_break()
            .list(items=['item1 after a line break', 'item2'])
            .model_object(model_object=person)
            .model_schema(model=Person)
            .module_source(module_name='dandy.bot.llm_bot')
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