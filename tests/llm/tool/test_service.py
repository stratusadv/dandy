from typing import Any
from unittest import TestCase, mock

from dandy.http.intelligence.intel import HttpResponseIntel
from dandy.llm.exceptions import LlmCriticalError, LlmRecoverableError
from dandy.llm.tool.intel import LlmToolCallsIntel
from dandy.tool.tool import BaseTool

from tests.llm.tool.intelligence.intel import FinalAnswerIntel
from tests.llm.tool.intelligence.tools import ToolBot, WeatherTool


class HandleWeatherTool(BaseTool):
    name = 'get_weather'
    description = 'Get the current weather for a location.'

    def handle(self, location: str = '') -> str:
        return f'The weather in {location} is sunny.'


class ActionSentenceWeatherTool(WeatherTool):
    def action_sentence(self, **kwargs: Any) -> str:
        return f'Fetching the weather for {kwargs["location"]}.'


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


class TestLlmToolService(TestCase):
    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
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

        self.assertTrue(isinstance(result, FinalAnswerIntel))
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

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
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

        self.assertEqual(progress_steps, ['Get Weather'])

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
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
                'Let me check the current weather.',
                'Get Weather',
                'Checking the forecast now.',
                'Get Weather',
            ],
        )

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_reports_tool_action_sentences(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Paris"}'),
            content_response('{"text": "Sunny in Paris."}'),
        ]

        progress_steps = []

        bot = ToolBot()

        bot.llm.tools.prompt_to_intel(
            prompt='What is the weather in Paris?',
            intel_class=FinalAnswerIntel,
            tools=[ActionSentenceWeatherTool],
            progress_callback=progress_steps.append,
        )

        self.assertEqual(progress_steps, ['Fetching the weather for Paris'])

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
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
            tools=[ActionSentenceWeatherTool],
            progress_callback=progress_steps.append,
        )

        self.assertEqual(
            progress_steps, ['Let me check the weather in Paris.', 'Fetching the weather for Paris']
        )

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
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

        self.assertTrue(isinstance(result, LlmToolCallsIntel))
        self.assertEqual(result.summary, 'Fetching the weather data.')

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_compacts_overgrown_history(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "A"}'),
            tool_call_response('get_weather', '{"location": "B"}'),
            tool_call_response('get_weather', '{"location": "C"}'),
            content_response('{"text": "Done."}'),
        ]

        progress_steps = []

        bot = ToolBot()

        bot.llm.tools.prompt_to_intel(
            prompt='What is the weather?',
            intel_class=FinalAnswerIntel,
            tools=[BigResultWeatherTool],
            progress_callback=progress_steps.append,
            max_tool_iterations=None,
        )

        compaction_target = int(bot.llm.config.context_size * 0.70)

        self.assertTrue(
            any(step.startswith('Compacting conversation history') for step in progress_steps)
        )
        self.assertLessEqual(bot.llm.messages.estimated_token_count, compaction_target)

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
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

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
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

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_returns_tool_calls_manually(self, mock_post_request):
        mock_post_request.side_effect = [tool_call_response('get_weather', '{"location": "Paris"}')]

        bot = ToolBot()

        result = bot.llm.prompt_to_intel(
            prompt='What is the weather in Paris?',
            intel_class=FinalAnswerIntel,
            tools=[WeatherTool],
        )

        self.assertTrue(isinstance(result, LlmToolCallsIntel))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'get_weather')
        self.assertEqual(result[0].arguments, '{"location": "Paris"}')

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
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

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
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

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
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

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_without_tools_keeps_response_format(self, mock_post_request):
        mock_post_request.side_effect = [content_response('{"text": "Hello"}')]

        bot = ToolBot()

        result = bot.llm.prompt_to_intel(prompt='Say hello', intel_class=FinalAnswerIntel)

        self.assertEqual(result.text, 'Hello')

        request = get_request_intel(mock_post_request, 0)

        self.assertIn('response_format', request.json_data)
        self.assertNotIn('tools', request.json_data)

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
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

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_with_unknown_tool_name(self, mock_post_request):
        mock_post_request.side_effect = [tool_call_response('some_other_tool', '{}')]

        bot = ToolBot()

        with self.assertRaises(LlmCriticalError):
            bot.llm.tools.prompt_to_intel(
                prompt='What is the weather in Paris?',
                intel_class=FinalAnswerIntel,
                tools=[WeatherTool],
            )

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
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

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
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

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
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

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
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
