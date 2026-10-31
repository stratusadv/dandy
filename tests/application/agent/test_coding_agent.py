from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from dandy.application.agent.agent import AGENT_MAX_CONTEXT_TOKENS_DEFAULT
from dandy.application.agent.coding_agent import CodingAgent
from dandy.application.agent.exceptions import AgentRecoverableError
from dandy.application.agent.session import session
from dandy.shared.settings import settings
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

        self.agent = CodingAgent(run_planning=False)

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()

    def _request_messages_for_call(
        self, mock_post_request: mock.MagicMock, call_index: int
    ) -> list[dict]:
        request_intel = mock_post_request.call_args_list[call_index].kwargs['request_intel']
        return request_intel.json_data['messages']

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

        compact_message_history(message_history, max_context_tokens=60)

        self.assertLessEqual(message_history.estimated_token_count, 60)
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

        self.assertNotIn('Question number 0', remaining_text)
        self.assertIn('Question number 4', remaining_text)

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
        message_history.add_message(role='user', text='Read the big file ' + ('q' * 200))
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
        message_history.add_message(
            role='tool', tool_call_id='call_1', text='Huge file contents ' + ('x' * 4000)
        )

        compact_message_history(message_history, max_context_tokens=100)

        self.assertEqual([message.role for message in message_history.messages], ['system', 'user'])

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

        self.agent = CodingAgent(run_planning=False)

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()

    def test_compaction_target_is_a_ratio_of_max_context(self) -> None:
        self.agent.max_context_tokens = 65_536

        self.assertEqual(self.agent._compaction_target_token_count(), 45_875)

        self.agent.max_context_tokens = 1000
        self.assertEqual(self.agent._compaction_target_token_count(), 700)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_agent_compacts_history_before_sending(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [
            content_response('{"text": "Acknowledged and compacted."}')
        ]

        self.agent.max_context_tokens = 300

        for _ in range(50):
            self.agent.history.add_message(
                role='user', text='Fill the conversation history with ' + ('y' * 200)
            )
            self.agent.history.add_message(
                role='assistant', text='A long assistant response ' + ('z' * 200)
            )

        progress_calls: list[str] = []

        self.agent.turn('continue', progress_callback=progress_calls.append)

        self.assertIn('Compacting conversation history', ' '.join(progress_calls))

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

    def test_compaction_counts_the_plan_section_of_the_prompt(self) -> None:
        self.agent.max_context_tokens = 2000

        raw_prompt = 'Change the greeting'
        plan_prompt = (
            Prompt()
            .text(raw_prompt)
            .line_break()
            .heading('Implementation Plan')
            .line_break()
            .text('Step one: ' + ('do the thing ' * 100))
        )

        self.agent.history = self._build_history_with_tool_rounds(12)
        self.agent._compact_history_for_next_message(message=raw_prompt)
        raw_remaining_count = len(self.agent.history)

        self.agent.history = self._build_history_with_tool_rounds(12)
        self.agent._compact_history_for_next_message(message=plan_prompt)
        plan_remaining_count = len(self.agent.history)

        self.assertLess(plan_remaining_count, raw_remaining_count)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_agent_does_not_compact_under_budget(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [content_response('{"text": "Short answer."}')]

        self.agent.max_context_tokens = 100_000

        progress_calls: list[str] = []

        self.agent.turn('short question', progress_callback=progress_calls.append)

        self.assertFalse(any('Compacting conversation history' in call for call in progress_calls))

    def test_agent_resolves_context_size_from_coding_config(self) -> None:
        self.assertEqual(self.agent.max_context_tokens, 65_536)

    def test_agent_context_size_accepts_string_values(self) -> None:
        with mock.patch.object(settings, 'LLM_CONFIGS', _coding_llm_configs(context_size='8000')):
            agent = CodingAgent(run_planning=False)

        self.assertEqual(agent.max_context_tokens, 8000)

    def test_agent_context_size_falls_back_when_absent(self) -> None:
        with mock.patch.object(settings, 'LLM_CONFIGS', _coding_llm_configs(context_size=None)):
            agent = CodingAgent(run_planning=False)

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


def user_message_text(request_intel: HttpResponseIntel, index: int = 1) -> str:
    messages = request_intel.json_data['messages']
    return ''.join(part.get('text') or '' for part in messages[index]['content'])


class TestCodingAgentPlanning(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.temp_directory_path = Path(self.temp_directory_context.name)
        self.original_project_base_path = session.project_base_path
        session.project_base_path = self.temp_directory_path

        self.agent = CodingAgent(run_planning=True)

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_turn_creates_plan_and_feeds_it_to_coding_bot(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [
            content_response('{"text": "Step 1: read the code, Step 2: edit it."}'),
            content_response('{"text": "Done."}'),
        ]

        progress_calls: list[str] = []

        result = self.agent.turn('Add a feature', progress_callback=progress_calls.append)

        self.assertEqual(result.text, 'Done.')
        self.assertEqual(mock_post_request.call_count, 2)
        self.assertIn('Planning', progress_calls)

        coding_request_intel = mock_post_request.call_args_list[1].kwargs['request_intel']
        coding_user_text = user_message_text(coding_request_intel)
        self.assertIn('Add a feature', coding_user_text)
        self.assertIn('Implementation Plan', coding_user_text)
        self.assertIn('Step 1: read the code, Step 2: edit it.', coding_user_text)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_turn_skips_planning_when_disabled(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [content_response('{"text": "Done."}')]

        self.agent.run_planning = False

        result = self.agent.turn('Add a feature')

        self.assertEqual(result.text, 'Done.')
        self.assertEqual(mock_post_request.call_count, 1)

        coding_user_text = user_message_text(mock_post_request.call_args.kwargs['request_intel'])
        self.assertIn('Add a feature', coding_user_text)
        self.assertNotIn('Implementation Plan', coding_user_text)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_planning_does_not_give_up_after_five_tool_rounds(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        responses = [tool_call_response('search_files', '{"query": "needle"}') for _ in range(6)]
        responses.append(content_response('{"text": "A plan."}'))
        responses.append(content_response('{"text": "Done."}'))
        mock_post_request.side_effect = responses

        result = self.agent.turn('Investigate then do it')

        self.assertEqual(result.text, 'Done.')
        self.assertEqual(mock_post_request.call_count, 8)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_planning_conversation_starts_fresh_each_turn(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [
            content_response('{"text": "First plan."}'),
            content_response('{"text": "First answer."}'),
            content_response('{"text": "Second plan."}'),
            content_response('{"text": "Second answer."}'),
        ]

        self.agent.turn('First request')
        self.agent.turn('Second request')

        planning_messages = self.agent.planning_bot.llm._llm_connector.request_body.messages

        self.assertEqual(
            [message.role for message in planning_messages.messages],
            ['system', 'user', 'assistant'],
        )
