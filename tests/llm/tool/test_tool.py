import inspect
from unittest import TestCase

from dandy.llm.request.message import Message, MessageHistory
from dandy.tool.exceptions import ToolCriticalError
from dandy.tool.tool import BaseTool, to_tool_instances

from tests.llm.tool.intelligence.tools import NoParametersTool, RequiredWeatherTool, WeatherTool


class NoHandleTool(BaseTool):
    name = 'no_handle_tool'


class MissingNameTool(BaseTool):
    def handle(self) -> str:
        return ''


class TestBaseTool(TestCase):
    def test_subclass_defines_class_attributes(self):
        tool = WeatherTool()

        self.assertEqual(tool.name, 'get_weather')
        self.assertEqual(tool.description, 'Get the current weather for a location.')

    def test_base_tool_is_abstract(self):
        self.assertTrue(inspect.isabstract(BaseTool))
        self.assertEqual(BaseTool.__abstractmethods__, frozenset({'handle'}))

    def test_cannot_instantiate_without_handle(self):
        with self.assertRaises(TypeError):
            NoHandleTool()

    def test_abstract_handle_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            BaseTool.handle(WeatherTool(), location='Paris')

    def test_to_function_dict_from_handle_signature(self):
        tool_dict = WeatherTool().to_function_dict()

        self.assertEqual(tool_dict['type'], 'function')
        self.assertEqual(tool_dict['function']['name'], 'get_weather')
        self.assertEqual(
            tool_dict['function']['description'], 'Get the current weather for a location.'
        )

        parameters = tool_dict['function']['parameters']

        self.assertEqual(parameters['type'], 'object')
        self.assertEqual(set(parameters['properties'].keys()), {'location', 'units'})
        self.assertEqual(parameters['properties']['location']['type'], 'string')
        self.assertNotIn('required', parameters)

    def test_to_function_dict_without_parameters(self):
        parameters = NoParametersTool().to_function_dict()['function']['parameters']

        self.assertEqual(parameters['type'], 'object')
        self.assertEqual(parameters['properties'], {})

    def test_to_function_dict_with_required_parameter(self):
        parameters = RequiredWeatherTool().to_function_dict()['function']['parameters']

        self.assertEqual(set(parameters['properties'].keys()), {'location', 'units'})
        self.assertEqual(parameters['required'], ['location'])

    def test_to_function_dict_without_name_raises(self):
        with self.assertRaises(ToolCriticalError):
            MissingNameTool().to_function_dict()

    def test_handle_derives_intel_class_from_signature(self):
        tool = WeatherTool()

        parameters_intel_class = tool.get_parameters_intel_class()

        self.assertIsNotNone(parameters_intel_class)

        model = parameters_intel_class.model_validate({'location': 'Paris'})

        self.assertEqual(model.location, 'Paris')
        self.assertEqual(model.units, 'celsius')

    def test_handle_derived_intel_class_is_cached(self):
        tool = WeatherTool()

        parameters_intel_class_a = tool.get_parameters_intel_class()
        parameters_intel_class_b = tool.get_parameters_intel_class()

        self.assertIs(parameters_intel_class_a, parameters_intel_class_b)

    def test_to_tool_instances_mixes_classes_and_instances(self):
        instances = to_tool_instances([WeatherTool, WeatherTool(), RequiredWeatherTool])

        self.assertEqual(len(instances), 3)
        self.assertTrue(all(isinstance(tool, BaseTool) for tool in instances))
        self.assertEqual(instances[0].name, 'get_weather')
        self.assertEqual(instances[2].name, 'get_weather')


class TestMessageToolWireFormat(TestCase):
    def test_tool_message_dump(self):
        message_history = MessageHistory()

        message_history.add_message(role='tool', tool_call_id='call_1', text='70 degrees')

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
                'function': {'name': 'get_weather', 'arguments': '{"location": "Paris"}'},
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
