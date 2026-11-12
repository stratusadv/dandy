from __future__ import annotations

import hashlib
import json

from dandy.shared.hashing import canonicalize
from dandy.domain.guard.guard import Guard, GuardEvent, GuardOutcome

# From the warning threshold on, the tool result fed back to the model carries
# a steering note; at the stop threshold the loop fails fast, so a degenerate
# run costs a bounded number of rounds instead of burning the whole
# tool-iteration cap.
REPEATED_CALL_WARNING_THRESHOLD = 3
REPEATED_CALL_STOP_THRESHOLD = 10

# Steering note appended to the tool result fed back to the model once a
# repeated call crosses the warning threshold. It tells the model that the
# repetition is not producing new information and to change approach or stop.

_SIGNATURE_STEERING_NOTE = (
    '\n\n[Note: you have now run this exact same call '
    '{count} times in this conversation. Running it again will not '
    'change anything. Either change your approach (for example, edit the '
    'code or run a different command) or stop calling tools and give '
    'your final answer.]'
)


def canonical_tool_arguments(kwargs: dict, shallow: bool = False) -> str:
    """Canonical form of validated tool arguments for repeat-call signatures.

    Whitespace runs in every string value fold to a single space and the dict
    dumps as sorted-key compact JSON, so re-typed calls that differ only in
    line wraps, indentation, or key order share one signature. In the shallow
    level, long string values additionally fold to a length plus head and
    tail fingerprint, keeping the signature cheap at volume.
    """
    return json.dumps(canonicalize(kwargs, shallow=shallow), sort_keys=True, separators=(',', ':'))


class RepeatGuard(Guard):
    """Steer a model out of degenerate repeat loops, or fail the loop fast.

    Counts every executed call, per conversation, against a full signature
    (tool name plus a digest of the exact canonical arguments): arguments are
    canonicalized (whitespace runs folded, sorted-key compact JSON), so a
    re-typed call that differs only in line wraps, indentation, or key order
    shares one signature and accumulates, while different arguments are
    different calls that never accumulate against each other no matter how
    often they happen to produce the same result. A model that keeps
    re-running the same call gets a steering note at the warning threshold
    and stops the loop at the stop threshold.
    """

    name = 'repeated call'

    def __init__(
        self,
        warning_threshold: int = REPEATED_CALL_WARNING_THRESHOLD,
        stop_threshold: int = REPEATED_CALL_STOP_THRESHOLD,
    ) -> None:
        super().__init__()
        self.warning_threshold = warning_threshold
        self.stop_threshold = stop_threshold
        self._full_counts: dict[str, int] = {}

    def observe(self, event: GuardEvent) -> GuardOutcome:
        """Count one executed call and return the correction to apply.

        The verdict is unchanged below the warning threshold, carries a
        steering note from the warning threshold on, and fails the loop at
        the stop threshold.
        """
        full_count = self._count_full(event)

        if full_count >= self.stop_threshold:
            message = (
                f'LLM Tool Service stopped the loop: the model repeated the '
                f'identical tool call "{event.tool_name}" {full_count} times '
                'in this conversation. Running it again will not change '
                'anything, so the loop stopped.'
            )
            return GuardOutcome(failure_message=message)

        if full_count >= self.warning_threshold:
            self.record_correction(self._full_signature(event))
            return GuardOutcome(
                note=_SIGNATURE_STEERING_NOTE.format(count=full_count),
                verbose_line=f'  - {event.tool_name} repeated {full_count}x: steering note added',
            )

        return GuardOutcome()

    def _count_full(self, event: GuardEvent) -> int:
        signature = self._full_signature(event)
        count = self._full_counts.get(signature, 0) + 1
        self._full_counts[signature] = count
        return count

    @staticmethod
    def _full_signature(event: GuardEvent) -> str:
        canonical = canonical_tool_arguments(event.arguments)
        digest = hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:32]
        return f'{event.tool_name}::{digest}'
