from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, ClassVar, Sequence

from dandy.domain.request.exceptions import LlmRecoverableError


@dataclass(frozen=True)
class GuardEvent:
    """One observed moment in a tool loop, everything a guard may need.

    Tool call events carry the executed call (name, validated arguments,
    result text, round number) plus the loop's context pressure (the
    conversation's estimated token count against the resolved context
    window), so guards that watch the conversation shape can run off the
    same event stream as guards that watch the calls themselves.
    """

    tool_name: str
    arguments: dict
    result_text: str
    round_number: int
    history_token_count: int
    context_window: int


@dataclass
class GuardOutcome:
    """A guard's verdict on one event.

    ``note`` is a steering text to append to the tool result fed back to the
    model (the live course correction), ``compact`` asks the loop to compact
    the conversation before the next LLM round, ``failure_message`` stops the
    loop (raised by the chain as ``LlmRecoverableError``), and ``verbose_line``
    is an optional debug line for the loop's verbose callback.
    """

    note: str | None = None
    compact: bool = False
    failure_message: str | None = None
    verbose_line: str | None = None


class Guard:
    """A watcher over a tool loop that course-corrects the model's behavior.

    Guards are middleware for the loop: each one observes the same events
    (round starts and executed tool calls) and returns a verdict. A guard
    that sees the same signature trip it again after it already issued a
    correction for that signature counts an identical failure: the
    correction did not change the behavior. Identical failures piling up is
    what fails the loop, so a stuck model costs a bounded number of rounds
    instead of burning the whole tool-iteration cap.

    Subclasses set ``name`` (used in loop error messages) and implement
    ``observe`` and/or ``on_round_start``; a hook that is not implemented
    stays a no-op, so a guard can watch only one kind of event.
    """

    name: ClassVar[str] = 'guard'

    def __init__(self) -> None:
        self._corrections_issued: dict[str, int] = {}

    def observe(self, event: GuardEvent) -> GuardOutcome:  # noqa: ARG002
        """Watch one executed tool call and return the correction to apply."""
        return GuardOutcome()

    def on_round_start(self, history_token_count: int, context_window: int) -> GuardOutcome:  # noqa: ARG002
        """Watch the loop's context pressure at the start of a round."""
        return GuardOutcome()

    def record_correction(self, signature: str) -> int:
        """Count a correction issued for a signature and return the new count.

        A signature that re-trips a guard after a correction was already
        issued for it is an identical failure: the correction did not change
        the behavior, and repeated identical failures are what fail the loop.
        """
        count = self._corrections_issued.get(signature, 0) + 1
        self._corrections_issued[signature] = count
        return count


class GuardChain:
    """Run an ordered set of guards over one tool loop.

    Every guard sees every event; the chain raises ``LlmRecoverableError``
    the moment any guard reports a failure (before the next HTTP call),
    appends every guard's steering notes to the tool result fed back to the
    model, and forwards any guard's compaction request to the loop.
    """

    def __init__(self, guards: Sequence[Guard]) -> None:
        self._guards = list(guards)

    def on_round_start(self, history_token_count: int, context_window: int) -> GuardOutcome:
        """Watch a round start through every guard; returns the combined verdict."""
        outcome = GuardOutcome()

        for guard in self._guards:
            guard_outcome = guard.on_round_start(history_token_count, context_window)

            if guard_outcome.failure_message:
                raise LlmRecoverableError(guard_outcome.failure_message)

            if guard_outcome.compact:
                outcome.compact = True

        return outcome

    def on_tool_call(
        self, event: GuardEvent, verbose_callback: Callable[[str], None] | None = None
    ) -> str:
        """Watch an executed tool call through every guard.

        Returns the result text to feed back to the model with any steering
        notes appended, and raises ``LlmRecoverableError`` when a guard fails
        the loop.
        """
        result_text = event.result_text

        for guard in self._guards:
            guard_outcome = guard.observe(event)

            if guard_outcome.failure_message:
                raise LlmRecoverableError(guard_outcome.failure_message)

            if guard_outcome.verbose_line and verbose_callback is not None:
                verbose_callback(guard_outcome.verbose_line)

            if guard_outcome.note:
                result_text += guard_outcome.note

        return result_text
