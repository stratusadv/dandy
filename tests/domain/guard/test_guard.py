from unittest import TestCase

from dandy.domain.request.exceptions import LlmExternalError
from dandy.domain.guard.context_guard import ContextPressureGuard
from dandy.domain.guard.guard import Guard, GuardChain, GuardEvent, GuardOutcome
from dandy.domain.intel.typing import IntelType
from dandy.domain.prompt.prompt import Prompt


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


class _TurnStartFailingGuard(Guard):
    name = 'turn-start-failing'

    def on_turn_start(
        self,
        _turn_number: int,
        _message: Prompt | str | None,
        _history_token_count: int,
        _context_window: int,
    ) -> GuardOutcome:
        return GuardOutcome(failure_message='the turn-start guard stopped the turn')


class _TurnEndFailingGuard(Guard):
    name = 'turn-end-failing'

    def on_turn_end(
        self, _turn_number: int, _result: IntelType, _history_token_count: int, _context_window: int
    ) -> GuardOutcome:
        return GuardOutcome(failure_message='the turn-end guard stopped the run')


class _TurnNotingGuard(Guard):
    name = 'turn-noting'

    def __init__(self, note: str = '', verbose_line: str | None = None) -> None:
        super().__init__()
        self.note = note
        self.verbose_line = verbose_line

    def on_turn_end(
        self, _turn_number: int, _result: IntelType, _history_token_count: int, _context_window: int
    ) -> GuardOutcome:
        return GuardOutcome(note=self.note, verbose_line=self.verbose_line)


class _TurnSpyingGuard(Guard):
    name = 'turn-spy'

    def __init__(self) -> None:
        super().__init__()
        self.turn_starts: list[tuple] = []
        self.turn_ends: list[tuple] = []

    def on_turn_start(
        self,
        turn_number: int,
        message: Prompt | str | None,
        history_token_count: int,
        context_window: int,
    ) -> GuardOutcome:
        self.turn_starts.append((turn_number, message, history_token_count, context_window))
        return GuardOutcome()

    def on_turn_end(
        self, turn_number: int, result: IntelType, history_token_count: int, context_window: int
    ) -> GuardOutcome:
        self.turn_ends.append((turn_number, result, history_token_count, context_window))
        return GuardOutcome()


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

        with self.assertRaises(LlmExternalError) as context:
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

        with self.assertRaises(LlmExternalError) as context:
            chain.on_round_start(65536 + 100, 65536)

        self.assertIn('still exceeds', str(context.exception))


class TestGuardTurnEvents(TestCase):
    def test_turn_hooks_are_no_ops_by_default(self) -> None:
        chain = GuardChain([_PassiveGuard()])

        self.assertEqual(chain.on_turn_start(1, 'go', 100, 65536), GuardOutcome())
        self.assertEqual(chain.on_turn_end(1, 'the answer', 200, 65536), GuardOutcome())

    def test_every_guard_sees_the_turn_events(self) -> None:
        spy = _TurnSpyingGuard()
        chain = GuardChain([spy, _TurnSpyingGuard()])

        chain.on_turn_start(1, 'go', 100, 65536)
        chain.on_turn_end(1, 'the answer', 200, 65536)

        self.assertEqual(spy.turn_starts, [(1, 'go', 100, 65536)])
        self.assertEqual(spy.turn_ends, [(1, 'the answer', 200, 65536)])

    def test_turn_start_failure_stops_the_run(self) -> None:
        chain = GuardChain([_PassiveGuard(), _TurnStartFailingGuard()])

        with self.assertRaises(LlmExternalError) as context:
            chain.on_turn_start(1, 'go', 100, 65536)

        self.assertIn('turn-start guard', str(context.exception))

    def test_turn_end_failure_stops_the_run(self) -> None:
        chain = GuardChain([_PassiveGuard(), _TurnEndFailingGuard()])

        with self.assertRaises(LlmExternalError) as context:
            chain.on_turn_end(1, 'the answer', 200, 65536)

        self.assertIn('turn-end guard', str(context.exception))

    def test_turn_end_notes_combine_in_chain_order(self) -> None:
        chain = GuardChain([_TurnNotingGuard('[one]'), _TurnNotingGuard('[two]')])

        outcome = chain.on_turn_end(1, 'the answer', 200, 65536)

        self.assertEqual(outcome.note, '[one][two]')

    def test_turn_verbose_lines_forward_to_the_callback(self) -> None:
        lines = []
        chain = GuardChain([_TurnNotingGuard('[one]', verbose_line='  - turn note')])

        chain.on_turn_end(1, 'the answer', 200, 65536, verbose_callback=lines.append)

        self.assertEqual(lines, ['  - turn note'])

    def test_guard_reset_clears_the_correction_counts(self) -> None:
        guard = _NotingGuard()

        guard.record_correction('signature')
        guard.record_correction('signature')
        guard.reset()

        self.assertEqual(guard.record_correction('signature'), 1)
