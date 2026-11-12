from unittest import TestCase

from dandy.domain.request.exceptions import LlmRecoverableError
from dandy.domain.guard.context_guard import ContextPressureGuard
from dandy.domain.guard.guard import Guard, GuardChain, GuardEvent, GuardOutcome


def _event(
    tool_name: str = 'read_file',
    *,
    arguments: dict | None = None,
    result_text: str = 'ok',
    round_number: int = 1,
    history_token_count: int = 100,
    context_window: int = 65536,
) -> GuardEvent:
    return GuardEvent(
        tool_name=tool_name,
        arguments=arguments if arguments is not None else {'path': 'src/foo.py'},
        result_text=result_text,
        round_number=round_number,
        history_token_count=history_token_count,
        context_window=context_window,
    )


class _PassiveGuard(Guard):
    name = 'passive'

    def __init__(self) -> None:
        super().__init__()
        self.observed = 0

    def observe(self, _event: GuardEvent) -> GuardOutcome:
        self.observed += 1
        return GuardOutcome()


class _NotingGuard(Guard):
    name = 'noting'

    def observe(self, _event: GuardEvent) -> GuardOutcome:
        return GuardOutcome(note='\n\n[Note: be different.]', verbose_line='  - noted')


class _FailingGuard(Guard):
    name = 'failing'

    def observe(self, _event: GuardEvent) -> GuardOutcome:
        return GuardOutcome(failure_message='the failing guard stopped the loop')


class _CompactingGuard(Guard):
    name = 'compacting'

    def on_round_start(self, _history_token_count: int, _context_window: int) -> GuardOutcome:
        return GuardOutcome(compact=True)


class TestGuardChain(TestCase):
    def test_every_guard_sees_every_tool_call(self) -> None:
        passive_guard = _PassiveGuard()
        chain = GuardChain([passive_guard, _PassiveGuard()])

        chain.on_tool_call(_event())

        self.assertEqual(passive_guard.observed, 1)

    def test_steering_notes_append_to_the_result_text(self) -> None:
        chain = GuardChain([_NotingGuard()])

        feedback = chain.on_tool_call(_event(result_text='the result'))

        self.assertEqual(feedback, 'the result\n\n[Note: be different.]')

    def test_verbose_lines_forward_to_the_callback(self) -> None:
        lines = []
        chain = GuardChain([_NotingGuard()])

        chain.on_tool_call(_event(), verbose_callback=lines.append)

        self.assertEqual(lines, ['  - noted'])

    def test_a_failing_guard_stops_the_loop(self) -> None:
        chain = GuardChain([_PassiveGuard(), _FailingGuard()])

        with self.assertRaises(LlmRecoverableError) as context:
            chain.on_tool_call(_event())

        self.assertIn('failing guard', str(context.exception))

    def test_round_start_compaction_request_is_forwarded(self) -> None:
        chain = GuardChain([ContextPressureGuard(), _CompactingGuard()])

        outcome = chain.on_round_start(100, 65536)

        self.assertTrue(outcome.compact)

    def test_round_start_failure_stops_the_loop(self) -> None:
        pressure_guard = ContextPressureGuard()
        pressure_guard.on_round_start(int(65536 * 0.85), 65536)
        chain = GuardChain([pressure_guard])

        with self.assertRaises(LlmRecoverableError) as context:
            chain.on_round_start(65536 + 100, 65536)

        self.assertIn('still exceeds', str(context.exception))
