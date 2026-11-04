import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING
from unittest import TestCase, mock

if TYPE_CHECKING:
    from dandy.domain.tool.beat import StoryBeat

from dandy.application.agent.agent import (
    AGENT_MAX_CONTEXT_TOKENS_DEFAULT,
    AGENT_MAX_TOOL_ROUNDS_DEFAULT,
)
from dandy.application.agent.coding_agent import CodingAgent
from dandy.application.agent.exceptions import AgentRecoverableError
from dandy.application.agent.session import session
from dandy.application.agent.tools.question import QuestionTool
from dandy.shared.settings import settings
from dandy.domain.request.exceptions import LlmRecoverableError
from dandy.infrastructure.http.intel import HttpResponseIntel
from dandy.domain.message.message import MessageHistory, compact_message_history
from dandy.domain.prompt.prompt import Prompt
from tests.application.agent.intelligence.llm_responses import content_response, tool_call_response


class TestCodingAgentMultiTurn(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.temp_directory_path = Path(self.temp_directory_context.name)
        self.original_project_base_path = session.project_base_path
        session.project_base_path = self.temp_directory_path

        self.agent = CodingAgent()

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()

    def _request_messages_for_call(
        self, mock_post_request: mock.MagicMock, call_index: int
    ) -> list[dict]:
        request_intel = mock_post_request.call_args_list[call_index].kwargs['request_intel']
        return request_intel.json_data['messages']

    def _write_agents_md(self, content: str) -> None:
        Path(self.temp_directory_path, 'AGENTS.md').write_text(content, encoding='utf-8')

    @staticmethod
    def _message_text(message: dict) -> str:
        content = message['content']

        if isinstance(content, str):
            return content

        return ''.join(part.get('text') or '' for part in content or [])

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_system_prompt_includes_the_project_agents_md(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        self._write_agents_md('# Project notes\n\nUse the make smoke command for local checks.')
        agent = CodingAgent()
        mock_post_request.side_effect = [content_response('{"text": "Noted."}')]

        agent.turn('Say noted')

        messages = self._request_messages_for_call(mock_post_request, 0)

        self.assertEqual(messages[0]['role'], 'system')
        system_text = self._message_text(messages[0])

        self.assertIn('### Project Instructions', system_text)
        self.assertIn('Use the make smoke command for local checks.', system_text)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_system_prompt_has_no_project_instructions_without_agents_md(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        agent = CodingAgent()
        mock_post_request.side_effect = [content_response('{"text": "Noted."}')]

        agent.turn('Say noted')

        messages = self._request_messages_for_call(mock_post_request, 0)

        self.assertNotIn('### Project Instructions', self._message_text(messages[0]))

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_reload_agents_md_syncs_the_running_conversation(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        self._write_agents_md('Rule one: use make smoke.')
        agent = CodingAgent()

        responses = iter(
            [
                content_response('{"text": "First answer."}'),
                content_response('{"text": "Second answer."}'),
            ]
        )
        snapshots: list[list[dict]] = []

        def fake_request_to_response(
            request_intel: HttpResponseIntel = None, **_kwargs
        ) -> HttpResponseIntel:
            snapshots.append(copy.deepcopy(request_intel.json_data['messages']))
            return next(responses)

        mock_post_request.side_effect = fake_request_to_response

        agent.turn('First question')

        self._write_agents_md('Rule two: use make test.')
        agent.reload_agents_md()

        agent.turn('Second question')

        first_system_text = self._message_text(snapshots[0][0])
        second_system_text = self._message_text(snapshots[1][0])

        self.assertIn('Rule one: use make smoke.', first_system_text)
        self.assertIn('Rule two: use make test.', second_system_text)
        self.assertNotIn('Rule one: use make smoke.', second_system_text)

        second_user_texts = [
            self._message_text(message) for message in snapshots[1] if message['role'] == 'user'
        ]

        self.assertTrue(any('First question' in text for text in second_user_texts))

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_agent_keeps_conversation_across_turns(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [
            tool_call_response(
                'write_file', '{"file_path": "nested/agent.txt", "content": "hello agent"}'
            ),
            content_response('{"text": "Created nested/agent.txt."}'),
            tool_call_response(
                'edit_file',
                '{"file_path": "nested/agent.txt", "old_string": "hello agent", '
                '"new_string": "goodbye agent"}',
            ),
            content_response('{"text": "Updated the file to say goodbye."}'),
        ]

        first_result = self.agent.turn('Create nested/agent.txt with the text hello agent')
        second_result = self.agent.turn('Change the greeting in nested/agent.txt to goodbye agent')

        self.assertEqual(first_result.text, 'Created nested/agent.txt.')
        self.assertEqual(second_result.text, 'Updated the file to say goodbye.')
        self.assertEqual(
            Path(self.temp_directory_path, 'nested', 'agent.txt').read_text(), 'goodbye agent'
        )

        second_turn_messages = self._request_messages_for_call(mock_post_request, 3)

        roles = [message['role'] for message in second_turn_messages]

        self.assertIn('system', roles)
        self.assertIn('tool', roles)
        self.assertEqual(roles[1], 'user')
        self.assertEqual(roles[-1], 'tool')

        user_texts = [
            ''.join(part.get('text') or '' for part in message['content'])
            for message in second_turn_messages
            if message['role'] == 'user'
        ]

        self.assertTrue(
            any('Create nested/agent.txt with the text hello agent' in text for text in user_texts)
        )
        self.assertTrue(
            any(
                'Change the greeting in nested/agent.txt to goodbye agent' in text
                for text in user_texts
            )
        )

        assistant_texts = [
            ''.join(part.get('text') or '' for part in message['content'])
            for message in second_turn_messages
            if message['role'] == 'assistant' and isinstance(message['content'], list)
        ]

        self.assertIn('Created nested/agent.txt.', ' '.join(assistant_texts))

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_agent_does_not_give_up_after_five_tool_rounds(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        responses = [tool_call_response('search_files', '{"query": "needle"}') for _ in range(6)]
        responses.append(content_response('{"text": "Found it."}'))
        mock_post_request.side_effect = responses

        result = self.agent.turn('Find needle')

        self.assertEqual(result.text, 'Found it.')
        self.assertEqual(mock_post_request.call_count, 7)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_agent_turn_caps_tool_rounds(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [
            tool_call_response('search_files', f'{{"query": "needle {index}"}}')
            for index in range(AGENT_MAX_TOOL_ROUNDS_DEFAULT + 1)
        ]

        with self.assertRaises(LlmRecoverableError):
            self.agent.turn('Find needle')

        self.assertEqual(mock_post_request.call_count, AGENT_MAX_TOOL_ROUNDS_DEFAULT + 1)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_agent_does_not_compact_within_hysteresis_band(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [content_response('{"text": "Within the band."}')]

        self.agent.max_context_tokens = 6000

        while self.agent.history.estimated_token_count < 4400:
            self.agent.history.add_message(role='user', text='x' * 500)

        progress_calls: list[StoryBeat] = []

        self.agent.turn('continue', progress_callback=progress_calls.append)

        self.assertFalse(any(step.kind == 'compaction' for step in progress_calls))

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_agent_forwards_verbose_details(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [content_response('{"text": "Direct answer."}')]

        verbose_messages = []

        result = self.agent.turn('Say something', verbose_callback=verbose_messages.append)

        self.assertEqual(result.text, 'Direct answer.')
        self.assertIn('Round 1: model returned a final response', verbose_messages)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_agent_clear_resets_history(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [
            content_response('{"text": "First answer."}'),
            content_response('{"text": "Second answer before clear."}'),
            content_response('{"text": "Third answer after clear."}'),
        ]

        self.agent.turn('First question')
        self.agent.turn('Second question before clear')

        self.assertGreater(len(self.agent.history), 0)

        self.agent.clear()

        self.assertEqual(len(self.agent.history), 0)

        cleared_result = self.agent.turn('Fresh question after clear')

        self.assertEqual(cleared_result.text, 'Third answer after clear.')

        messages = self._request_messages_for_call(mock_post_request, 2)
        roles = [message['role'] for message in messages]

        self.assertEqual(roles, ['system', 'user'])


class TestCompactMessageHistory(TestCase):
    def _build_history(self) -> MessageHistory:
        message_history = MessageHistory()
        message_history.add_message(role='system', text='System rules here.')

        for index in range(5):
            message_history.add_message(role='user', text=f'Question number {index}')
            message_history.add_message(
                role='assistant',
                tool_calls=[
                    {
                        'id': f'call_{index}',
                        'type': 'function',
                        'function': {'name': 'read_file', 'arguments': '{"path": "a.py"}'},
                    }
                ],
            )
            message_history.add_message(
                role='tool',
                tool_call_id=f'call_{index}',
                text=f'File contents for question {index} ' + ('x' * 300),
            )
            message_history.add_message(role='assistant', text=f'Answer to question {index}.')

        return message_history

    def _is_well_formed(self, message_history: MessageHistory) -> bool:
        previous_was_assistant_tool_calls = False

        for message in message_history.messages:
            if message.role == 'tool' and not previous_was_assistant_tool_calls:
                return False

            previous_was_assistant_tool_calls = (
                message.role == 'assistant' and bool(message.tool_calls)
            ) or (message.role == 'tool' and previous_was_assistant_tool_calls)

        return True

    def test_compaction_brings_history_under_budget(self) -> None:
        message_history = self._build_history()

        compact_message_history(message_history, max_context_tokens=3000)

        self.assertLessEqual(message_history.estimated_token_count, 3000)
        self.assertGreater(len(message_history), 0)

    def test_compaction_keeps_system_and_newest_messages(self) -> None:
        message_history = self._build_history()
        newest_message = message_history.messages[-1]
        system_message = message_history.messages[0]

        compact_message_history(message_history, max_context_tokens=60)

        self.assertEqual(message_history.messages[0], system_message)
        self.assertEqual(message_history.messages[-1], newest_message)

    def test_compaction_drops_oldest_content(self) -> None:
        message_history = self._build_history()

        compact_message_history(message_history, max_context_tokens=60)

        remaining_text = ' '.join(message.text_content for message in message_history.messages)

        self.assertIn('Question number 0', remaining_text)
        self.assertNotIn('Question number 1', remaining_text)
        self.assertNotIn('Question number 2', remaining_text)
        self.assertIn('Answer to question 4.', remaining_text)

    def test_compaction_never_leaves_dangling_tool_messages(self) -> None:
        message_history = self._build_history()

        compact_message_history(message_history, max_context_tokens=60)

        self.assertTrue(self._is_well_formed(message_history))

    def test_compaction_is_a_noop_under_budget(self) -> None:
        message_history = self._build_history()
        original_messages = list(message_history.messages)

        compact_message_history(message_history, max_context_tokens=10_000)

        self.assertEqual(message_history.messages, original_messages)

    def test_compaction_drops_newest_round_when_newest_is_tool_result(self) -> None:
        message_history = MessageHistory()
        message_history.add_message(role='system', text='System rules here.')
        message_history.add_message(role='user', text='Read the first file')
        message_history.add_message(
            role='assistant',
            tool_calls=[
                {
                    'id': 'call_1',
                    'type': 'function',
                    'function': {'name': 'read_file', 'arguments': '{"path": "a.py"}'},
                }
            ],
        )
        message_history.add_message(role='tool', tool_call_id='call_1', text='First file contents')
        message_history.add_message(role='user', text='Now read the big file ' + ('q' * 200))
        message_history.add_message(
            role='assistant',
            tool_calls=[
                {
                    'id': 'call_2',
                    'type': 'function',
                    'function': {'name': 'read_file', 'arguments': '{"path": "b.py"}'},
                }
            ],
        )
        message_history.add_message(
            role='tool', tool_call_id='call_2', text='Huge file contents ' + ('x' * 4000)
        )

        compact_message_history(message_history, max_context_tokens=40)

        self.assertEqual(
            [message.role for message in message_history.messages],
            ['system', 'user', 'assistant', 'tool', 'user'],
        )
        self.assertEqual(message_history.messages[1].text_content, 'Read the first file')
        self.assertTrue(
            message_history.messages[4].text_content.startswith('Now read the big file')
        )

    def test_compaction_leaves_oversized_newest_message_in_place(self) -> None:
        message_history = MessageHistory()
        message_history.add_message(role='system', text='System rules here.')
        message_history.add_message(role='user', text='Pasted content ' + ('p' * 100_000))
        original_messages = list(message_history.messages)

        compact_message_history(message_history, max_context_tokens=100)

        self.assertEqual(message_history.messages, original_messages)


class TestCodingAgentCompaction(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.temp_directory_path = Path(self.temp_directory_context.name)
        self.original_project_base_path = session.project_base_path
        session.project_base_path = self.temp_directory_path

        self.agent = CodingAgent()

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()

    def test_compaction_target_is_a_ratio_of_max_context(self) -> None:
        self.agent.max_context_tokens = 65_536

        self.assertEqual(self.agent._compaction_target_token_count(), 45_875)
        self.assertEqual(self.agent._compaction_trigger_token_count(), 52_428)

        self.agent.max_context_tokens = 1000
        self.assertEqual(self.agent._compaction_target_token_count(), 700)
        self.assertEqual(self.agent._compaction_trigger_token_count(), 800)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_agent_compacts_history_before_sending(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [
            content_response('{"text": "Acknowledged and compacted."}')
        ]

        self.agent.max_context_tokens = 3000

        for _ in range(50):
            self.agent.history.add_message(
                role='user', text='Fill the conversation history with ' + ('y' * 200)
            )
            self.agent.history.add_message(
                role='assistant', text='A long assistant response ' + ('z' * 200)
            )

        progress_calls: list[StoryBeat] = []

        self.agent.turn('continue', progress_callback=progress_calls.append)

        self.assertIn(
            'Compacting my thoughts into a more manageable size',
            ' '.join(step.description for step in progress_calls),
        )

        request_intel = mock_post_request.call_args.kwargs['request_intel']
        request_messages = request_intel.json_data['messages']

        self.assertLess(len(request_messages), 100)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_agent_raises_when_conversation_cannot_fit_window(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [content_response('{"text": "Should never be sent."}')]

        self.agent.max_context_tokens = 1000

        self.agent.history.add_message(role='system', text='System rules here.')
        self.agent.history.add_message(role='user', text='A huge pasted payload ' + ('h' * 50_000))

        with self.assertRaises(AgentRecoverableError) as context:
            self.agent.turn('tiny question')

        self.assertIn('context window', str(context.exception))
        self.assertEqual(mock_post_request.call_count, 0)

    def _build_history_with_tool_rounds(self, round_count: int) -> MessageHistory:
        message_history = MessageHistory()

        for index in range(round_count):
            message_history.add_message(role='user', text=f'Question {index} ' + ('u' * 100))
            message_history.add_message(
                role='assistant',
                tool_calls=[
                    {
                        'id': f'call_{index}',
                        'type': 'function',
                        'function': {'name': 'read_file', 'arguments': '{"path": "a.py"}'},
                    }
                ],
            )
            message_history.add_message(
                role='tool', tool_call_id=f'call_{index}', text='File contents ' + ('x' * 300)
            )

        return message_history

    def test_compaction_counts_a_long_incoming_prompt(self) -> None:
        self.agent.max_context_tokens = 5000

        short_prompt = 'Change the greeting'
        long_prompt = (
            Prompt()
            .text(short_prompt)
            .line_break()
            .heading('Extra Context')
            .line_break()
            .text('Note: ' + ('do the thing ' * 100))
        )

        self.agent.history = self._build_history_with_tool_rounds(12)
        self.agent._compact_history_for_next_message(message=short_prompt)
        short_remaining_count = len(self.agent.history)

        self.agent.history = self._build_history_with_tool_rounds(12)
        self.agent._compact_history_for_next_message(message=long_prompt)
        long_remaining_count = len(self.agent.history)

        self.assertLess(long_remaining_count, short_remaining_count)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_agent_does_not_compact_under_budget(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [content_response('{"text": "Short answer."}')]

        self.agent.max_context_tokens = 100_000

        progress_calls: list[StoryBeat] = []

        self.agent.turn('short question', progress_callback=progress_calls.append)

        self.assertFalse(any(call.kind == 'compaction' for call in progress_calls))

    def test_agent_resolves_context_size_from_coding_config(self) -> None:
        self.assertEqual(self.agent.max_context_tokens, 262_144)

    def test_agent_context_size_accepts_string_values(self) -> None:
        with mock.patch.object(settings, 'LLM_CONFIGS', _coding_llm_configs(context_size='8000')):
            agent = CodingAgent()

        self.assertEqual(agent.max_context_tokens, 8000)

    def test_agent_context_size_falls_back_when_absent(self) -> None:
        with mock.patch.object(settings, 'LLM_CONFIGS', _coding_llm_configs(context_size=None)):
            agent = CodingAgent()

        self.assertEqual(agent.max_context_tokens, AGENT_MAX_CONTEXT_TOKENS_DEFAULT)


def _coding_llm_configs(context_size: int | str | None) -> dict:
    default_config = {
        'HOST': 'https://api.openai.com',
        'PORT': 443,
        'API_KEY': 'test-key',
        'MODEL': 'gpt-test',
    }

    if context_size is not None:
        default_config['CONTEXT_SIZE'] = context_size

    return {'DEFAULT': default_config, 'THINKING': {'MODEL': 'gpt-test'}}


class TestCodingAgentQuestionTool(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.temp_directory_path = Path(self.temp_directory_context.name)
        self.original_project_base_path = session.project_base_path
        session.project_base_path = self.temp_directory_path

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()

    @staticmethod
    def _question_tools(agent: CodingAgent) -> list[QuestionTool]:
        return [tool for tool in agent.tools if isinstance(tool, QuestionTool)]

    def test_tools_include_one_question_tool(self) -> None:
        agent = CodingAgent()

        self.assertEqual(len(self._question_tools(agent)), 1)
        self.assertIsNone(self._question_tools(agent)[0].ask_user)

    def test_ask_user_reaches_the_question_tool(self) -> None:
        def ask_user(question: str, choices: list[str]) -> str:
            return 'answer'

        agent = CodingAgent(ask_user=ask_user)

        self.assertIs(self._question_tools(agent)[0].ask_user, ask_user)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_turn_feeds_the_user_answer_back_to_the_model(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        agent = CodingAgent(ask_user=lambda question, choices: 'blue')
        mock_post_request.side_effect = [
            tool_call_response(
                'question',
                '{"question": "Which color should the banner be?", "choices": ["red", "blue"]}',
            ),
            content_response('{"text": "Made it blue."}'),
        ]

        result = agent.turn('Make the banner a color I like')

        self.assertEqual(result.text, 'Made it blue.')

        second_call_messages = (
            mock_post_request.call_args_list[1].kwargs['request_intel'].json_data['messages']
        )
        tool_messages = [message for message in second_call_messages if message['role'] == 'tool']

        self.assertEqual(len(tool_messages), 1)
        self.assertIn('blue', json.dumps(tool_messages))

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_turn_without_ask_user_gets_the_no_user_answer(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        agent = CodingAgent()
        mock_post_request.side_effect = [
            tool_call_response('question', '{"question": "Which color should the banner be?"}'),
            content_response('{"text": "Assumed blue."}'),
        ]

        agent.turn('Make the banner a color I like')

        second_call_messages = (
            mock_post_request.call_args_list[1].kwargs['request_intel'].json_data['messages']
        )
        tool_messages = [message for message in second_call_messages if message['role'] == 'tool']

        self.assertIn('No user is available', json.dumps(tool_messages))
