from unittest import TestCase

from hypothesis import given, settings

from dandy.domain.message.message import MessageHistory, compact_message_history
from tests.domain.message.intelligence.compaction_fuzz_strategies import (
    conversation_history_strategy,
    fuzz_budget_strategy,
)


class TestCompactMessageHistoryFuzz(TestCase):
    @given(history=conversation_history_strategy(), budget=fuzz_budget_strategy())
    @settings(deadline=None)
    def test_system_slot_survives_compaction(self, history: MessageHistory, budget: int) -> None:
        system_message = history.messages[0]

        compact_message_history(history, budget)

        self.assertIs(history.messages[0], system_message)

    @given(history=conversation_history_strategy(), budget=fuzz_budget_strategy())
    @settings(deadline=None)
    def test_compacted_history_is_an_ordered_subsequence_of_the_input(
        self, history: MessageHistory, budget: int
    ) -> None:
        original_messages = list(history.messages)

        compact_message_history(history, budget)

        remaining_originals = iter(original_messages)

        for surviving_message in history.messages:
            for original_message in remaining_originals:
                if original_message is surviving_message:
                    break
            else:
                self.fail('a surviving message is not a member of the original history')

    @given(history=conversation_history_strategy(), budget=fuzz_budget_strategy())
    @settings(deadline=None)
    def test_tool_rounds_survive_atomically(self, history: MessageHistory, budget: int) -> None:
        original_messages = list(history.messages)

        result_indexes_by_declaration_index: dict[int, list[int]] = {}

        for index, message in enumerate(original_messages):
            if message.role != 'assistant' or not message.tool_calls:
                continue
            result_indexes = []
            for following_index in range(index + 1, len(original_messages)):
                if original_messages[following_index].role != 'tool':
                    break
                result_indexes.append(following_index)
            result_indexes_by_declaration_index[index] = result_indexes

        compact_message_history(history, budget)

        surviving_message_ids = {id(message) for message in history.messages}

        for declaration_index, result_indexes in result_indexes_by_declaration_index.items():
            declaration = original_messages[declaration_index]
            if id(declaration) not in surviving_message_ids:
                continue
            for result_index in result_indexes:
                self.assertIn(
                    id(original_messages[result_index]),
                    surviving_message_ids,
                    'a surviving tool-call declaration lost one of its results',
                )

        for position, message in enumerate(history.messages):
            if message.role != 'tool':
                continue
            declaration_messages = [
                earlier_message
                for earlier_message in reversed(history.messages[:position])
                if earlier_message.role == 'assistant' and earlier_message.tool_calls
            ]
            self.assertTrue(declaration_messages, 'a tool result survived without its declaration')
            declaration_call_ids = [call['id'] for call in declaration_messages[0].tool_calls]
            self.assertIn(message.tool_call_id, declaration_call_ids)

    @given(history=conversation_history_strategy(), budget=fuzz_budget_strategy())
    @settings(deadline=None)
    def test_compaction_is_a_fixed_point(self, history: MessageHistory, budget: int) -> None:
        compact_message_history(history, budget)
        first_pass_messages = list(history.messages)

        compact_message_history(history, budget)
        second_pass_messages = list(history.messages)

        self.assertEqual(len(second_pass_messages), len(first_pass_messages))

        for first_pass_message, second_pass_message in zip(
            first_pass_messages, second_pass_messages, strict=True
        ):
            self.assertIs(second_pass_message, first_pass_message)

    @given(history=conversation_history_strategy(), headroom=fuzz_budget_strategy())
    @settings(deadline=None)
    def test_history_that_already_fits_the_budget_is_unchanged(
        self, history: MessageHistory, headroom: int
    ) -> None:
        original_messages = list(history.messages)

        compact_message_history(history, history.estimated_token_count + headroom)

        self.assertEqual(len(history.messages), len(original_messages))

        for original_message, surviving_message in zip(
            original_messages, history.messages, strict=True
        ):
            self.assertIs(surviving_message, original_message)

    @given(history=conversation_history_strategy(), budget=fuzz_budget_strategy())
    @settings(deadline=None)
    def test_result_fits_the_budget_or_is_stuck_at_two_messages(
        self, history: MessageHistory, budget: int
    ) -> None:
        compact_message_history(history, budget)

        self.assertGreaterEqual(len(history.messages), 1)

        if history.estimated_token_count > budget:
            self.assertLessEqual(len(history.messages), 2)
