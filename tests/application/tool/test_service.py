import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest import TestCase, mock

from dandy.application.agent.session import session
from dandy.application.agent.tools import EditFileTool
from dandy.infrastructure.http.intel import HttpResponseIntel
from dandy.domain.request.exceptions import LlmCriticalError, LlmRecoverableError
from dandy.domain.tool.beat import StoryBeat
from dandy.domain.tool.intel import ToolCallsIntel
from dandy.domain.tool.tool import BaseTool
from dandy.shared.cancellation import stop_signal
from dandy.shared.exceptions import RunStoppedError

from tests.application.tool.intelligence.intel import FinalAnswerIntel
from tests.application.tool.intelligence.tools import ToolBot, WeatherTool


class HandleWeatherTool(BaseTool):
    name = 'get_weather'
    description = 'Get the current weather for a location.'

    def handle(self, location: str = '') -> str:
        return f'The weather in {location} is sunny.'


class ActionOutputWeatherTool(WeatherTool):
    action_label = 'Fetching the weather'

    def action_output(self, **kwargs: Any) -> str:
        return f'for {kwargs["location"]}'


class AsciiCharWeatherTool(WeatherTool):
    action_ascii_char = '>'


class MutatingWeatherTool(WeatherTool):
    can_mutate_state = True


class RecordingWeatherTool(WeatherTool):
    def handle(self, location: str = '', units: str = 'celsius') -> str:
        self._received_kwargs.append({'location': location, 'units': units})
        return f'The weather in {location} is {units}.'


class UnexpectedWeatherTool(BaseTool):
    name = 'get_weather'
    description = 'Get the current weather for a location.'

    def handle(self, location: str, units: str = 'celsius') -> str:
        raise AssertionError('handler should not be called on invalid arguments')


class BigResultWeatherTool(WeatherTool):
    def handle(self, location: str = '') -> str:
        return 'x' * 200_000


class ConstantEchoTool(BaseTool):
    name = 'echo'
    description = 'Always returns the same output.'

    def handle(self, command: str = '') -> str:
        return 'always the same output'


class ConstantEchoBTool(BaseTool):
    name = 'echo_b'
    description = 'Second tool that returns the same output.'

    def handle(self, command: str = '') -> str:
        return 'always the same output'


def tool_call_response(
    tool_name: str, arguments: str, tool_call_id: str = 'call_1', content: str | None = None
) -> HttpResponseIntel:
    return HttpResponseIntel(
        status_code=200,
        json_data={
            'choices': [
                {
                    'message': {
                        'content': content,
                        'tool_calls': [
                            {
                                'id': tool_call_id,
                                'type': 'function',
                                'function': {'name': tool_name, 'arguments': arguments},
                            }
                        ],
                    }
                }
            ]
        },
    )


def content_response(content: str) -> HttpResponseIntel:
    return HttpResponseIntel(
        status_code=200, json_data={'choices': [{'message': {'content': content}}]}
    )


def get_request_intel(mock_post_request, call_index: int):
    call = mock_post_request.call_args_list[call_index]
    request_intel = call.kwargs.get('request_intel')

    if request_intel is None and call.args:
        request_intel = call.args[0]

    return request_intel


def get_request_messages(mock_post_request, call_index: int) -> list[dict]:
    return get_request_intel(mock_post_request, call_index).json_data['messages']


class TestToolService(TestCase):
    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_with_tools_loops_until_final_answer(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "San Francisco"}'),
            content_response('{"text": "Sunny and 70 degrees."}'),
        ]

        received_arguments = []

        def get_weather_handler(arguments_intel) -> str:
            received_arguments.append(arguments_intel)
            return f'The weather in {arguments_intel.location} is sunny.'

        bot = ToolBot()

        result = bot.llm.tools.prompt_to_intel(
            prompt='What is the weather in San Francisco?',
            intel_class=FinalAnswerIntel,
            tools=[WeatherTool],
            tool_functions={'get_weather': get_weather_handler},
        )

        self.assertIsInstance(result, FinalAnswerIntel)
        self.assertEqual(result.text, 'Sunny and 70 degrees.')

        self.assertEqual(len(received_arguments), 1)
        self.assertEqual(received_arguments[0].location, 'San Francisco')

        first_request_messages = get_request_messages(mock_post_request, 0)
        second_request_messages = get_request_messages(mock_post_request, 1)

        self.assertEqual(first_request_messages[0]['role'], 'system')
        self.assertEqual(first_request_messages[1]['role'], 'user')

        self.assertEqual(len(second_request_messages), 4)
        self.assertEqual(second_request_messages[0]['role'], 'system')
        self.assertEqual(second_request_messages[1]['role'], 'user')
        self.assertEqual(second_request_messages[2]['role'], 'assistant')
        self.assertEqual(
            second_request_messages[2]['tool_calls'][0]['function']['name'], 'get_weather'
        )
        self.assertEqual(second_request_messages[3]['role'], 'tool')
        self.assertEqual(
            second_request_messages[3]['content'], 'The weather in San Francisco is sunny.'
        )

        first_request = get_request_intel(mock_post_request, 0)

        self.assertIn('tools', first_request.json_data)
        self.assertEqual(first_request.json_data['tools'][0]['function']['name'], 'get_weather')
        self.assertNotIn('response_format', first_request.json_data)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_reports_progress_steps(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "San Francisco"}'),
            content_response('{"text": "Sunny and 70 degrees."}'),
        ]

        progress_steps = []

        bot = ToolBot()

        bot.llm.tools.prompt_to_intel(
            prompt='What is the weather in San Francisco?',
            intel_class=FinalAnswerIntel,
            tools=[HandleWeatherTool],
            progress_callback=progress_steps.append,
        )

        self.assertEqual(
            progress_steps, [StoryBeat(label='Get Weather', description='', ascii_char='•')]
        )

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_reports_summary_sentences(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response(
                'get_weather',
                '{"location": "San Francisco"}',
                content='Let me check the current weather.',
            ),
            tool_call_response(
                'get_weather', '{"location": "Paris"}', content='Checking the forecast now.'
            ),
            content_response('{"text": "Sunny and 70 degrees."}'),
        ]

        progress_steps = []

        bot = ToolBot()

        bot.llm.tools.prompt_to_intel(
            prompt='What is the weather in San Francisco?',
            intel_class=FinalAnswerIntel,
            tools=[HandleWeatherTool],
            progress_callback=progress_steps.append,
        )

        self.assertEqual(
            progress_steps,
            [
                StoryBeat(description='Let me check the current weather.', kind='narration'),
                StoryBeat(label='Get Weather', description='', ascii_char='•'),
                StoryBeat(description='Checking the forecast now.', kind='narration'),
                StoryBeat(label='Get Weather', description='', ascii_char='•'),
            ],
        )

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_reports_tool_action_label_and_output(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Paris"}'),
            content_response('{"text": "Sunny in Paris."}'),
        ]

        progress_steps = []

        bot = ToolBot()

        bot.llm.tools.prompt_to_intel(
            prompt='What is the weather in Paris?',
            intel_class=FinalAnswerIntel,
            tools=[ActionOutputWeatherTool],
            progress_callback=progress_steps.append,
        )

        self.assertEqual(
            progress_steps,
            [StoryBeat(label='Fetching the weather', description='for Paris', ascii_char='•')],
        )

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_reports_can_mutate_state_on_tool_beats(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Paris"}'),
            content_response('{"text": "Sunny in Paris."}'),
        ]

        progress_steps = []

        bot = ToolBot()

        bot.llm.tools.prompt_to_intel(
            prompt='What is the weather in Paris?',
            intel_class=FinalAnswerIntel,
            tools=[MutatingWeatherTool],
            progress_callback=progress_steps.append,
        )

        self.assertEqual(
            progress_steps,
            [
                StoryBeat(
                    label='Get Weather', description='', ascii_char='•', can_mutate_state=True
                )
            ],
        )

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_reports_tool_action_ascii_char(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Paris"}'),
            content_response('{"text": "Sunny in Paris."}'),
        ]

        progress_steps = []

        bot = ToolBot()

        bot.llm.tools.prompt_to_intel(
            prompt='What is the weather in Paris?',
            intel_class=FinalAnswerIntel,
            tools=[AsciiCharWeatherTool],
            progress_callback=progress_steps.append,
        )

        self.assertEqual(
            progress_steps, [StoryBeat(label='Get Weather', description='', ascii_char='>')]
        )

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_reports_summary_and_tool_sentence(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response(
                'get_weather', '{"location": "Paris"}', content='Let me check the weather in Paris.'
            ),
            content_response('{"text": "Sunny in Paris."}'),
        ]

        progress_steps = []

        bot = ToolBot()

        bot.llm.tools.prompt_to_intel(
            prompt='What is the weather in Paris?',
            intel_class=FinalAnswerIntel,
            tools=[ActionOutputWeatherTool],
            progress_callback=progress_steps.append,
        )

        self.assertEqual(
            progress_steps,
            [
                StoryBeat(description='Let me check the weather in Paris.', kind='narration'),
                StoryBeat(label='Fetching the weather', description='for Paris', ascii_char='•'),
            ],
        )

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_captures_summary_on_tool_calls_intel(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response(
                'get_weather', '{"location": "Paris"}', content='Fetching the weather data.'
            )
        ]

        bot = ToolBot()

        result = bot.llm.prompt_to_intel(
            prompt='What is the weather in Paris?',
            intel_class=FinalAnswerIntel,
            tools=[WeatherTool],
        )

        self.assertIsInstance(result, ToolCallsIntel)
        self.assertEqual(result.summary, 'Fetching the weather data.')

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_compacts_overgrown_history(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "A"}'),
            tool_call_response('get_weather', '{"location": "B"}'),
            content_response('{"text": "Done."}'),
        ]

        progress_steps = []

        bot = ToolBot()

        bot.llm.config.context_size = 7000

        bot.llm.tools.prompt_to_intel(
            prompt='What is the weather?',
            intel_class=FinalAnswerIntel,
            tools=[BigResultWeatherTool],
            progress_callback=progress_steps.append,
            max_tool_iterations=None,
        )

        compaction_target = int(bot.llm.config.context_size * 0.70)

        self.assertTrue(
            any(
                step.description.startswith('Compacting conversation history')
                for step in progress_steps
            )
        )
        self.assertLessEqual(bot.llm.messages.estimated_token_count, compaction_target)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_skips_compaction_within_hysteresis_band(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [content_response('{"text": "Within the band."}')]

        progress_steps = []

        bot = ToolBot()

        bot.llm.config.context_size = 6000

        while bot.llm.messages.estimated_token_count < 4400:
            bot.llm.messages.add_message(role='user', text='x' * 500)

        bot.llm.tools.prompt_to_intel(
            prompt='What is the weather?',
            intel_class=FinalAnswerIntel,
            tools=[WeatherTool],
            progress_callback=progress_steps.append,
            max_tool_iterations=None,
        )

        self.assertFalse(
            any(
                step.description.startswith('Compacting conversation history')
                for step in progress_steps
            )
        )

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_caps_oversized_tool_results(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "A"}'),
            content_response('{"text": "Done."}'),
        ]

        bot = ToolBot()

        bot.llm.tools.prompt_to_intel(
            prompt='What is the weather?',
            intel_class=FinalAnswerIntel,
            tools=[BigResultWeatherTool],
        )

        tool_messages = [message for message in bot.llm.messages.messages if message.role == 'tool']

        self.assertEqual(len(tool_messages), 1)
        self.assertLess(len(tool_messages[0].text_content), 8200)
        self.assertTrue(tool_messages[0].text_content.startswith('x' * 8000))
        self.assertTrue(tool_messages[0].text_content.endswith('\n... (truncated)'))

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_reports_verbose_details(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "San Francisco"}'),
            content_response('{"text": "Sunny and 70 degrees."}'),
        ]

        verbose_messages = []

        bot = ToolBot()

        bot.llm.tools.prompt_to_intel(
            prompt='What is the weather in San Francisco?',
            intel_class=FinalAnswerIntel,
            tools=[HandleWeatherTool],
            verbose_callback=verbose_messages.append,
        )

        self.assertIn('Round 1: model requested 1 tool call(s)', verbose_messages)
        self.assertIn('  - get_weather args: {"location": "San Francisco"}', verbose_messages)
        self.assertIn(
            '  - get_weather result: The weather in San Francisco is sunny.', verbose_messages
        )
        self.assertIn('Round 2: model returned a final response', verbose_messages)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_verbose_reports_give_up(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "San Francisco"}') for _ in range(6)
        ]

        verbose_messages = []

        bot = ToolBot()

        with self.assertRaises(LlmRecoverableError):
            bot.llm.tools.prompt_to_intel(
                prompt='What is the weather in San Francisco?',
                intel_class=FinalAnswerIntel,
                tools=[HandleWeatherTool],
                verbose_callback=verbose_messages.append,
            )

        self.assertTrue(any(message.startswith('GAVE UP:') for message in verbose_messages))

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_returns_tool_calls_manually(self, mock_post_request):
        mock_post_request.side_effect = [tool_call_response('get_weather', '{"location": "Paris"}')]

        bot = ToolBot()

        result = bot.llm.prompt_to_intel(
            prompt='What is the weather in Paris?',
            intel_class=FinalAnswerIntel,
            tools=[WeatherTool],
        )

        self.assertIsInstance(result, ToolCallsIntel)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'get_weather')
        self.assertEqual(result[0].arguments, '{"location": "Paris"}')

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_with_tools_and_invalid_arguments(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"not_a_real_field": "Paris"}'),
            content_response('{"text": "I could not get the weather."}'),
        ]

        bot = ToolBot()

        result = bot.llm.tools.prompt_to_intel(
            prompt='What is the weather in Paris?',
            intel_class=FinalAnswerIntel,
            tools=[UnexpectedWeatherTool],
        )

        self.assertEqual(result.text, 'I could not get the weather.')

        second_request_messages = get_request_messages(mock_post_request, 1)
        tool_message = second_request_messages[3]

        self.assertEqual(tool_message['role'], 'tool')
        self.assertIn('could not be validated', tool_message['content'])

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_with_tools_and_exceeded_max_iterations(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Paris"}'),
            tool_call_response('get_weather', '{"location": "Paris"}'),
            tool_call_response('get_weather', '{"location": "Paris"}'),
        ]

        bot = ToolBot()

        def get_weather_handler(arguments_intel) -> str:
            return 'Sunny.'

        with self.assertRaises(LlmRecoverableError):
            bot.llm.tools.prompt_to_intel(
                prompt='What is the weather in Paris?',
                intel_class=FinalAnswerIntel,
                tools=[WeatherTool],
                tool_functions={'get_weather': get_weather_handler},
                max_tool_iterations=2,
            )

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_with_unlimited_iterations(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Paris"}'),
            tool_call_response('get_weather', '{"location": "Paris"}'),
            tool_call_response('get_weather', '{"location": "Paris"}'),
            tool_call_response('get_weather', '{"location": "Paris"}'),
            tool_call_response('get_weather', '{"location": "Paris"}'),
            tool_call_response('get_weather', '{"location": "Paris"}'),
            content_response('{"text": "Sunny."}'),
        ]

        bot = ToolBot()

        def get_weather_handler(arguments_intel) -> str:
            return 'Sunny.'

        result = bot.llm.tools.prompt_to_intel(
            prompt='What is the weather in Paris?',
            intel_class=FinalAnswerIntel,
            tools=[WeatherTool],
            tool_functions={'get_weather': get_weather_handler},
            max_tool_iterations=None,
        )

        self.assertEqual(mock_post_request.call_count, 7)
        self.assertEqual(result.text, 'Sunny.')

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_without_tools_keeps_response_format(self, mock_post_request):
        mock_post_request.side_effect = [content_response('{"text": "Hello"}')]

        bot = ToolBot()

        result = bot.llm.prompt_to_intel(prompt='Say hello', intel_class=FinalAnswerIntel)

        self.assertEqual(result.text, 'Hello')

        request = get_request_intel(mock_post_request, 0)

        self.assertIn('response_format', request.json_data)
        self.assertNotIn('tools', request.json_data)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_with_tool_handle_method(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Chicago"}'),
            content_response('{"text": "Sunny and 75 degrees."}'),
        ]

        bot = ToolBot()

        result = bot.llm.tools.prompt_to_intel(
            prompt='What is the weather in Chicago?',
            intel_class=FinalAnswerIntel,
            tools=[HandleWeatherTool],
        )

        self.assertEqual(result.text, 'Sunny and 75 degrees.')

        second_request_messages = get_request_messages(mock_post_request, 1)

        self.assertEqual(second_request_messages[3]['content'], 'The weather in Chicago is sunny.')

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_with_unknown_tool_name(self, mock_post_request):
        mock_post_request.side_effect = [tool_call_response('some_other_tool', '{}')]

        bot = ToolBot()

        with self.assertRaises(LlmCriticalError):
            bot.llm.tools.prompt_to_intel(
                prompt='What is the weather in Paris?',
                intel_class=FinalAnswerIntel,
                tools=[WeatherTool],
            )

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_with_handle_kwargs(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Seattle"}'),
            content_response('{"text": "Rainy and 60 degrees."}'),
        ]

        received_kwargs = []

        tool = RecordingWeatherTool()
        tool._received_kwargs = received_kwargs

        bot = ToolBot()

        result = bot.llm.tools.prompt_to_intel(
            prompt='What is the weather in Seattle?', intel_class=FinalAnswerIntel, tools=[tool]
        )

        self.assertEqual(result.text, 'Rainy and 60 degrees.')
        self.assertEqual(received_kwargs, [{'location': 'Seattle', 'units': 'celsius'}])

        second_request_messages = get_request_messages(mock_post_request, 1)

        self.assertEqual(
            second_request_messages[3]['content'], 'The weather in Seattle is celsius.'
        )

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_applies_handle_defaults(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{}'),
            content_response('{"text": "Done."}'),
        ]

        received_kwargs = []

        tool = RecordingWeatherTool()
        tool._received_kwargs = received_kwargs

        bot = ToolBot()

        bot.llm.tools.prompt_to_intel(
            prompt='What is the weather?', intel_class=FinalAnswerIntel, tools=[tool]
        )

        self.assertEqual(received_kwargs, [{'location': '', 'units': 'celsius'}])

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_with_handle_and_external_handler(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Portland"}'),
            content_response('{"text": "Cloudy and 55 degrees."}'),
        ]

        received_arguments = []

        def external_handler(arguments_intel) -> str:
            received_arguments.append(arguments_intel)
            return 'External handler ran.'

        bot = ToolBot()

        result = bot.llm.tools.prompt_to_intel(
            prompt='What is the weather in Portland?',
            intel_class=FinalAnswerIntel,
            tools=[WeatherTool],
            tool_functions={'get_weather': external_handler},
        )

        self.assertEqual(result.text, 'Cloudy and 55 degrees.')
        self.assertEqual(len(received_arguments), 1)
        self.assertEqual(received_arguments[0].location, 'Portland')

        second_request_messages = get_request_messages(mock_post_request, 1)
        self.assertEqual(second_request_messages[3]['content'], 'External handler ran.')

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_includes_handle_derived_schema(self, mock_post_request):
        mock_post_request.side_effect = [content_response('{"text": "Done."}')]

        bot = ToolBot()

        bot.llm.tools.prompt_to_intel(
            prompt='What is the weather?', intel_class=FinalAnswerIntel, tools=[WeatherTool]
        )

        request = get_request_intel(mock_post_request, 0)

        tool_schema = request.json_data['tools'][0]['function']['parameters']

        self.assertEqual(set(tool_schema['properties'].keys()), {'location', 'units'})
        self.assertNotIn('required', tool_schema)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_stops_when_stop_signal_is_set(self, mock_post_request) -> None:
        stop_signal.set()
        self.addCleanup(stop_signal.clear)

        bot = ToolBot()

        with self.assertRaises(RunStoppedError):
            bot.llm.tools.prompt_to_intel(
                prompt='What is the weather?', intel_class=FinalAnswerIntel, tools=[WeatherTool]
            )

        self.assertEqual(mock_post_request.call_count, 0)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_stops_between_tool_rounds(self, mock_post_request) -> None:
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "San Francisco"}')
        ]

        def get_weather_handler(arguments_intel) -> str:
            stop_signal.set()
            return 'The weather in San Francisco is sunny.'

        self.addCleanup(stop_signal.clear)

        bot = ToolBot()

        with self.assertRaises(RunStoppedError):
            bot.llm.tools.prompt_to_intel(
                prompt='What is the weather in San Francisco?',
                intel_class=FinalAnswerIntel,
                tools=[WeatherTool],
                tool_functions={'get_weather': get_weather_handler},
            )

        # The first round ran; the second round's checkpoint raised before any
        # further LLM request.
        self.assertEqual(mock_post_request.call_count, 1)


class TestRepeatedCallGuard(TestCase):
    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_repeated_identical_call_gets_a_steering_note(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Oslo"}', tool_call_id='call_1'),
            tool_call_response('get_weather', '{"location": "Oslo"}', tool_call_id='call_2'),
            tool_call_response('get_weather', '{"location": "Oslo"}', tool_call_id='call_3'),
            content_response('{"text": "Still sunny."}'),
        ]

        bot = ToolBot()

        result = bot.llm.tools.prompt_to_intel(
            prompt='What is the weather in Oslo?',
            intel_class=FinalAnswerIntel,
            tools=[HandleWeatherTool],
            max_tool_iterations=5,
        )

        self.assertIsInstance(result, FinalAnswerIntel)

        final_request_messages = get_request_messages(
            mock_post_request, mock_post_request.call_count - 1
        )
        final_request_tool_contents = [
            message['content'] for message in final_request_messages if message['role'] == 'tool'
        ]

        self.assertEqual(len(final_request_tool_contents), 3)
        self.assertEqual(final_request_tool_contents[0], 'The weather in Oslo is sunny.')
        self.assertEqual(final_request_tool_contents[1], 'The weather in Oslo is sunny.')
        self.assertIn('Note:', final_request_tool_contents[2])
        self.assertIn('3 times in this conversation', final_request_tool_contents[2])

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_persistently_repeated_call_fails_fast(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Oslo"}', tool_call_id=f'call_{i}')
            for i in range(1, 11)
        ]

        bot = ToolBot()

        with self.assertRaises(LlmRecoverableError) as context:
            bot.llm.tools.prompt_to_intel(
                prompt='What is the weather in Oslo?',
                intel_class=FinalAnswerIntel,
                tools=[HandleWeatherTool],
                max_tool_iterations=50,
            )

        self.assertIn('repeated the identical tool call', str(context.exception))
        self.assertEqual(mock_post_request.call_count, 10)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_calls_with_different_arguments_count_separately(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Oslo"}', tool_call_id='call_1'),
            tool_call_response('get_weather', '{"location": "Tromso"}', tool_call_id='call_2'),
            tool_call_response('get_weather', '{"location": "Oslo"}', tool_call_id='call_3'),
            content_response('{"text": "Sunny everywhere."}'),
        ]

        bot = ToolBot()

        result = bot.llm.tools.prompt_to_intel(
            prompt='Weather in Oslo and Tromso?',
            intel_class=FinalAnswerIntel,
            tools=[HandleWeatherTool],
            max_tool_iterations=5,
        )

        self.assertIsInstance(result, FinalAnswerIntel)

        final_request_tool_contents = [
            message['content']
            for message in get_request_messages(mock_post_request, 3)
            if message['role'] == 'tool'
        ]
        self.assertEqual(len(final_request_tool_contents), 3)
        for tool_content in final_request_tool_contents:
            self.assertNotIn('Note:', tool_content)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_oscillating_repeats_accumulate_across_other_calls(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        # Oslo and Tromso alternate, so no two identical calls are consecutive,
        # but the Oslo call still accumulates toward the stop threshold.
        mock_post_request.side_effect = [
            tool_call_response(
                'get_weather',
                '{"location": "Oslo"}' if index % 2 == 0 else '{"location": "Tromso"}',
                tool_call_id=f'call_{index + 1}',
            )
            for index in range(19)
        ]

        bot = ToolBot()

        with self.assertRaises(LlmRecoverableError) as context:
            bot.llm.tools.prompt_to_intel(
                prompt='Weather in Oslo and Tromso?',
                intel_class=FinalAnswerIntel,
                tools=[HandleWeatherTool],
                max_tool_iterations=50,
            )

        self.assertIn('repeated the identical tool call', str(context.exception))
        self.assertEqual(mock_post_request.call_count, 19)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_retyped_calls_with_formatting_drift_share_a_signature(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        # The model re-types the same call with different key order and JSON
        # spacing; the canonical arguments keep one signature.
        mock_post_request.side_effect = [
            tool_call_response(
                'get_weather', '{"location": "Oslo", "units": "celsius"}', tool_call_id='call_1'
            ),
            tool_call_response(
                'get_weather', '{"units":"celsius","location": "Oslo"}', tool_call_id='call_2'
            ),
            tool_call_response(
                'get_weather', '{"units": "celsius",  "location":"Oslo"}', tool_call_id='call_3'
            ),
            content_response('{"text": "Sunny in Oslo."}'),
        ]

        bot = ToolBot()

        result = bot.llm.tools.prompt_to_intel(
            prompt='Weather in Oslo?',
            intel_class=FinalAnswerIntel,
            tools=[WeatherTool],
            max_tool_iterations=5,
        )

        self.assertIsInstance(result, FinalAnswerIntel)

        final_request_tool_contents = [
            message['content']
            for message in get_request_messages(mock_post_request, mock_post_request.call_count - 1)
            if message['role'] == 'tool'
        ]
        self.assertEqual(len(final_request_tool_contents), 3)
        self.assertNotIn('Note:', final_request_tool_contents[0])
        self.assertNotIn('Note:', final_request_tool_contents[1])
        self.assertIn('Note:', final_request_tool_contents[2])
        self.assertIn('exact same call', final_request_tool_contents[2])

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_retyped_calls_with_same_result_get_a_steering_note(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        # The model re-words the command every round; the arguments never match
        # exactly, but the result does, so the result counter accumulates.
        mock_post_request.side_effect = [
            tool_call_response('echo', f'{{"command": "variant {i}"}}', tool_call_id=f'call_{i}')
            for i in range(1, 4)
        ] + [content_response('{"text": "done."}')]

        bot = ToolBot()

        result = bot.llm.tools.prompt_to_intel(
            prompt='Run the echo tool.',
            intel_class=FinalAnswerIntel,
            tools=[ConstantEchoTool],
            max_tool_iterations=5,
        )

        self.assertIsInstance(result, FinalAnswerIntel)

        final_request_tool_contents = [
            message['content']
            for message in get_request_messages(mock_post_request, mock_post_request.call_count - 1)
            if message['role'] == 'tool'
        ]
        self.assertEqual(len(final_request_tool_contents), 3)
        self.assertNotIn('Note:', final_request_tool_contents[0])
        self.assertNotIn('Note:', final_request_tool_contents[1])
        self.assertIn('Note:', final_request_tool_contents[2])
        self.assertIn('exact same result', final_request_tool_contents[2])

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_retyped_calls_with_same_result_fail_fast(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [
            tool_call_response('echo', f'{{"command": "variant {i}"}}', tool_call_id=f'call_{i}')
            for i in range(1, 11)
        ]

        bot = ToolBot()

        with self.assertRaises(LlmRecoverableError) as context:
            bot.llm.tools.prompt_to_intel(
                prompt='Run the echo tool.',
                intel_class=FinalAnswerIntel,
                tools=[ConstantEchoTool],
                max_tool_iterations=50,
            )

        self.assertIn('returned the identical result', str(context.exception))
        self.assertEqual(mock_post_request.call_count, 10)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_result_counter_is_separate_per_tool_name(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        # Two tools return the same output; alternating them keeps each tool's
        # own result count at three, so notes appear but the loop never stops.
        mock_post_request.side_effect = [
            tool_call_response(
                'echo' if index % 2 == 0 else 'echo_b',
                f'{{"command": "variant {index + 1}"}}',
                tool_call_id=f'call_{index + 1}',
            )
            for index in range(6)
        ] + [content_response('{"text": "done."}')]

        bot = ToolBot()

        result = bot.llm.tools.prompt_to_intel(
            prompt='Run both echo tools.',
            intel_class=FinalAnswerIntel,
            tools=[ConstantEchoTool, ConstantEchoBTool],
            max_tool_iterations=10,
        )

        self.assertIsInstance(result, FinalAnswerIntel)

        final_request_tool_contents = [
            message['content']
            for message in get_request_messages(mock_post_request, mock_post_request.call_count - 1)
            if message['role'] == 'tool'
        ]
        noted = [content for content in final_request_tool_contents if 'Note:' in content]
        self.assertEqual(len(noted), 2)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_parallel_edits_to_one_file_do_not_trip_the_result_counter(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        # Distinct edits in one round used to share one generic success string,
        # so the result counter false-positived from the third call on.
        temp_directory_context = TemporaryDirectory()
        temp_directory_path = Path(temp_directory_context.name)
        (temp_directory_path / 'example.py').write_text('first = 1\nsecond = 2\nthird = 3\n')
        self.addCleanup(temp_directory_context.cleanup)

        original_base_path = session.project_base_path
        session.project_base_path = temp_directory_path

        def restore_base_path() -> None:
            session.project_base_path = original_base_path

        self.addCleanup(restore_base_path)

        parallel_edits = HttpResponseIntel(
            status_code=200,
            json_data={
                'choices': [
                    {
                        'message': {
                            'content': None,
                            'tool_calls': [
                                {
                                    'id': f'call_{index}',
                                    'type': 'function',
                                    'function': {
                                        'name': 'edit_file',
                                        'arguments': json.dumps(
                                            {
                                                'file_path': 'example.py',
                                                'old_string': old_string,
                                                'new_string': new_string,
                                            }
                                        ),
                                    },
                                }
                                for index, (old_string, new_string) in enumerate(
                                    [
                                        ('first = 1', 'first = 10'),
                                        ('second = 2', 'second = 20'),
                                        ('third = 3', 'third = 30'),
                                    ],
                                    start=1,
                                )
                            ],
                        }
                    }
                ]
            },
        )

        mock_post_request.side_effect = [
            parallel_edits,
            content_response('{"text": "All three edits applied."}'),
        ]

        bot = ToolBot()

        result = bot.llm.tools.prompt_to_intel(
            prompt='Apply the three edits.',
            intel_class=FinalAnswerIntel,
            tools=[EditFileTool],
            max_tool_iterations=5,
        )

        self.assertIsInstance(result, FinalAnswerIntel)

        final_request_tool_contents = [
            message['content']
            for message in get_request_messages(mock_post_request, mock_post_request.call_count - 1)
            if message['role'] == 'tool'
        ]
        self.assertEqual(len(final_request_tool_contents), 3)
        self.assertEqual(len(set(final_request_tool_contents)), 3)
        for tool_content in final_request_tool_contents:
            self.assertNotIn('Note:', tool_content)
