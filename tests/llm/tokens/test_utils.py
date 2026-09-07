import json
from unittest import TestCase

from dandy.llm.request.message import Message, MessageContent, MessageHistory
from dandy.llm.tokens.utils import (
    TOKEN_COUNT_IMAGE_HIGH_DEFAULT,
    TOKEN_COUNT_IMAGE_LOW,
    TOKEN_COUNT_ROLE_OVERHEAD,
    TOKEN_COUNT_TOOL_CALL_OVERHEAD,
    get_estimated_token_count_for_audio,
    get_estimated_token_count_for_image,
    get_estimated_token_count_for_string,
    get_estimated_token_count_for_tool_calls,
)


class TestStringTokenEstimation(TestCase):
    def test_empty_string_returns_zero(self) -> None:
        self.assertEqual(get_estimated_token_count_for_string(''), 0)

    def test_prose_estimate_is_within_reasonable_range(self) -> None:
        prose = 'The quick brown fox jumps over the lazy dog. ' * 20

        token_count = get_estimated_token_count_for_string(prose)
        character_count = len(prose)

        self.assertGreater(token_count, 0)
        self.assertLess(token_count, character_count / 3)
        self.assertGreater(token_count, character_count / 6)

    def test_symbol_heavy_content_counts_higher_than_prose(self) -> None:
        prose = 'aaaa bbbb cccc dddd eeee ffff'
        symbol_dense = '{"a":{"b":[1,2,3,4,5,6,7,8]}}'

        prose_token_count = get_estimated_token_count_for_string(prose)
        symbol_token_count = get_estimated_token_count_for_string(symbol_dense)

        self.assertGreater(symbol_token_count, prose_token_count)

    def test_code_counts_higher_than_prose_per_character(self) -> None:
        code = "def foo():\n    return {'a': 1, 'b': 2}\n"
        prose = 'the quick brown fox jumps over the lazy dog once more'

        code_count = get_estimated_token_count_for_string(code)
        prose_count = get_estimated_token_count_for_string(prose)

        self.assertGreater(code_count, prose_count)

    def test_json_schema_density_is_estimated(self) -> None:
        json_string = json.dumps(
            {
                'choices': [
                    {
                        'message': {
                            'role': 'assistant',
                            'content': 'hello',
                            'tool_calls': [
                                {
                                    'id': 'call_1',
                                    'type': 'function',
                                    'function': {
                                        'name': 'get_weather',
                                        'arguments': '{"location": "NYC"}',
                                    },
                                }
                            ],
                        }
                    }
                ]
            },
            indent=2,
        )

        self.assertGreater(get_estimated_token_count_for_string(json_string), 0)


class TestContentTypeTokenEstimation(TestCase):
    def test_image_low_has_fixed_cost(self) -> None:
        self.assertEqual(get_estimated_token_count_for_image('low'), TOKEN_COUNT_IMAGE_LOW)

    def test_image_high_and_auto_are_conservative(self) -> None:
        self.assertEqual(
            get_estimated_token_count_for_image('high'), TOKEN_COUNT_IMAGE_HIGH_DEFAULT
        )
        self.assertEqual(
            get_estimated_token_count_for_image('auto'), TOKEN_COUNT_IMAGE_HIGH_DEFAULT
        )
        self.assertGreater(
            get_estimated_token_count_for_image('high'), get_estimated_token_count_for_image('low')
        )

    def test_audio_base64_is_estimated(self) -> None:
        self.assertEqual(get_estimated_token_count_for_audio(''), 0)
        self.assertGreater(get_estimated_token_count_for_audio('QUJDRA==QUJDRA==QUJDRA=='), 0)

    def test_tool_calls_scale_with_call_count(self) -> None:
        single_call = [
            {
                'id': 'call_1',
                'function': {'name': 'get_weather', 'arguments': '{"location": "NYC"}'},
            }
        ]

        double_call = [
            {
                'id': 'call_1',
                'function': {'name': 'get_weather', 'arguments': '{"location": "NYC"}'},
            },
            {'id': 'call_2', 'function': {'name': 'get_time', 'arguments': '{"city": "NYC"}'}},
        ]

        single_count = get_estimated_token_count_for_tool_calls(single_call)
        double_count = get_estimated_token_count_for_tool_calls(double_call)

        self.assertGreaterEqual(single_count, TOKEN_COUNT_TOOL_CALL_OVERHEAD)
        self.assertGreater(double_count, single_count)


class TestMessageTokenEstimation(TestCase):
    def test_text_message_counts_role_overhead_plus_text(self) -> None:
        message = Message(role='user')
        message.add_content_from_text('hello world')

        expected = TOKEN_COUNT_ROLE_OVERHEAD + get_estimated_token_count_for_string('hello world')

        self.assertEqual(message.estimated_token_count, expected)

    def test_tool_call_message_counts_tool_calls(self) -> None:
        tool_calls = [
            {
                'id': 'call_1',
                'type': 'function',
                'function': {'name': 'read_file', 'arguments': '{"path": "a.py"}'},
            }
        ]

        message = Message(role='assistant', tool_calls=tool_calls)

        expected = TOKEN_COUNT_ROLE_OVERHEAD + get_estimated_token_count_for_tool_calls(tool_calls)

        self.assertEqual(message.estimated_token_count, expected)

    def test_image_message_counts_image_and_role_overhead(self) -> None:
        message = Message(role='user')
        message.content.append(
            MessageContent(
                type='image_url', image_url={'url': 'https://example.com/a.png', 'detail': 'low'}
            )
        )

        self.assertEqual(
            message.estimated_token_count, TOKEN_COUNT_ROLE_OVERHEAD + TOKEN_COUNT_IMAGE_LOW
        )

    def test_tool_result_message_counts_tool_call_id(self) -> None:
        message = Message(role='tool', tool_call_id='call_1')
        message.add_content_from_text('file contents here')

        token_count = message.estimated_token_count

        self.assertGreater(token_count, TOKEN_COUNT_ROLE_OVERHEAD)
        self.assertGreater(
            token_count,
            TOKEN_COUNT_ROLE_OVERHEAD + get_estimated_token_count_for_string('file contents here'),
        )

    def test_message_history_sums_message_counts(self) -> None:
        message_history = MessageHistory()
        message_history.add_message(role='user', text='What files are here?')
        message_history.add_message(role='assistant', text='Let me look.')

        expected = sum(message.estimated_token_count for message in message_history.messages)

        self.assertEqual(message_history.estimated_token_count, expected)

    def test_accumulated_agent_history_is_bounded_and_sensible(self) -> None:
        message_history = MessageHistory()
        message_history.add_message(
            role='system', text='You are a coding agent that only responds in raw JSON.'
        )

        for index in range(5):
            message_history.add_message(role='user', text=f'Read file number {index}')
            message_history.add_message(
                role='assistant',
                tool_calls=[
                    {
                        'id': f'call_{index}',
                        'type': 'function',
                        'function': {
                            'name': 'read_file',
                            'arguments': f'{{"path": "a{index}.py"}}',
                        },
                    }
                ],
            )
            message_history.add_message(
                role='tool',
                tool_call_id=f'call_{index}',
                text='print("hello world") print("hello world")' * 10,
            )
            message_history.add_message(role='assistant', text=f'Done reading file {index}.')

        token_count = message_history.estimated_token_count

        self.assertGreater(token_count, 0)
        self.assertLess(token_count, 5000)
