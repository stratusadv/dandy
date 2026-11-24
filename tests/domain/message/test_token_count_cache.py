from unittest import TestCase
from unittest.mock import patch

from dandy.domain.message.message import Message, MessageContent, MessageHistory


class TestMessageTokenCountCache(TestCase):
    def test_repeated_access_reuses_cached_count(self) -> None:
        message = Message(role='user')
        message.add_content_from_text('hello world ' * 100)

        first_count = message.estimated_token_count

        with patch(
            'dandy.domain.message.message.get_estimated_token_count_for_string',
            side_effect=AssertionError('token count recomputed on a cache hit'),
        ):
            self.assertEqual(message.estimated_token_count, first_count)

    def test_direct_content_append_invalidates(self) -> None:
        message = Message(role='user')
        message.add_content_from_text('hello')
        before_count = message.estimated_token_count

        message.content.append(MessageContent(type='text', text='more text here'))

        self.assertGreater(message.estimated_token_count, before_count)

    def test_content_reassignment_invalidates(self) -> None:
        message = Message(role='system')
        message.add_content_from_text('original system prompt')
        before_count = message.estimated_token_count

        message.content = [
            MessageContent(type='text', text='a much longer replacement system prompt text')
        ]

        self.assertNotEqual(message.estimated_token_count, before_count)

    def test_in_place_text_edit_invalidates(self) -> None:
        message = Message(role='assistant')
        message.add_content_from_text('hello world')
        before_count = message.estimated_token_count

        message.content[0].text = 'goodbye world, a different length'

        self.assertNotEqual(message.estimated_token_count, before_count)

    def test_tool_calls_assignment_invalidates(self) -> None:
        message = Message(role='assistant')
        before_count = message.estimated_token_count

        message.tool_calls = [
            {
                'id': 'call_1',
                'type': 'function',
                'function': {'name': 'read_file', 'arguments': '{"path": "a.py"}'},
            }
        ]

        self.assertGreater(message.estimated_token_count, before_count)

    def test_cache_is_excluded_from_wire_dump(self) -> None:
        message = Message(role='user')
        message.add_content_from_text('hello')
        self.assertGreater(message.estimated_token_count, 0)

        self.assertNotIn('_token_count_cache', message.model_dump())

    def test_history_total_tracks_appends_and_deletes(self) -> None:
        history = MessageHistory()
        history.add_message(role='system', text='sys')
        history.add_message(role='user', text='hello')
        before_count = history.estimated_token_count

        history.add_message(role='assistant', text='a new reply with some length')
        self.assertGreater(history.estimated_token_count, before_count)

        del history.messages[-1]
        self.assertEqual(history.estimated_token_count, before_count)
