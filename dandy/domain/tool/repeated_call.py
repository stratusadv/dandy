from __future__ import annotations

import json
from typing import Any, Callable

from dandy.domain.request.exceptions import LlmRecoverableError

# A model that keeps re-observing the same state is not gathering new
# information, so the tool loop guards against it with two counters, both per
# loop and neither consecutive-only. The signature counter counts calls whose
# (name, canonical arguments, result) triple repeats: arguments are
# canonicalized (whitespace runs folded in every string value, sorted-key
# compact JSON) so a model that re-types a call with line-wrap, indent, or
# key-order drift still accumulates toward one signature. The result counter
# counts (name, result) pairs across any argument wording, so a reworded call
# that keeps producing the same output is caught too. A model that oscillates
# between a few near-identical calls accumulates, and a changed result never
# accumulates toward either counter, so legitimately time-varying commands do
# not trip them. From the warning threshold on, the tool result fed back to
# the model carries a steering note; at the stop threshold the loop fails
# fast, so a degenerate run costs a bounded number of rounds instead of
# burning the whole tool-iteration cap.

REPEATED_CALL_WARNING_THRESHOLD = 3
REPEATED_CALL_STOP_THRESHOLD = 10

# Steering notes appended to the tool result fed back to the model once a
# repeated call crosses the warning threshold. They tell the model that the
# repetition is not producing new information and to change approach or stop.

_SIGNATURE_STEERING_NOTE = (
    '\n\n[Note: you have now run this exact same call '
    '{count} times in this conversation and received the '
    'identical result each time. Repeating it again will not change '
    'anything. Either change your approach (for example, edit the '
    'code or run a different command) or stop calling tools and give '
    'your final answer.]'
)

_RESULT_STEERING_NOTE = (
    '\n\n[Note: the tool "{tool_name}" has now returned this '
    'exact same result {count} times in this conversation. '
    'Reading it again will not change anything. Either change your '
    'approach (for example, edit the code or run a different command) '
    'or stop calling tools and give your final answer.]'
)


def canonical_tool_arguments(kwargs: dict) -> str:
    """Canonical form of validated tool arguments for repeat-call signatures.

    Whitespace runs in every string value fold to a single space and the dict
    dumps as sorted-key compact JSON, so re-typed calls that differ only in
    line wraps, indentation, or key order share one signature.
    """

    def _fold(value: Any) -> Any:
        if isinstance(value, str):
            return ' '.join(value.split())
        if isinstance(value, dict):
            return {key: _fold(item) for key, item in value.items()}
        if isinstance(value, list):
            return [_fold(item) for item in value]
        return value

    return json.dumps(_fold(kwargs), sort_keys=True, separators=(',', ':'))


class RepeatedCallGuard:
    """Steer a model out of degenerate repeat loops, or fail the loop fast.

    Counts one call per conversation with two signatures (see the module
    comment). Call :meth:`observe` once per executed tool call; it returns the
    result text to feed back to the model, appends a steering note at the
    warning threshold, and raises :class:`LlmRecoverableError` at the stop
    threshold so a stuck model costs a bounded number of rounds.
    """

    def __init__(
        self,
        warning_threshold: int = REPEATED_CALL_WARNING_THRESHOLD,
        stop_threshold: int = REPEATED_CALL_STOP_THRESHOLD,
    ) -> None:
        self.warning_threshold = warning_threshold
        self.stop_threshold = stop_threshold
        self._signature_counts: dict[tuple[str, str, str], int] = {}
        self._result_counts: dict[tuple[str, str], int] = {}

    def observe(
        self,
        name: str,
        arguments: dict,
        result_text: str,
        verbose_callback: Callable[[str], None] | None = None,
    ) -> str:
        """Count one executed call and return the feedback text for the model.

        The result is returned unchanged below the warning threshold, with a
        steering note appended from the warning threshold on, and
        ``LlmRecoverableError`` is raised at the stop threshold.
        """
        signature_count = self._count_signature(name, arguments, result_text)
        result_count = self._count_result(name, result_text)

        if signature_count >= self.stop_threshold:
            message = (
                f'LLM Tool Service stopped the loop: the model repeated the '
                f'identical tool call "{name}" {signature_count} times in '
                'this conversation and the result never changed.'
            )
            raise LlmRecoverableError(message)

        if result_count >= self.stop_threshold:
            message = (
                f'LLM Tool Service stopped the loop: the tool "{name}" '
                f'returned the identical result {result_count} times in this '
                'conversation, so the model is not gathering new information.'
            )
            raise LlmRecoverableError(message)

        if signature_count >= self.warning_threshold:
            if verbose_callback is not None:
                verbose_callback(f'  - {name} repeated {signature_count}x: steering note added')

            return result_text + _SIGNATURE_STEERING_NOTE.format(count=signature_count)

        if result_count >= self.warning_threshold:
            if verbose_callback is not None:
                verbose_callback(f'  - {name} same result {result_count}x: steering note added')

            return result_text + _RESULT_STEERING_NOTE.format(tool_name=name, count=result_count)

        return result_text

    def _count_signature(self, name: str, arguments: dict, result_text: str) -> int:
        signature = (name, canonical_tool_arguments(arguments), result_text)
        count = int(self._signature_counts.get(signature, 0)) + 1
        self._signature_counts[signature] = count
        return count

    def _count_result(self, name: str, result_text: str) -> int:
        result_key = (name, result_text)
        count = int(self._result_counts.get(result_key, 0)) + 1
        self._result_counts[result_key] = count
        return count
