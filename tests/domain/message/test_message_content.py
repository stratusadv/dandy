import base64
from pathlib import Path
from unittest import TestCase

from dandy.domain.message.message import (
    ImageUrl,
    InputAudio,
    Message,
    MessageContent,
    MessageHistory,
    compact_message_history,
)
from dandy.domain.tokens.estimate import (
    TOKEN_COUNT_ROLE_OVERHEAD,
    TOKEN_COUNT_TOOL_CALL_ID_OVERHEAD,
    get_estimated_token_count_for_image,
    get_estimated_token_count_for_string,
)

TESTS_ASSETS_PATH = Path(__file__).resolve().parents[2] / 'assets'
IMAGE_FILE_PATH = TESTS_ASSETS_PATH / 'images' / 'vision_test_people_and_animal.jpg'
AUDIO_FILE_PATH = TESTS_ASSETS_PATH / 'audio' / 'recording.mp3'

OGG_BASE64_STRING = 'T2dnUwAAAAAAAAAKAAAAAAAAAAA='


class TestMessageContent(TestCase):
    def test_as_str_returns_text(self) -> None:
        self.assertEqual(MessageContent(type='text', text='hello').as_str(), 'hello')

    def test_as_str_returns_image_url_repr(self) -> None:
        content = MessageContent(
            type='image_url', image_url=ImageUrl(url='https://example.com/a.jpg')
        )

        self.assertEqual(content.as_str(), str(ImageUrl(url='https://example.com/a.jpg')))

    def test_as_str_returns_audio_data_url(self) -> None:
        content = MessageContent(
            type='input_audio', input_audio=InputAudio(data='abc123', format='mp3')
        )

        self.assertEqual(content.as_str(), 'data:audio/mp3;base64,abc123')

    def test_as_str_falls_back_to_repr(self) -> None:
        content = MessageContent(type='text')

        self.assertEqual(content.as_str(), str(content))


class TestMessage(TestCase):
    def test_text_content_joins_all_text_parts(self) -> None:
        message = Message(role='user')
        message.add_content_from_text('a ')
        message.add_content_from_text('b')

        self.assertEqual(message.text_content, 'a b')

    def test_estimated_token_count_includes_string_tokens(self) -> None:
        message = Message(role='user')
        message.add_content_from_text('hello world')

        self.assertEqual(
            message.estimated_token_count,
            TOKEN_COUNT_ROLE_OVERHEAD + get_estimated_token_count_for_string('hello world'),
        )

    def test_estimated_token_count_includes_image_tokens_by_detail(self) -> None:
        message = Message(role='user')
        message.add_content_from_image_url('https://example.com/a.jpg')

        self.assertEqual(
            message.estimated_token_count,
            TOKEN_COUNT_ROLE_OVERHEAD + get_estimated_token_count_for_image('auto'),
        )

    def test_estimated_token_count_includes_audio_tokens(self) -> None:
        message = Message(role='user')
        message.add_content_from_input_audio_base64_string(OGG_BASE64_STRING)

        self.assertGreater(message.estimated_token_count, TOKEN_COUNT_ROLE_OVERHEAD)

    def test_estimated_token_count_includes_tool_call_id(self) -> None:
        message = Message(role='tool', tool_call_id='call_abc')
        message.add_content_from_text('result')

        expected = (
            TOKEN_COUNT_ROLE_OVERHEAD
            + TOKEN_COUNT_TOOL_CALL_ID_OVERHEAD
            + get_estimated_token_count_for_string('call_abc')
            + get_estimated_token_count_for_string('result')
        )

        self.assertEqual(message.estimated_token_count, expected)

    def test_add_content_from_image_file_path(self) -> None:
        message = Message(role='user')
        message.add_content_from_image_file_path(IMAGE_FILE_PATH)

        expected_base64 = base64.b64encode(IMAGE_FILE_PATH.read_bytes()).decode('utf-8')
        image_url = message.content[0].image_url.url
        self.assertTrue(image_url.startswith('data:image/jpg;base64,'))
        self.assertEqual(image_url, f'data:image/jpg;base64,{expected_base64}')

    def test_add_content_from_image_base64_string(self) -> None:
        message = Message(role='user')
        message.add_content_from_image_base64_string('/9j/4AAQSkZJRg')

        self.assertEqual(message.content[0].image_url.url, 'data:image/jpg;base64,/9j/4AAQSkZJRg')

    def test_add_content_from_input_audio_url(self) -> None:
        message = Message(role='user')
        message.add_content_from_input_audio_url('https://example.com/song.mp3')

        self.assertEqual(message.content[0].input_audio.data, 'https://example.com/song.mp3')
        self.assertEqual(message.content[0].input_audio.format, 'mp3')

    def test_add_content_from_input_audio_file_path(self) -> None:
        message = Message(role='user')
        message.add_content_from_input_audio_file_path(AUDIO_FILE_PATH)

        expected_base64 = base64.b64encode(AUDIO_FILE_PATH.read_bytes()).decode('utf-8')
        self.assertEqual(message.content[0].input_audio.data, expected_base64)
        self.assertIn(message.content[0].input_audio.format, ('mp3', 'ogg', 'wav', 'mp4'))

    def test_add_content_from_input_audio_base64_string(self) -> None:
        message = Message(role='user')
        message.add_content_from_input_audio_base64_string(OGG_BASE64_STRING)

        self.assertEqual(message.content[0].input_audio.data, OGG_BASE64_STRING)
        self.assertEqual(message.content[0].input_audio.format, 'ogg')

    def test_model_dump_for_tool_message_uses_string_content(self) -> None:
        message = Message(role='tool', tool_call_id='call_1')
        message.add_content_from_text('70 degrees')

        self.assertEqual(message.model_dump()['content'], '70 degrees')

    def test_model_dump_for_assistant_tool_calls_sets_content_none(self) -> None:
        message = Message(
            role='assistant',
            tool_calls=[{'id': 'call_1', 'function': {'name': 'get_weather', 'arguments': '{}'}}],
        )
        message.add_content_from_text('narration')

        dumped = message.model_dump()
        self.assertIsNone(dumped['content'])
        self.assertEqual(dumped['tool_calls'][0]['function']['name'], 'get_weather')


class TestMessageHistory(TestCase):
    def test_len_getitem_iter_setitem(self) -> None:
        history = MessageHistory()
        history.add_message(role='system', text='s')
        history.add_message(role='user', text='u')

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].role, 'system')
        self.assertEqual([message.role for message in history], ['system', 'user'])

        replacement = Message(role='assistant')
        history[1] = replacement
        self.assertIs(history[1], replacement)

    def test_is_falsy_when_empty(self) -> None:
        self.assertFalse(MessageHistory())
        history = MessageHistory()
        history.add_message(role='user', text='x')
        self.assertTrue(history)

    def test_has_system_message_only_when_first(self) -> None:
        history = MessageHistory()
        self.assertFalse(history.has_system_message)

        history.add_message(role='user', text='u')
        self.assertFalse(history.has_system_message)

        history.prepend(Message(role='system'))
        self.assertTrue(history.has_system_message)

    def test_add_message_appends_multimodal_content(self) -> None:
        history = MessageHistory()
        history.add_message(
            role='user',
            text='look at these',
            image_urls=['https://example.com/a.jpg'],
            image_base64_strings=['/9j/4AAQSkZJRg'],
            audio_urls=['https://example.com/song.mp3'],
            audio_base64_strings=[OGG_BASE64_STRING],
        )

        message = history[0]
        types = [content.type for content in message.content]
        self.assertEqual(types, ['text', 'image_url', 'image_url', 'input_audio', 'input_audio'])

    def test_add_message_prepend(self) -> None:
        history = MessageHistory()
        history.add_message(role='user', text='u')
        history.add_message(role='system', text='s', prepend=True)

        self.assertEqual([message.role for message in history], ['system', 'user'])

    def test_extend(self) -> None:
        history = MessageHistory()
        history.extend([Message(role='user'), Message(role='assistant')])

        self.assertEqual([message.role for message in history], ['user', 'assistant'])

    def test_estimated_token_count_sums_messages(self) -> None:
        history = MessageHistory()
        history.add_message(role='system', text='s')
        history.add_message(role='user', text='u')

        expected = sum(message.estimated_token_count for message in history)
        self.assertEqual(history.estimated_token_count, expected)


class TestCompactMessageHistory(TestCase):
    def build_history(self, text: str = 'a' * 1000) -> MessageHistory:
        history = MessageHistory()
        history.add_message(role='system', text='system')
        history.add_message(role='user', text=text)
        history.add_message(
            role='assistant',
            tool_calls=[{'id': 'call_1', 'function': {'name': 't', 'arguments': '{}'}}],
        )
        history.add_message(role='tool', tool_call_id='call_1', text=text)
        history.add_message(role='assistant', text=text)
        return history

    def test_within_budget_is_untouched(self) -> None:
        history = self.build_history()
        original_count = len(history)

        compact_message_history(history, max_context_tokens=1_000_000)

        self.assertEqual(len(history), original_count)

    def test_drops_tool_round_first_then_oldest_exchange(self) -> None:
        history = self.build_history()

        compact_message_history(history, max_context_tokens=100)

        roles = [message.role for message in history]
        self.assertEqual(roles, ['system', 'assistant'])

    def test_keeps_system_and_newest_when_nothing_else_droppable(self) -> None:
        history = MessageHistory()
        history.add_message(role='system', text='system')
        history.add_message(role='user', text='a' * 1000)

        compact_message_history(history, max_context_tokens=100)

        self.assertEqual([message.role for message in history], ['system', 'user'])

    def test_single_message_history_is_untouched(self) -> None:
        history = MessageHistory()
        history.add_message(role='user', text='a' * 1000)

        compact_message_history(history, max_context_tokens=100)

        self.assertEqual(len(history), 1)

    def test_never_dangles_tool_results_without_their_tool_calls(self) -> None:
        history = MessageHistory()
        history.add_message(role='system', text='system')
        history.add_message(
            role='assistant',
            tool_calls=[{'id': 'call_1', 'function': {'name': 't', 'arguments': '{}'}}],
        )
        history.add_message(role='tool', tool_call_id='call_1', text='a' * 1000)
        history.add_message(role='user', text='a' * 1000)

        compact_message_history(history, max_context_tokens=100)

        roles = [message.role for message in history]
        for index, role in enumerate(roles):
            if role == 'tool':
                self.assertEqual(roles[index - 1], 'assistant')
