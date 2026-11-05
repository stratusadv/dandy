from unittest import TestCase

from dandy.application.bot.bot import Bot
from dandy.domain.intel.intel import BaseIntel
from dandy.domain.message.message import Message, MessageHistory
from dandy.domain.message.compaction import drop_incomplete_tool_round
from tests.consts import live_llm_test


class TestMessageWireShape(TestCase):
    def test_tool_message_accepts_string_content(self) -> None:
        message = Message.model_validate(
            {'role': 'tool', 'tool_call_id': 'call_1', 'content': 'Sunny and 80.'}
        )

        self.assertEqual(message.text_content, 'Sunny and 80.')
        self.assertEqual(message.tool_call_id, 'call_1')

    def test_tool_call_message_accepts_missing_content(self) -> None:
        message = Message.model_validate(
            {
                'role': 'assistant',
                'tool_calls': [
                    {
                        'id': 'call_1',
                        'type': 'function',
                        'function': {'name': 'get_weather', 'arguments': '{}'},
                    }
                ],
            }
        )

        self.assertEqual(message.text_content, '')
        self.assertEqual(message.tool_calls[0]['function']['name'], 'get_weather')

    def test_wire_round_trip_preserves_messages(self) -> None:
        history = MessageHistory()
        history.add_message(role='system', text='You are helpful.')
        history.add_message(role='user', text='What is the weather in Austin?')
        history.add_message(
            role='assistant',
            tool_calls=[
                {
                    'id': 'call_1',
                    'type': 'function',
                    'function': {'name': 'get_weather', 'arguments': '{"location": "Austin"}'},
                }
            ],
        )
        history.add_message(role='tool', tool_call_id='call_1', text='Sunny and 80.')

        dumped_messages = [message.model_dump() for message in history.messages]
        restored_messages = [Message.model_validate(dumped) for dumped in dumped_messages]

        for original, restored in zip(history.messages, restored_messages, strict=True):
            self.assertEqual(original.text_content, restored.text_content)

        self.assertEqual(restored_messages[2].tool_calls, history.messages[2].tool_calls)
        self.assertEqual(restored_messages[3].tool_call_id, 'call_1')


class TestDropIncompleteToolRound(TestCase):
    @staticmethod
    def _tool_call(call_id: str, function_name: str = 'get_weather') -> dict:
        return {
            'id': call_id,
            'type': 'function',
            'function': {'name': function_name, 'arguments': '{}'},
        }

    def _history_with_opening_exchange(self) -> MessageHistory:
        history = MessageHistory()
        history.add_message(role='system', text='You are helpful.')
        history.add_message(role='user', text='What is the weather in Austin?')
        return history

    def test_dangling_declaration_is_dropped(self) -> None:
        history = self._history_with_opening_exchange()
        history.add_message(role='assistant', tool_calls=[self._tool_call('call_1')])

        drop_incomplete_tool_round(history)

        self.assertEqual(len(history.messages), 2)
        self.assertEqual(history.messages[-1].role, 'user')

    def test_partial_round_is_dropped(self) -> None:
        history = self._history_with_opening_exchange()
        history.add_message(
            role='assistant', tool_calls=[self._tool_call('call_1'), self._tool_call('call_2')]
        )
        history.add_message(role='tool', tool_call_id='call_1', text='Sunny and 80.')

        drop_incomplete_tool_round(history)

        self.assertEqual(len(history.messages), 2)
        self.assertEqual(history.messages[-1].role, 'user')

    def test_complete_round_is_kept(self) -> None:
        history = self._history_with_opening_exchange()
        history.add_message(role='assistant', tool_calls=[self._tool_call('call_1')])
        history.add_message(role='tool', tool_call_id='call_1', text='Sunny and 80.')

        drop_incomplete_tool_round(history)

        self.assertEqual(len(history.messages), 4)
        self.assertEqual(history.messages[-1].role, 'tool')

    def test_earlier_complete_rounds_are_untouched(self) -> None:
        history = self._history_with_opening_exchange()
        history.add_message(role='assistant', tool_calls=[self._tool_call('call_1')])
        history.add_message(role='tool', tool_call_id='call_1', text='Sunny and 80.')
        history.add_message(role='user', text='And in Houston?')
        history.add_message(
            role='assistant', tool_calls=[self._tool_call('call_2'), self._tool_call('call_3')]
        )
        history.add_message(role='tool', tool_call_id='call_2', text='Hot and 95.')

        drop_incomplete_tool_round(history)

        self.assertEqual(len(history.messages), 5)
        self.assertEqual(history.messages[-1].role, 'user')

    def test_trailing_assistant_answer_is_untouched(self) -> None:
        history = self._history_with_opening_exchange()
        history.add_message(role='assistant', text='It is sunny in Austin.')

        drop_incomplete_tool_round(history)

        self.assertEqual(len(history.messages), 3)
        self.assertEqual(history.messages[-1].role, 'assistant')

    def test_trailing_user_message_is_untouched(self) -> None:
        history = self._history_with_opening_exchange()
        history.add_message(role='assistant', text='It is sunny in Austin.')
        history.add_message(role='user', text='Thanks!')

        drop_incomplete_tool_round(history)

        self.assertEqual(len(history.messages), 4)
        self.assertEqual(history.messages[-1].role, 'user')

    def test_empty_history_is_a_noop(self) -> None:
        history = MessageHistory()

        drop_incomplete_tool_round(history)

        self.assertEqual(len(history.messages), 0)


class TestMessages(TestCase):
    @live_llm_test
    def test_message_history(self):
        message_history = MessageHistory()
        message_history.add_message(
            role='system',
            text='You are chatting about a birthday. Ask when it is, then how old they are now, then react with surprise.',
        )
        message_history.add_message(role='user', text='I was 91 years old a few days ago')
        message_history.add_message(role='user', text='It is my birthday today!')
        message_history.add_message(role='user', text='I just turned 92')
        message_history.add_message(role='user', text='That is ok I am feeling great')

        class BirthdayIntel(BaseIntel):
            past_age: int
            current_age: int

        birthday_intel = Bot().llm.prompt_to_intel(
            prompt='What were my ages in our conversation',
            intel_class=BirthdayIntel,
            message_history=message_history,
        )

        self.assertEqual(birthday_intel.past_age, 91)
        self.assertEqual(birthday_intel.current_age, 92)
