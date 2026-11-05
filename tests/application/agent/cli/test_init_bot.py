from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from dandy.application.agent.cli.intelligence.bots.init_bot import InitBot
from dandy.application.agent.cli.cli_agent import CliAgent
from dandy.application.agent.cli.intelligence.prompts import init_prompt
from dandy.application.agent.session import session
from dandy.shared.settings.load import get_cli_llm_config
from tests.application.agent.intelligence.llm_responses import content_response, tool_call_response


class TestInitBot(TestCase):
    def test_init_bot_uses_the_coding_config_and_init_guidelines(self) -> None:
        bot = InitBot()

        self.assertEqual(bot.llm_config, get_cli_llm_config('CODING'))
        self.assertIn('### Writing AGENTS.md', bot.guidelines.to_str())


class TestInitPrompt(TestCase):
    def test_prompt_without_an_existing_file(self) -> None:
        rendered = init_prompt(None).to_str()

        self.assertIn('Create the project AGENTS.md file', rendered)
        self.assertNotIn('BEGIN CURRENT AGENTS.md', rendered)

    def test_prompt_inlines_the_existing_file(self) -> None:
        rendered = init_prompt('# Old notes\n\nUse make smoke.').to_str()

        self.assertIn('Refresh it', rendered)
        self.assertIn('--- BEGIN CURRENT AGENTS.md ---', rendered)
        self.assertIn('# Old notes', rendered)
        self.assertIn('Use make smoke.', rendered)
        self.assertIn('--- END CURRENT AGENTS.md ---', rendered)


class TestRunInitPass(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.temp_directory_path = Path(self.temp_directory_context.name)
        self.original_project_base_path = session.project_base_path
        session.project_base_path = self.temp_directory_path
        (self.temp_directory_path / 'README.md').write_text('# Demo project\n', encoding='utf-8')

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_init_pass_writes_agents_md_and_reloads_the_system_prompt(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [
            tool_call_response(
                'write_file',
                '{"file_path": "AGENTS.md", "content": "# Demo project\\n\\nUse make smoke."}',
            ),
            content_response('{"text": "Created AGENTS.md covering the commands."}'),
        ]

        agent = CliAgent()

        summary = agent.run_init_pass()

        self.assertEqual(summary, 'Created AGENTS.md covering the commands.')
        self.assertEqual(
            (self.temp_directory_path / 'AGENTS.md').read_text(encoding='utf-8'),
            '# Demo project\n\nUse make smoke.',
        )

        mock_post_request.side_effect = [content_response('{"text": "After init."}')]

        agent.turn('What now?')

        turn_messages = (
            mock_post_request.call_args_list[2].kwargs['request_intel'].json_data['messages']
        )
        system_text = ''.join(part.get('text') or '' for part in turn_messages[0]['content'])

        self.assertEqual(turn_messages[0]['role'], 'system')
        self.assertIn('### Project Instructions', system_text)
        self.assertIn('Use make smoke.', system_text)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_init_pass_sends_the_existing_file_in_the_prompt(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        (self.temp_directory_path / 'AGENTS.md').write_text('# Old notes\n', encoding='utf-8')
        mock_post_request.side_effect = [
            tool_call_response('write_file', '{"file_path": "AGENTS.md", "content": "# Fresh"}'),
            content_response('{"text": "Refreshed AGENTS.md."}'),
        ]

        agent = CliAgent()

        summary = agent.run_init_pass()

        self.assertEqual(summary, 'Refreshed AGENTS.md.')

        init_messages = (
            mock_post_request.call_args_list[0].kwargs['request_intel'].json_data['messages']
        )
        user_text = ''.join(
            ''.join(part.get('text') or '' for part in message['content'])
            for message in init_messages
            if message['role'] == 'user'
        )

        self.assertIn('# Old notes', user_text)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_init_pass_returns_none_when_no_file_is_written(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [content_response('{"text": "Skipped by the model."}')]

        agent = CliAgent()

        summary = agent.run_init_pass()

        self.assertIsNone(summary)
        self.assertFalse((self.temp_directory_path / 'AGENTS.md').exists())
