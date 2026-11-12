from __future__ import annotations

from dandy.domain.message.compaction import COMPACTION_TRIGGER_RATIO
from dandy.domain.guard.guard import Guard, GuardOutcome


class ContextPressureGuard(Guard):
    """Watch the conversation's context pressure and keep the loop on the ground.

    Requests compaction (the loop's course correction) once the conversation's
    estimated token count passes the trigger share of the context window. If
    the pressure re-asserts itself after a compaction was already issued, that
    is an identical failure: the correction could not relieve the pressure.
    When what remains still exceeds the whole window, no valid request can be
    sent, so the guard fails the loop instead of letting the provider reject
    it. Pressure that settles back under the trigger clears the guard.
    """

    name = 'context pressure'

    def __init__(self, trigger_ratio: float = COMPACTION_TRIGGER_RATIO) -> None:
        super().__init__()
        self.trigger_ratio = trigger_ratio
        self._compaction_issued = False

    def on_round_start(self, history_token_count: int, context_window: int) -> GuardOutcome:
        if context_window <= 0:
            return GuardOutcome()

        trigger_token_count = max(1, int(context_window * self.trigger_ratio))

        if history_token_count <= trigger_token_count:
            self._compaction_issued = False
            return GuardOutcome()

        if self._compaction_issued:
            self.record_correction(self.name)

            if history_token_count > context_window:
                message = (
                    f'LLM Tool Service stopped the loop: compaction was '
                    f'requested but the conversation ({history_token_count} '
                    f'tokens) still exceeds the {context_window} token '
                    'context window, so no valid request can be sent. '
                    'Clear the conversation and retry, with a shorter '
                    'request if possible.'
                )
                return GuardOutcome(failure_message=message)

            return GuardOutcome()

        self._compaction_issued = True
        return GuardOutcome(compact=True)
