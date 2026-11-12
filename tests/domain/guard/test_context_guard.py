from unittest import TestCase

from dandy.domain.guard.context_guard import ContextPressureGuard


class TestContextPressureGuard(TestCase):
    def test_under_the_trigger_does_nothing(self) -> None:
        guard = ContextPressureGuard()

        outcome = guard.on_round_start(1000, 65536)

        self.assertFalse(outcome.compact)
        self.assertIsNone(outcome.failure_message)

    def test_over_the_trigger_requests_compaction(self) -> None:
        guard = ContextPressureGuard()

        outcome = guard.on_round_start(int(65536 * 0.85), 65536)

        self.assertTrue(outcome.compact)
        self.assertIsNone(outcome.failure_message)

    def test_pressure_after_compaction_under_the_window_does_not_refire(self) -> None:
        guard = ContextPressureGuard()
        pressured = int(65536 * 0.85)

        guard.on_round_start(pressured, 65536)
        outcome = guard.on_round_start(pressured, 65536)

        self.assertFalse(outcome.compact)
        self.assertIsNone(outcome.failure_message)

    def test_pressure_still_over_the_window_after_compaction_fails(self) -> None:
        guard = ContextPressureGuard()

        guard.on_round_start(int(65536 * 0.85), 65536)
        outcome = guard.on_round_start(65536 + 100, 65536)

        self.assertFalse(outcome.compact)
        self.assertIn('still exceeds', outcome.failure_message)

    def test_pressure_settling_clears_the_guard(self) -> None:
        guard = ContextPressureGuard()

        guard.on_round_start(int(65536 * 0.85), 65536)
        guard.on_round_start(int(65536 * 0.5), 65536)
        outcome = guard.on_round_start(int(65536 * 0.85), 65536)

        self.assertTrue(outcome.compact)
        self.assertIsNone(outcome.failure_message)
