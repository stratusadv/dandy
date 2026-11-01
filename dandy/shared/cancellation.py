import threading


class StopSignal:
    """A thread-safe, set-once stop flag shared across a running task.

    The CLI sets it when the user presses escape twice while a turn is running;
    the agent, tool loop, LLM connector, and subprocess helpers all poll it at
    safe checkpoints and stop the work.
    """

    def __init__(self) -> None:
        self._event = threading.Event()

    def is_set(self) -> bool:
        return self._event.is_set()

    def set(self) -> None:
        self._event.set()

    def clear(self) -> None:
        self._event.clear()


# Module-level singleton, mirroring the `session` singleton pattern. The CLI
# clears it before each turn and sets it on double-escape; every layer that
# needs to react to a stop imports and checks the same instance.
stop_signal = StopSignal()
