import threading
from dataclasses import dataclass, field

from dandy.shared.cancellation import StopSignal

# The answer a waiting worker sees when the run is stopped while a question is
# on screen (or a stop is requested without one).
STOPPED_ANSWER = 'The user stopped the run. Do not continue the work.'

# How often a blocked ask polls for an externally set stop signal.
STOP_POLL_SECONDS = 0.25


@dataclass
class UserQuestion:
    """One question handed from a worker thread to the UI thread."""

    question: str
    choices: list[str] = field(default_factory=list)


class QuestionGate:
    """A one-slot mailbox that lets a worker thread ask the user a question.

    The worker thread (an agent's tool loop) calls `ask`, which parks the
    question in the gate and blocks until the UI thread calls `deliver` with
    the user's answer. The UI thread sees the parked question through
    `pending`. A `None` delivery means the user declined to answer (for
    example, double-escape at the prompt): the stop signal passed to `ask` is
    set and the worker gets `STOPPED_ANSWER`. While blocked, `ask` also polls
    the stop signal, so a stop requested elsewhere releases the worker even if
    no prompt is ever delivered.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._answered = threading.Event()
        self._pending: UserQuestion | None = None
        self._answer: str | None = None
        self._stop_signal: StopSignal | None = None

    @property
    def pending(self) -> UserQuestion | None:
        with self._lock:
            return self._pending

    def ask(
        self, question: str, choices: list[str] | None = None, stop_signal: StopSignal | None = None
    ) -> str:
        with self._lock:
            self._pending = UserQuestion(question=question, choices=list(choices or []))
            self._answer = None
            self._stop_signal = stop_signal
            self._answered.clear()

        while not self._answered.wait(STOP_POLL_SECONDS):
            if stop_signal is not None and stop_signal.is_set():
                self._clear_pending()
                return STOPPED_ANSWER

        with self._lock:
            answer = self._answer
        self._clear_pending()

        return answer if answer is not None else STOPPED_ANSWER

    def deliver(self, answer: str | None) -> None:
        with self._lock:
            self._pending = None
            self._answer = answer if answer is not None else STOPPED_ANSWER
            if answer is None and self._stop_signal is not None:
                self._stop_signal.set()
            self._answered.set()

    def _clear_pending(self) -> None:
        with self._lock:
            self._pending = None
            self._stop_signal = None


# Module-level singleton, mirroring the `stop_signal` pattern: the CLI's
# render loop and the agent's question tool both import and share this gate.
question_gate = QuestionGate()
