from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from dandy.application.agent.agents_md import agents_md_section, read_agents_md


class TestReadAgentsMd(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.temp_directory_path = Path(self.temp_directory_context.name)
        self.agents_md_path = self.temp_directory_path / 'AGENTS.md'

    def tearDown(self) -> None:
        self.temp_directory_context.cleanup()

    def test_returns_none_when_the_file_is_missing(self) -> None:
        self.assertIsNone(read_agents_md(self.agents_md_path))

    def test_returns_none_when_the_file_is_blank(self) -> None:
        self.agents_md_path.write_text('\n   \n', encoding='utf-8')

        self.assertIsNone(read_agents_md(self.agents_md_path))

    def test_returns_the_stripped_content(self) -> None:
        self.agents_md_path.write_text('\n# Project notes\n\nUse make test.\n\n', encoding='utf-8')

        self.assertEqual(read_agents_md(self.agents_md_path), '# Project notes\n\nUse make test.')


class TestAgentsMdSection(TestCase):
    def test_section_wraps_the_content_in_project_instructions(self) -> None:
        rendered = agents_md_section('# Project notes\n\nUse make test.').to_str()

        self.assertIn('### Project Instructions', rendered)
        self.assertIn('# Project notes', rendered)
        self.assertIn('Use make test.', rendered)
