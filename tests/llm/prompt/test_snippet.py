from pathlib import Path
from unittest import TestCase

from dandy.llm.prompt import snippet


class TestSnippet(TestCase):
    def setUp(self):
        self.items = [
            'Hello World',
            1.0,
            False,
            [
                'This',
                'is',
                'a',
                'list',
            ],
            888,
            (
                'This',
                'is',
                'a',
                'tuple',
            )
        ]

    def test_file_snippet(self):
        file_snippet = snippet.FileSnippet(
            file_path=Path(Path(__file__).parent.parent.parent.resolve(), 'assets/documents/complex_markdown.md')
        )

        self.assertFalse('', file_snippet.to_str())

    def test_object_source_snippet(self):
        object_source = snippet.ObjectSourceSnippet(
            object_module_name='dandy.bot.bot.Bot'
        )

        self.assertEqual(object_source.to_str()[:10], '\nclass Bot')

    def test_text_snippet(self):
        new_snippet = snippet.TextSnippet(text='Hello World')

        self.assertEqual(new_snippet.to_str(), 'Hello World\n')

    def test_text_snippet_with_label(self):
        text = 'Hello World'
        label = 'Label'

        new_snippet = snippet.TextSnippet(text=text, label=label)

        self.assertEqual(new_snippet.to_str(), f'**{label}**: {text}\n')

    def test_ordered_list_snippet(self):
        snippet.OrderedListSnippet(
            items=self.items
        )

        self.assertTrue(True)

    def test_unordered_list_snippet(self):
        snippet.UnorderedListSnippet(
            items=self.items
        )

        self.assertTrue(True)
