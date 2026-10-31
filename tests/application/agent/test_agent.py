from unittest import TestCase, mock

from dandy.application.agent.agent import Agent
from dandy.application.agent.exceptions import AgentCriticalError, AgentRecoverableError
from dandy.application.agent.intel import AgentSession, AgentTurnIntel
from tests.application.tool.intelligence.tools import ToolBot, WeatherTool
from dandy.domain.intel.intel import DefaultIntel
from tests.application.agent.intelligence.llm_responses import content_response, tool_call_response


def _request_messages_for_call(mock_post_request: mock.MagicMock, call_index: int) -> list[dict]:
    request_intel = mock_post_request.call_args_list[call_index].kwargs['request_intel']
    return request_intel.json_data['messages']


def _message_text(message: dict) -> str:
    content = message.get('content')

    if isinstance(content, list):
        return ''.join(part.get('text') or '' for part in content)

    return content or ''


class TestAgentTurn(TestCase):
    def setUp(self) -> None:
        self.agent = Agent(ToolBot(), tools=[WeatherTool()])

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_turn_returns_final_answer(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [content_response('{"text": "It is sunny.", "done": true}')]

        result = self.agent.turn('What is the weather in Austin?')

        self.assertIsInstance(result, AgentTurnIntel)
        self.assertEqual(result.text, 'It is sunny.')
        self.assertTrue(result.done)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_turn_works_through_tool_rounds(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Austin"}'),
            content_response('{"text": "It is sunny.", "done": false}'),
        ]

        result = self.agent.turn('What is the weather in Austin?')

        self.assertEqual(result.text, 'It is sunny.')
        self.assertFalse(result.done)
        self.assertEqual(mock_post_request.call_count, 2)

        second_call_messages = _request_messages_for_call(mock_post_request, 1)
        self.assertIn('tool', [message['role'] for message in second_call_messages])

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_turns_keep_conversation_history(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [
            content_response('{"text": "First answer.", "done": false}'),
            content_response('{"text": "Second answer.", "done": true}'),
        ]

        first = self.agent.turn('What is the weather in Austin?')
        second = self.agent.turn('And in Dallas?')

        self.assertEqual(first.text, 'First answer.')
        self.assertEqual(second.text, 'Second answer.')

        second_turn_messages = _request_messages_for_call(mock_post_request, 1)

        roles = [message['role'] for message in second_turn_messages]
        self.assertIn('system', roles)
        self.assertEqual(roles[1], 'user')

        user_texts = [
            _message_text(message) for message in second_turn_messages if message['role'] == 'user'
        ]
        self.assertTrue(any('What is the weather in Austin?' in text for text in user_texts))

        assistant_texts = [
            _message_text(message)
            for message in second_turn_messages
            if message['role'] == 'assistant'
        ]
        self.assertIn('First answer.', ' '.join(assistant_texts))

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_clear_resets_history(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [
            content_response('{"text": "First answer.", "done": false}'),
            content_response('{"text": "After clear.", "done": true}'),
        ]

        self.agent.turn('What is the weather in Austin?')
        self.agent.clear()

        result = self.agent.turn('And in Dallas?')

        self.assertEqual(result.text, 'After clear.')

        post_clear_messages = _request_messages_for_call(mock_post_request, 1)
        user_texts = [
            _message_text(message) for message in post_clear_messages if message['role'] == 'user'
        ]
        self.assertFalse(any('Austin' in text for text in user_texts))

    def test_turn_raises_when_history_and_message_exceed_window(self) -> None:
        self.agent.max_context_tokens = 1

        with self.assertRaises(AgentRecoverableError):
            self.agent.turn('This message is far too big for the window.')

        self.assertEqual(len(self.agent.history), 0)


class TestAgentSession(TestCase):
    def setUp(self) -> None:
        self.agent = Agent(ToolBot(), tools=[WeatherTool()])

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_save_session_captures_context(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [content_response('{"text": "It is sunny.", "done": true}')]

        self.agent.turn('What is the weather in Austin?')

        session = self.agent.save_session()

        self.assertEqual(session.last_request, 'What is the weather in Austin?')
        self.assertEqual(
            [message.role for message in session.messages], ['system', 'user', 'assistant']
        )
        self.assertGreater(session.token_count, 0)
        self.assertIsNotNone(session.model)
        self.assertIsNotNone(session.config)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_save_load_round_trip_keeps_conversation(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Austin"}'),
            content_response('{"text": "It is sunny.", "done": true}'),
            content_response('{"text": "Loaded answer.", "done": true}'),
        ]

        self.agent.turn('What is the weather in Austin?')
        session = AgentSession.model_validate_json(self.agent.save_session().model_dump_json())

        fresh_agent = Agent(ToolBot(), tools=[WeatherTool()])
        fresh_agent.load_session(session)
        result = fresh_agent.turn('And in Dallas?')

        self.assertEqual(result.text, 'Loaded answer.')
        self.assertEqual(fresh_agent.last_request, 'And in Dallas?')

        resumed_messages = _request_messages_for_call(mock_post_request, 2)
        user_texts = [
            _message_text(message) for message in resumed_messages if message['role'] == 'user'
        ]
        self.assertTrue(any('Austin' in text for text in user_texts))
        self.assertTrue(any('Dallas' in text for text in user_texts))
        self.assertIn('tool', [message['role'] for message in resumed_messages])

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_clear_forgets_session_metadata(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [content_response('{"text": "It is sunny.", "done": true}')]

        self.agent.turn('What is the weather in Austin?')
        self.agent.clear()

        self.assertIsNone(self.agent.last_request)
        self.assertEqual(len(self.agent.history), 0)


class TestAgentRun(TestCase):
    def setUp(self) -> None:
        self.agent = Agent(ToolBot(), tools=[WeatherTool()])

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_run_stops_when_done(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [
            content_response('{"text": "Started the work.", "done": false}'),
            content_response('{"text": "All done.", "done": true}'),
        ]

        result = self.agent.run('Do the thing.')

        self.assertEqual(result.text, 'All done.')
        self.assertTrue(result.done)
        self.assertEqual(mock_post_request.call_count, 2)

        second_turn_messages = _request_messages_for_call(mock_post_request, 1)
        user_texts = [
            _message_text(message) for message in second_turn_messages if message['role'] == 'user'
        ]
        self.assertTrue(any('Do the thing.' in text for text in user_texts))
        self.assertTrue(any('Continue working on the request' in text for text in user_texts))

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_run_returns_immediately_when_first_turn_is_done(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [
            content_response('{"text": "Already done.", "done": true}')
        ]

        result = self.agent.run('Do the thing.')

        self.assertEqual(result.text, 'Already done.')
        self.assertEqual(mock_post_request.call_count, 1)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_run_is_done_callback_wins_and_needs_no_done_field(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        agent = Agent(ToolBot(), intel_class=DefaultIntel)
        mock_post_request.side_effect = [
            content_response('{"text": "Step one."}'),
            content_response('{"text": "Step two."}'),
        ]

        result = agent.run('Go.', is_done=lambda intel: intel.text == 'Step two.')

        self.assertEqual(result.text, 'Step two.')
        self.assertEqual(mock_post_request.call_count, 2)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_run_without_done_field_or_callback_raises_critical(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        agent = Agent(ToolBot(), intel_class=DefaultIntel)

        with self.assertRaises(AgentCriticalError):
            agent.run('Go.')

        self.assertEqual(mock_post_request.call_count, 0)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_run_gives_up_at_max_turns(self, mock_post_request: mock.MagicMock) -> None:
        agent = Agent(ToolBot(), max_turns=3)
        mock_post_request.side_effect = [
            content_response('{"text": "Still working.", "done": false}'),
            content_response('{"text": "Still working.", "done": false}'),
            content_response('{"text": "Still working.", "done": false}'),
        ]

        with self.assertRaises(AgentRecoverableError):
            agent.run('Do the thing.')

        self.assertEqual(mock_post_request.call_count, 3)
