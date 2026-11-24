from unittest import TestCase
from unittest.mock import patch

from dandy.application.agent.compaction import summarize_and_compact_history
from dandy.application.agent.intel import CompactionSummaryIntel
from dandy.domain.message.compaction import replace_middle_with_summary, summarizable_middle_range
from dandy.domain.message.message import Message, MessageHistory
from dandy.shared.exceptions import RunStoppedError


def _long_history(round_count: int = 20) -> MessageHistory:
    history = MessageHistory()
    history.add_message(role='system', text='You are a coding agent.')
    history.add_message(role='user', text='Original request: refactor the module.')

    for index in range(round_count):
        history.add_message(
            role='assistant',
            tool_calls=[
                {
                    'id': f'call_{index}',
                    'type': 'function',
                    'function': {'name': 'read_file', 'arguments': f'{{"path": "f{index}.py"}}'},
                }
            ],
        )
        history.add_message(role='tool', tool_call_id=f'call_{index}', text='x' * 8000)

    history.add_message(role='assistant', text='All done.')

    return history


def _assert_wire_valid(test_case: TestCase, history: MessageHistory) -> None:
    messages = history.messages
    test_case.assertEqual(messages[0].role, 'system')

    index = 0
    while index < len(messages):
        message = messages[index]
        if message.role == 'assistant' and message.tool_calls:
            declared_ids = {tool_call['id'] for tool_call in message.tool_calls}
            result_ids = set()
            index += 1
            while index < len(messages) and messages[index].role == 'tool':
                result_ids.add(messages[index].tool_call_id)
                index += 1
            test_case.assertTrue(declared_ids <= result_ids)
        else:
            index += 1


class TestSummarizableMiddleRange(TestCase):
    def test_head_and_tail_kept_middle_bounded(self) -> None:
        history = _long_history()
        head_end_index, tail_start_index = summarizable_middle_range(history)

        self.assertGreater(head_end_index, 0)
        self.assertGreater(tail_start_index, head_end_index)
        self.assertEqual(history.messages[0].role, 'system')
        self.assertIn(history.messages[tail_start_index].role, ('user', 'assistant'))

    def test_small_history_has_empty_middle(self) -> None:
        history = MessageHistory()
        history.add_message(role='system', text='sys')
        history.add_message(role='user', text='hello')
        history.add_message(role='assistant', text='hi')

        head_end_index, tail_start_index = summarizable_middle_range(history)

        self.assertEqual(head_end_index, tail_start_index)


class TestReplaceMiddleWithSummary(TestCase):
    def test_rebuild_keeps_head_and_tail_and_is_wire_valid(self) -> None:
        history = _long_history()
        head_end_index, tail_start_index = summarizable_middle_range(history)
        head_messages = history.messages[:head_end_index]
        tail_messages = history.messages[tail_start_index:]

        summary_message = Message(role='user', text='[Summary of earlier conversation]')
        replace_middle_with_summary(history, head_end_index, tail_start_index, summary_message)

        self.assertEqual(history.messages[:head_end_index], head_messages)
        self.assertEqual(history.messages[head_end_index], summary_message)
        self.assertEqual(history.messages[head_end_index + 1 :], tail_messages)
        _assert_wire_valid(self, history)


class TestSummarizeAndCompactHistory(TestCase):
    def test_summary_replaces_middle_and_reduces_tokens(self) -> None:
        history = _long_history()
        before_count = history.estimated_token_count
        head_end_index, tail_start_index = summarizable_middle_range(history)
        tail_messages = history.messages[tail_start_index:]

        summary_intel = CompactionSummaryIntel(goal='Refactor the module.', next_step='Run tests.')

        with patch(
            'dandy.application.agent.intelligence.bots.compaction_bot.CompactionBot.process',
            return_value=summary_intel,
        ):
            summarized = summarize_and_compact_history(history, max_context_tokens=100000)

        self.assertTrue(summarized)
        self.assertEqual(history.messages[head_end_index].role, 'user')
        self.assertTrue(
            history.messages[head_end_index].text_content.startswith(
                '[Summary of earlier conversation]'
            )
        )
        self.assertEqual(history.messages[head_end_index + 1 :], tail_messages)
        self.assertLess(history.estimated_token_count, before_count)
        _assert_wire_valid(self, history)

    def test_fallback_to_drop_only_when_summarizer_fails(self) -> None:
        history = _long_history()

        with patch(
            'dandy.application.agent.intelligence.bots.compaction_bot.CompactionBot.process',
            side_effect=RuntimeError('summarizer down'),
        ):
            summarized = summarize_and_compact_history(history, max_context_tokens=20000)

        self.assertFalse(summarized)
        self.assertLessEqual(history.estimated_token_count, 20000 + 3000)
        _assert_wire_valid(self, history)

    def test_empty_middle_returns_false(self) -> None:
        history = MessageHistory()
        history.add_message(role='system', text='sys')
        history.add_message(role='user', text='hello')
        history.add_message(role='assistant', text='hi')

        summarized = summarize_and_compact_history(history, max_context_tokens=100000)

        self.assertFalse(summarized)
        self.assertEqual(len(history), 3)

    def test_user_stop_is_reraised(self) -> None:
        history = _long_history()

        with patch(
            'dandy.application.agent.intelligence.bots.compaction_bot.CompactionBot.process',
            side_effect=RunStoppedError('Run stopped by user.'),
        ):
            with self.assertRaises(RunStoppedError):
                summarize_and_compact_history(history, max_context_tokens=100000)
