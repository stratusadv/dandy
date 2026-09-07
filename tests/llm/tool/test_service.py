from unittest import TestCase, mock

from dandy.http.intelligence.intel import HttpResponseIntel
from dandy.llm.exceptions import LlmCriticalError, LlmRecoverableError
from dandy.llm.tool.intel import LlmToolCallsIntel
from dandy.tool.exceptions import ToolCriticalError
from dandy.tool.tool import BaseTool

from tests.llm.tool.intelligence.intel import FinalAnswerIntel, WeatherIntel
from tests.llm.tool.intelligence.tools import ToolBot, WeatherTool


class HandleWeatherTool(BaseTool):
    name = 'get_weather'
    description = 'Get the current weather for a location.'
    intel_class = WeatherIntel

    def handle(self, weather_intel) -> str:
        return f'The weather in {weather_intel.location} is sunny.'


def tool_call_response(
    tool_name: str,
    arguments: str,
    tool_call_id: str = 'call_1',
) -> HttpResponseIntel:
    return HttpResponseIntel(
        status_code=200,
        json_data={
            'choices': [
                {
                    'message': {
                        'content': None,
                        'tool_calls': [
                            {
                                'id': tool_call_id,
                                'type': 'function',
                                'function': {
                                    'name': tool_name,
                                    'arguments': arguments,
                                },
                            }
                        ],
                    }
                }
            ]
        }
    )


def content_response(content: str) -> HttpResponseIntel:
    return HttpResponseIntel(
        status_code=200,
        json_data={
            'choices': [
                {
                    'message': {
                        'content': content,
                    }
                }
            ]
        }
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

        def get_weather_handler(weather_intel) -> str:
            received_arguments.append(weather_intel)
            return f'The weather in {weather_intel.location} is sunny.'

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
        self.assertTrue(isinstance(received_arguments[0], WeatherIntel))
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
            second_request_messages[2]['tool_calls'][0]['function']['name'],
            'get_weather',
        )
        self.assertEqual(second_request_messages[3]['role'], 'tool')
        self.assertEqual(
            second_request_messages[3]['content'],
            'The weather in San Francisco is sunny.',
        )

        first_request = get_request_intel(mock_post_request, 0)

        self.assertIn('tools', first_request.json_data)
        self.assertEqual(
            first_request.json_data['tools'][0]['function']['name'],
            'get_weather',
        )
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
            tools=[WeatherTool],
            tool_functions={'get_weather': HandleWeatherTool().handle},
            progress_callback=progress_steps.append,
        )

        self.assertEqual(
            progress_steps,
            ['Thinking', 'Running get_weather', 'Thinking'],
        )

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_returns_tool_calls_manually(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Paris"}'),
        ]

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
    def test_prompt_to_intel_with_tools_and_missing_tool_function(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"location": "Paris"}'),
        ]

        bot = ToolBot()

        with self.assertRaises(ToolCriticalError):
            bot.llm.tools.prompt_to_intel(
                prompt='What is the weather in Paris?',
                intel_class=FinalAnswerIntel,
                tools=[WeatherTool],
                tool_functions={},
            )

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_with_tools_and_invalid_arguments(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('get_weather', '{"not_a_real_field": "Paris"}'),
            content_response('{"text": "I could not get the weather."}'),
        ]

        bot = ToolBot()

        def get_weather_handler(weather_intel):
            raise AssertionError('handler should not be called on invalid arguments')

        result = bot.llm.tools.prompt_to_intel(
            prompt='What is the weather in Paris?',
            intel_class=FinalAnswerIntel,
            tools=[WeatherTool],
            tool_functions={'get_weather': get_weather_handler},
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

        def get_weather_handler(weather_intel) -> str:
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
    def test_prompt_to_intel_without_tools_keeps_response_format(self, mock_post_request):
        mock_post_request.side_effect = [
            content_response('{"text": "Hello"}'),
        ]

        bot = ToolBot()

        result = bot.llm.prompt_to_intel(
            prompt='Say hello',
            intel_class=FinalAnswerIntel,
        )

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

        self.assertEqual(
            second_request_messages[3]['content'],
            'The weather in Chicago is sunny.',
        )

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_with_unknown_tool_name(self, mock_post_request):
        mock_post_request.side_effect = [
            tool_call_response('some_other_tool', '{}'),
        ]

        bot = ToolBot()

        with self.assertRaises(LlmCriticalError):
            bot.llm.tools.prompt_to_intel(
                prompt='What is the weather in Paris?',
                intel_class=FinalAnswerIntel,
                tools=[WeatherTool],
            )
