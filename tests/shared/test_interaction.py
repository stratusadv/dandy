import threading
import time
from typing import Callable
from unittest import TestCase

from dandy.shared.cancellation import StopSignal
from dandy.shared.interaction import QuestionGate, STOPPED_ANSWER, UserQuestion


class TestQuestionGate(TestCase):
    @staticmethod
    def _wait_until(condition: Callable[[], bool], timeout: float = 2.0) -> None:
        deadline = time.monotonic() + timeout

        while not condition():
            if time.monotonic() > deadline:
                raise AssertionError
            time.sleep(0.01)

    def test_ask_blocks_until_the_ui_delivers_the_answer(self) -> None:
        gate = QuestionGate()
        answers: list[str] = []

        def worker() -> None:
            answers.append(gate.ask('Which color?', ['red', 'blue']))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

        self._wait_until(lambda: gate.pending is not None)
        self.assertIsInstance(gate.pending, UserQuestion)
        self.assertEqual(gate.pending.question, 'Which color?')
        self.assertEqual(gate.pending.choices, ['red', 'blue'])

        gate.deliver('blue')
        thread.join(timeout=2)

        self.assertEqual(answers, ['blue'])
        self.assertIsNone(gate.pending)

    def test_deliver_none_sets_the_stop_signal_and_returns_the_sentinel(self) -> None:
        gate = QuestionGate()
        stop_signal = StopSignal()
        answers: list[str] = []

        def worker() -> None:
            answers.append(gate.ask('Continue?', None, stop_signal))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

        self._wait_until(lambda: gate.pending is not None)

        gate.deliver(None)
        thread.join(timeout=2)

        self.assertEqual(answers, [STOPPED_ANSWER])
        self.assertTrue(stop_signal.is_set())
        self.assertIsNone(gate.pending)

    def test_ask_returns_the_sentinel_when_stop_is_set_without_a_delivery(self) -> None:
        gate = QuestionGate()
        stop_signal = StopSignal()
        answers: list[str] = []

        def worker() -> None:
            answers.append(gate.ask('Continue?', None, stop_signal))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

        self._wait_until(lambda: gate.pending is not None)

        stop_signal.set()
        thread.join(timeout=2)

        self.assertEqual(answers, [STOPPED_ANSWER])
        self.assertIsNone(gate.pending)

    def test_questions_can_be_asked_repeatedly(self) -> None:
        gate = QuestionGate()
        answers: list[str] = []

        def worker() -> None:
            answers.append(gate.ask('First?'))
            answers.append(gate.ask('Second?'))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

        self._wait_until(lambda: gate.pending is not None)
        gate.deliver('yes')

        self._wait_until(lambda: gate.pending is not None and gate.pending.question == 'Second?')
        gate.deliver('no')
        thread.join(timeout=2)

        self.assertEqual(answers, ['yes', 'no'])
        self.assertIsNone(gate.pending)
