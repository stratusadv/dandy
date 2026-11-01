import threading
from unittest import TestCase

from dandy.shared.cancellation import StopSignal, stop_signal


class TestStopSignal(TestCase):
    def test_starts_unset(self) -> None:
        signal = StopSignal()

        self.assertFalse(signal.is_set())

    def test_set_marks_the_signal(self) -> None:
        signal = StopSignal()

        signal.set()

        self.assertTrue(signal.is_set())

    def test_clear_resets_the_signal(self) -> None:
        signal = StopSignal()
        signal.set()

        signal.clear()

        self.assertFalse(signal.is_set())

    def test_set_is_visible_from_other_threads(self) -> None:
        signal = StopSignal()
        seen = []

        def worker() -> None:
            signal.set()
            seen.append(signal.is_set())

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()

        self.assertTrue(signal.is_set())
        self.assertEqual(seen, [True])

    def test_module_level_singleton_is_a_stop_signal(self) -> None:
        self.assertIsInstance(stop_signal, StopSignal)
