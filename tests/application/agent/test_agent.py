from unittest import TestCase, mock

from dandy.application.agent.agent import Agent
from dandy.application.agent.exceptions import AgentCriticalError, AgentRecoverableError
from dandy.application.agent.intel import AgentSession, AgentTurnIntel
from tests.application.tool.intelligence.tools import ToolBot, WeatherTool
from dandy.domain.guard.guard import Guard, GuardOutcome
from dandy.domain.guard.repeat_guard import RepeatGuard
from dandy.domain.intel.intel import DefaultIntel
from dandy.domain.intel.typing import IntelType
from dandy.domain.prompt.prompt import Prompt
from dandy.shared.cancellation import stop_signal
from dandy.shared.exceptions import RunStoppedError
from tests.application.agent.intelligence.llm_responses import content_response, tool_call_response


def _request_messages_for_call(mock_post_request: mock.MagicMock, call_index: int) -> list[dict]:
    request_intel = mock_post_request.call_args_list[call_index].kwargs['request_intel']
    return request_intel.json_data['messages']


def _message_text(message: dict) -> str:
    content = message.get('content')

    if isinstance(content, list):
        return ''.join(part.get('text') or '' for part in content)

    return content or ''


class _TurnStartFailingGuard(Guard):
    name = 'turn-start-failing'

    def on_turn_start(
        self,
        _turn_number: int,
        _message: Prompt | str | None,
        _history_token_count: int,
        _context_window: int,
    ) -> GuardOutcome:
        return GuardOutcome(failure_message='the turn-start guard stopped the turn')


class _TurnEndFailingGuard(Guard):
    name = 'turn-end-failing'

    def on_turn_end(
        self, _turn_number: int, _result: IntelType, _history_token_count: int, _context_window: int
    ) -> GuardOutcome:
        return GuardOutcome(failure_message='the turn-end guard stopped the run')


class _TurnEndNotingGuard(Guard):
    name = 'turn-end-noting'

    def __init__(self) -> None:
        super().__init__()
        self.notes_issued = 0

    def on_turn_end(
        self, _turn_number: int, _result: IntelType, _history_token_count: int, _context_window: int
    ) -> GuardOutcome:
        if self.notes_issued == 0:
            self.notes_issued += 1
            return GuardOutcome(note='\n\n[Turn note: check the failing test next.]')
        return GuardOutcome()


class _TurnSpyingGuard(Guard):
    name = 'turn-spy'

    def __init__(self) -> None:
        super().__init__()
        self.turn_starts: list[tuple] = []
        self.turn_ends: list[tuple] = []

    def on_turn_start(
        self,
        turn_number: int,
        message: Prompt | str | None,
        history_token_count: int,
        context_window: int,
    ) -> GuardOutcome:
        self.turn_starts.append((turn_number, message, history_token_count, context_window))
        return GuardOutcome()

    def on_turn_end(
        self, turn_number: int, result: IntelType, history_token_count: int, context_window: int
    ) -> GuardOutcome:
        self.turn_ends.append((turn_number, result, history_token_count, context_window))
        return GuardOutcome()


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
    def test_turn_reports_executed_tool_calls(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Austin"}'),
            content_response('{"text": "It is sunny.", "done": true}'),
        ]

        tool_calls = []

        def record_tool_call(name: str, arguments: dict[str, object]) -> None:
            tool_calls.append((name, arguments))

        self.agent.turn('What is the weather in Austin?', tool_call_callback=record_tool_call)

        self.assertEqual(tool_calls, [('get_weather', {'location': 'Austin', 'units': 'celsius'})])

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
        self.agent.bot.llm.config.context_size = 1

        with self.assertRaises(AgentRecoverableError):
            self.agent.turn('This message is far too big for the window.')

        self.assertEqual(len(self.agent.history), 0)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_turn_stops_when_stop_signal_is_set(self, mock_post_request: mock.MagicMock) -> None:
        stop_signal.set()
        self.addCleanup(stop_signal.clear)

        with self.assertRaises(RunStoppedError):
            self.agent.turn('What is the weather in Austin?')

        self.assertEqual(mock_post_request.call_count, 0)
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

    def test_save_session_drops_dangling_tool_round(self) -> None:
        self.agent.last_request = 'What is the weather in Austin?'
        self.agent.history.add_message(role='system', text='You are a coding agent.')
        self.agent.history.add_message(role='user', text='What is the weather in Austin?')
        self.agent.history.add_message(
            role='assistant',
            tool_calls=[
                {
                    'id': 'call_1',
                    'type': 'function',
                    'function': {'name': 'get_weather', 'arguments': '{"location": "Austin"}'},
                },
                {
                    'id': 'call_2',
                    'type': 'function',
                    'function': {'name': 'get_time', 'arguments': '{"location": "Austin"}'},
                },
            ],
        )
        self.agent.history.add_message(role='tool', tool_call_id='call_1', text='Sunny and 80.')

        session = self.agent.save_session()

        self.assertEqual([message.role for message in session.messages], ['system', 'user'])
        self.assertEqual(
            [message.role for message in self.agent.history.messages], ['system', 'user']
        )

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_clear_forgets_session_metadata(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [content_response('{"text": "It is sunny.", "done": true}')]

        self.agent.turn('What is the weather in Austin?')
        self.agent.clear()

        self.assertIsNone(self.agent.last_request)
        self.assertEqual(len(self.agent.history), 0)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_save_load_session_json_round_trip(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Austin"}'),
            content_response('{"text": "It is sunny.", "done": true}'),
            content_response('{"text": "Loaded answer.", "done": true}'),
        ]

        self.agent.turn('What is the weather in Austin?')
        session_json = self.agent.save_session_json()

        fresh_agent = Agent(ToolBot(), tools=[WeatherTool()])
        fresh_agent.load_session_json(session_json)
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

    def test_save_session_json_of_empty_agent_round_trips(self) -> None:
        session_json = self.agent.save_session_json()

        self.agent.load_session_json(session_json)

        self.assertEqual(len(self.agent.history), 0)
        self.assertIsNone(self.agent.last_request)

    def test_load_session_json_rejects_invalid_json(self) -> None:
        for invalid_json in ('not a session', '{"messages": "nope"}', '{"token_count": "lots"}'):
            with self.assertRaises(AgentRecoverableError):
                self.agent.load_session_json(invalid_json)

        self.assertEqual(len(self.agent.history), 0)
        self.assertIsNone(self.agent.last_request)


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


class TestAgentGuards(TestCase):
    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_turn_start_guard_failure_stops_before_any_llm_call(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        agent = Agent(ToolBot(), tools=[WeatherTool()], guards=[_TurnStartFailingGuard()])
        mock_post_request.side_effect = [content_response('{"text": "It is sunny.", "done": true}')]

        with self.assertRaises(AgentRecoverableError) as context:
            agent.turn('What is the weather in Austin?')

        self.assertIn('turn-start guard', str(context.exception))
        self.assertEqual(mock_post_request.call_count, 0)
        self.assertEqual(len(agent.history), 0)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_turn_end_guard_failure_stops_after_the_turn(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        agent = Agent(ToolBot(), tools=[WeatherTool()], guards=[_TurnEndFailingGuard()])
        mock_post_request.side_effect = [content_response('{"text": "It is sunny.", "done": true}')]

        with self.assertRaises(AgentRecoverableError) as context:
            agent.turn('What is the weather in Austin?')

        self.assertIn('turn-end guard', str(context.exception))
        self.assertEqual(mock_post_request.call_count, 1)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_turn_end_note_steers_the_next_continuation(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        noting_guard = _TurnEndNotingGuard()
        agent = Agent(ToolBot(), tools=[WeatherTool()], guards=[noting_guard])
        mock_post_request.side_effect = [
            content_response('{"text": "First answer.", "done": false}'),
            content_response('{"text": "Second answer.", "done": true}'),
        ]

        result = agent.run('What is the weather in Austin?')

        self.assertEqual(result.text, 'Second answer.')
        self.assertEqual(mock_post_request.call_count, 2)
        self.assertIsNone(agent._pending_turn_note)

        second_turn_messages = _request_messages_for_call(mock_post_request, 1)
        user_texts = [
            _message_text(message) for message in second_turn_messages if message['role'] == 'user'
        ]
        self.assertTrue(any('Continue working on the request' in text for text in user_texts))
        self.assertTrue(any('check the failing test next' in text for text in user_texts))

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_passed_tool_guards_replace_the_defaults_and_persist_across_turns(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        repeat_guard = RepeatGuard(warning_threshold=3, stop_threshold=10)
        agent = Agent(ToolBot(), tools=[WeatherTool()], guards=[repeat_guard])
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Austin"}'),
            tool_call_response('get_weather', '{"location": "Austin"}'),
            content_response('{"text": "First answer.", "done": false}'),
            tool_call_response('get_weather', '{"location": "Austin"}'),
            tool_call_response('get_weather', '{"location": "Austin"}'),
            content_response('{"text": "Second answer.", "done": true}'),
        ]

        agent.turn('What is the weather in Austin?')
        result = agent.turn('What is the weather in Austin?')

        self.assertEqual(result.text, 'Second answer.')

        # The connector mutates one shared request body, so every captured
        # request shows the final conversation; the final state carries all
        # four executions in order, and the note appears only from the third
        # (the first turn's executions stay note-free, proving the guard
        # instance's count carried across the turns rather than a fresh
        # default guard per turn).
        final_request_tool_contents = [
            message['content']
            for message in _request_messages_for_call(
                mock_post_request, mock_post_request.call_count - 1
            )
            if message['role'] == 'tool'
        ]
        self.assertEqual(len(final_request_tool_contents), 4)
        self.assertNotIn('Note:', final_request_tool_contents[0])
        self.assertNotIn('Note:', final_request_tool_contents[1])
        self.assertIn('Note:', final_request_tool_contents[2])
        self.assertIn('3 times in this conversation', final_request_tool_contents[2])

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_clear_resets_guard_state(self, mock_post_request: mock.MagicMock) -> None:
        # Two identical calls per turn: without the clear() reset, the second
        # turn's second call would hit the stop threshold on the persisted
        # count and fail the loop.
        repeat_guard = RepeatGuard(warning_threshold=3, stop_threshold=4)
        agent = Agent(ToolBot(), tools=[WeatherTool()], guards=[repeat_guard])
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Austin"}'),
            tool_call_response('get_weather', '{"location": "Austin"}'),
            content_response('{"text": "First answer.", "done": true}'),
            tool_call_response('get_weather', '{"location": "Austin"}'),
            tool_call_response('get_weather', '{"location": "Austin"}'),
            content_response('{"text": "Second answer.", "done": true}'),
        ]

        agent.turn('What is the weather in Austin?')
        agent.clear()
        result = agent.turn('What is the weather in Austin?')

        self.assertEqual(result.text, 'Second answer.')

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_turn_number_counts_conversation_turns_and_resets_on_clear(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        spy_guard = _TurnSpyingGuard()
        agent = Agent(ToolBot(), tools=[WeatherTool()], guards=[spy_guard])
        mock_post_request.side_effect = [
            content_response('{"text": "One.", "done": true}'),
            content_response('{"text": "Two.", "done": true}'),
            content_response('{"text": "Three.", "done": true}'),
        ]

        agent.turn('First')
        agent.turn('Second')
        agent.clear()
        agent.turn('Third')

        self.assertEqual([entry[0] for entry in spy_guard.turn_starts], [1, 2, 1])
        self.assertEqual([entry[0] for entry in spy_guard.turn_ends], [1, 2, 1])
