from unittest import TestCase

from dandy.domain.guard.guard import GuardEvent
from dandy.domain.guard.repeat_guard import (
    REPEATED_CALL_STOP_THRESHOLD,
    REPEATED_CALL_WARNING_THRESHOLD,
    RepeatGuard,
    canonical_tool_arguments,
)


def _event(arguments: dict, result_text: str = 'ok') -> GuardEvent:
    return GuardEvent(
        tool_name='read_file',
        arguments=arguments,
        result_text=result_text,
        round_number=1,
        history_token_count=100,
        context_window=65536,
    )


class TestCanonicalToolArguments(TestCase):
    def test_whitespace_and_key_order_drift_share_a_signature(self) -> None:
        self.assertEqual(
            canonical_tool_arguments({'a': 'x  y', 'b': 1}),
            canonical_tool_arguments({'b': 1, 'a': 'x y'}),
        )

    def test_shallow_level_folds_long_strings(self) -> None:
        first = {'content': 'A' * 32 + 'x' * 200 + 'Z' * 32}
        second = {'content': 'A' * 32 + 'y' * 200 + 'Z' * 32}

        self.assertEqual(
            canonical_tool_arguments(first, shallow=True),
            canonical_tool_arguments(second, shallow=True),
        )
        self.assertNotEqual(canonical_tool_arguments(first), canonical_tool_arguments(second))


class TestRepeatGuard(TestCase):
    def test_distinct_arguments_never_accumulate_even_with_identical_results(self) -> None:
        guard = RepeatGuard()

        for index in range(REPEATED_CALL_STOP_THRESHOLD + 5):
            outcome = guard.observe(
                _event({'path': f'src/file_{index}.py'}, result_text='same output')
            )
            self.assertIsNone(outcome.note)
            self.assertIsNone(outcome.failure_message)

    def test_results_do_not_affect_the_count(self) -> None:
        guard = RepeatGuard()

        for index in range(REPEATED_CALL_WARNING_THRESHOLD - 1):
            guard.observe(_event({'path': 'src/foo.py'}, result_text=f'output {index}'))

        outcome = guard.observe(
            _event({'path': 'src/foo.py'}, result_text='a totally different output')
        )

        self.assertIn('[Note:', outcome.note)

    def test_identical_call_gets_a_steering_note_at_the_warning_threshold(self) -> None:
        guard = RepeatGuard()
        arguments = {'path': 'src/foo.py'}

        for _ in range(REPEATED_CALL_WARNING_THRESHOLD - 1):
            self.assertIsNone(guard.observe(_event(arguments)).note)

        outcome = guard.observe(_event(arguments))

        self.assertIn('[Note:', outcome.note)
        self.assertIn(f'{REPEATED_CALL_WARNING_THRESHOLD} times', outcome.note)

    def test_persistently_repeated_call_fails_fast(self) -> None:
        guard = RepeatGuard()
        arguments = {'path': 'src/foo.py'}

        for _ in range(REPEATED_CALL_STOP_THRESHOLD - 1):
            self.assertIsNone(guard.observe(_event(arguments)).failure_message)

        outcome = guard.observe(_event(arguments))

        self.assertIn('repeated the identical tool call', outcome.failure_message)
        self.assertIn(f'{REPEATED_CALL_STOP_THRESHOLD} times', outcome.failure_message)

    def test_whitespace_drift_still_accumulates(self) -> None:
        guard = RepeatGuard()

        for whitespace in ['x  y', 'x y', 'x\ty', 'x\ny']:
            outcome = guard.observe(_event({'a': whitespace}))

        self.assertIn('[Note:', outcome.note)

    def test_custom_thresholds(self) -> None:
        guard = RepeatGuard(warning_threshold=2, stop_threshold=4)
        arguments = {'path': 'src/foo.py'}

        self.assertIsNone(guard.observe(_event(arguments)).note)
        self.assertIn('[Note:', guard.observe(_event(arguments)).note)
        self.assertIsNone(guard.observe(_event(arguments)).failure_message)
        outcome = guard.observe(_event(arguments))
        self.assertIn('repeated the identical tool call', outcome.failure_message)
