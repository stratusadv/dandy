from unittest import TestCase

import dandy
from dandy import Dandy

PUBLIC_NAMES = [
    'Agent',
    'BaseIntel',
    'BaseListIntel',
    'BaseSkill',
    'BaseTool',
    'Bot',
    'DandyCriticalError',
    'DandyError',
    'DandyRecoverableError',
    'Decision',
    'DefaultIntel',
    'LlmOptions',
    'MemoryCache',
    'MessageHistory',
    'Prompt',
    'Recorder',
    'SqliteCache',
    'cache_to_memory',
    'cache_to_sqlite',
    'generate_cache_key',
    'process_to_future',
    'recorder_to_html_file',
    'recorder_to_json_file',
    'recorder_to_markdown_file',
]


class TestDandyNamespace(TestCase):
    def test_namespace_members_are_the_public_api_objects(self) -> None:
        for name in PUBLIC_NAMES:
            with self.subTest(name=name):
                self.assertIs(getattr(Dandy, name), getattr(dandy, name))

    def test_namespace_exposes_exactly_the_public_api(self) -> None:
        public = [name for name in dir(Dandy) if not name.startswith('_')]

        self.assertEqual(sorted(public), sorted(PUBLIC_NAMES))

    def test_prompt_construction_through_namespace(self) -> None:
        rendered = Dandy.Prompt().text('hello').to_str()

        self.assertEqual(rendered.strip(), 'hello')

    def test_base_skill_subclass_through_namespace(self) -> None:
        class DemoSkill(Dandy.BaseSkill):
            name = 'demo'
            description = 'A demo skill.'
            prompt = 'Do the demo.'

        skill = DemoSkill()

        self.assertEqual(skill.name, 'demo')

    def test_options_construction_through_namespace(self) -> None:
        options = Dandy.LlmOptions(temperature=0.2)

        self.assertEqual(options.temperature, 0.2)

    def test_all_lists_the_namespace_and_public_api(self) -> None:
        self.assertIn('Dandy', dandy.__all__)

        for name in dandy.__all__:
            with self.subTest(name=name):
                self.assertTrue(hasattr(dandy, name))
