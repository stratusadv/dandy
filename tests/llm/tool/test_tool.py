from unittest import TestCase

from dandy.intel.exceptions import IntelCriticalError
from dandy.tool.exceptions import ToolCriticalError
from dandy.llm.request.message import Message, MessageHistory
from dandy.tool.tool import BaseTool, to_tool_instances

from tests.llm.tool.intelligence.intel import (
    WeatherIntel,
)
from tests.llm.tool.intelligence.tools import (
    MinimalWeatherTool,
    NoUnitsWeatherTool,
    RequiredUnitsWeatherTool,
    WeatherTool,
)


class NoArgumentsTool(BaseTool):
    name = 'no_arguments_tool'


class MissingNameTool(BaseTool):
    pass


class IncludeAndExcludeTool(BaseTool):
    name = 'get_weather'
    intel_class = WeatherIntel
    include_fields = {'location'}
    exclude_fields = {'units'}


class TestBaseTool(TestCase):
    def test_subclass_defines_class_attributes(self):
        tool = WeatherTool()

        self.assertEqual(tool.name, 'get_weather')
        self.assertEqual(tool.description, 'Get the current weather for a location.')
        self.assertIs(tool.intel_class, WeatherIntel)

    def test_to_function_dict_with_intel_class(self):
        tool = WeatherTool()

        tool_dict = tool.to_function_dict()

        self.assertEqual(tool_dict['type'], 'function')
        self.assertEqual(tool_dict['function']['name'], 'get_weather')
        self.assertEqual(
            tool_dict['function']['description'],
            'Get the current weather for a location.',
        )

        parameters = tool_dict['function']['parameters']

        self.assertEqual(parameters['type'], 'object')
        self.assertEqual(parameters['properties']['location']['type'], 'string')
        self.assertIn('location', parameters['required'])

    def test_to_function_dict_without_intel_class(self):
        tool = NoArgumentsTool()

        tool_dict = tool.to_function_dict()

        self.assertEqual(tool_dict['function']['parameters'], {})

    def test_to_function_dict_with_include_fields(self):
        tool = MinimalWeatherTool()

        parameters = tool.to_function_dict()['function']['parameters']

        self.assertEqual(set(parameters['properties'].keys()), {'location'})
        self.assertEqual(parameters['required'], ['location'])

    def test_to_function_dict_with_exclude_fields(self):
        tool = NoUnitsWeatherTool()

        parameters = tool.to_function_dict()['function']['parameters']

        self.assertEqual(set(parameters['properties'].keys()), {'location'})
        self.assertEqual(parameters['required'], ['location'])

    def test_premade_required_units_weather_tool(self):
        parameters = RequiredUnitsWeatherTool().to_function_dict()['function']['parameters']

        self.assertEqual(set(parameters['properties'].keys()), {'location', 'units'})
        self.assertEqual(parameters['required'], ['location', 'units'])

    def test_to_function_dict_with_include_and_exclude(self):
        with self.assertRaises(IntelCriticalError):
            IncludeAndExcludeTool().to_function_dict()

    def test_to_function_dict_without_name_raises(self):
        with self.assertRaises(ToolCriticalError):
            MissingNameTool().to_function_dict()

    def test_default_handle_raises(self):
        with self.assertRaises(ToolCriticalError):
            WeatherTool().handle(arguments='')

    def test_to_tool_instances_mixes_classes_and_instances(self):
        instances = to_tool_instances([WeatherTool, WeatherTool(), NoArgumentsTool])

        self.assertEqual(len(instances), 3)
        self.assertTrue(all(isinstance(tool, BaseTool) for tool in instances))
        self.assertEqual(instances[0].name, 'get_weather')
        self.assertEqual(instances[2].name, 'no_arguments_tool')

    def test_weather_units_required_intel_schema(self):
        parameters = RequiredUnitsWeatherTool().to_function_dict()['function']['parameters']

        self.assertEqual(set(parameters['properties'].keys()), {'location', 'units'})
        self.assertEqual(parameters['required'], ['location', 'units'])


class TestMessageToolWireFormat(TestCase):
    def test_tool_message_dump(self):
        message_history = MessageHistory()

        message_history.add_message(
            role='tool',
            tool_call_id='call_1',
            text='70 degrees',
        )

        dumped_message = message_history[0].model_dump()

        self.assertEqual(dumped_message['role'], 'tool')
        self.assertEqual(dumped_message['content'], '70 degrees')
        self.assertEqual(dumped_message['tool_call_id'], 'call_1')

    def test_assistant_tool_calls_dump(self):
        message = Message(role='assistant')
        message.tool_calls = [
            {
                'id': 'call_1',
                'type': 'function',
                'function': {
                    'name': 'get_weather',
                    'arguments': '{"location": "Paris"}',
                },
            }
        ]

        dumped_message = message.model_dump()

        self.assertEqual(dumped_message['role'], 'assistant')
        self.assertIsNone(dumped_message['content'])
        self.assertEqual(dumped_message['tool_calls'][0]['function']['name'], 'get_weather')

    def test_ordinary_user_message_dump(self):
        message = Message(role='user')
        message.add_content_from_text('Hello world')

        dumped_message = message.model_dump()

        self.assertEqual(dumped_message['role'], 'user')
        self.assertEqual(dumped_message['content'][0]['text'], 'Hello world')
        self.assertNotIn('tool_call_id', dumped_message)
        self.assertNotIn('tool_calls', dumped_message)
