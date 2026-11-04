from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Callable

from pydantic import ValidationError

from dandy.shared.cancellation import stop_signal
from dandy.shared.exceptions import RunStoppedError
from dandy.shared.service.service import BaseService
from dandy.shared.utils import pascal_to_title_case, pydantic_validation_error_to_str
from dandy.domain.intel.factory import IntelFactory
from dandy.domain.request.exceptions import LlmCriticalError, LlmRecoverableError
from dandy.domain.message.message import compact_message_history
from dandy.domain.tool.beat import StoryBeat
from dandy.domain.tool.intel import ToolCallIntel, ToolCallsIntel
from dandy.infrastructure.recorder.tool_events import recorder_add_tool_result_event
from dandy.domain.tool.tool import BaseTool, ToolType, ToolHandler, to_tool_instances

if TYPE_CHECKING:
    from dandy.application.skill.service import SkillService
    from dandy.domain.intel.typing import IntelType
    from dandy.domain.prompt.prompt import Prompt

# Compaction in the tool loop keeps the accumulated conversation to this share
# of the model's context window, matching the agent's compaction target in
# dandy/cli/intelligence/coding_agent.py (0.70), so a long tool-calling session
# never overflows the provider's context window. The fallback window mirrors
# AGENT_MAX_CONTEXT_TOKENS_DEFAULT for configs without a CONTEXT_SIZE.

TOOL_LOOP_CONTEXT_DEFAULT = 65536
TOOL_LOOP_COMPACTION_TARGET_RATIO = 0.70

# Compaction triggers at this higher share of the window and compacts back
# down to the target, so a loop whose rounds keep re-adding about what
# compaction just dropped does not re-compact on every round; the band
# between trigger and target is the headroom a long loop may use.
TOOL_LOOP_COMPACTION_TRIGGER_RATIO = 0.80

# A model that keeps re-observing the same state is not gathering new
# information, and the loop guards against it with two counters, both per
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

# Tool results are capped before they enter the conversation so one oversized
# result (a huge file read, a chatty user tool) can never blow past the model's
# context window or be silently dropped whole by compaction. The cap mirrors
# the 8000-character limits on the built-in agent tools.

_TOOL_RESULT_CHARACTER_LIMIT = 8000


def _tool_preview(text: str, limit: int = 240) -> str:
    """One-line preview of tool arguments or results for verbose tracing."""
    text = text.replace('\n', '\\n')
    return f'{text[:limit]}{"..." if len(text) > limit else ""}'


def _canonical_arguments(kwargs: dict) -> str:
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


class ToolService(BaseService['dandy.application.tool.mixin.ToolServiceMixin']):
    def prompt_to_intel(
        self,
        prompt: Prompt | str | None = None,
        intel_class: type[IntelType] | None = None,
        intel_object: IntelType | None = None,
        tools: list[ToolType] | None = None,
        tool_functions: dict[str, ToolHandler] | None = None,
        max_tool_iterations: int | None = 5,
        progress_callback: Callable[[StoryBeat], None] | None = None,
        verbose_callback: Callable[[str], None] | None = None,
        tool_call_callback: Callable[[str, dict[str, object]], None] | None = None,
        **kwargs,
    ) -> IntelType:
        skill_service = self.obj.skills
        user_tools = to_tool_instances(tools)
        self._validate_no_tool_name_collision(user_tools, skill_service)
        tool_functions = tool_functions or {}

        iteration_count = 0
        repeated_call_tracker: dict[tuple[str, str, str], int] = {}
        repeated_result_tracker: dict[tuple[str, str], int] = {}

        while True:
            if stop_signal.is_set():
                raise RunStoppedError('Run stopped by user.')

            self._compact_history_before_next_round(progress_callback=progress_callback)

            skill_tools = skill_service.active_tools()
            round_tools = user_tools + skill_tools
            tools_by_name = {tool.name: tool for tool in round_tools}

            intel = self.obj.prompt_to_intel(
                prompt=prompt if iteration_count == 0 else None,
                intel_class=intel_class,
                intel_object=intel_object,
                tools=round_tools if (tools is not None or skill_tools) else None,
                **kwargs,
            )

            if not isinstance(intel, ToolCallsIntel):
                if verbose_callback is not None:
                    verbose_callback(
                        f'Round {iteration_count + 1}: model returned a final response'
                    )
                return intel

            if max_tool_iterations is not None and iteration_count >= max_tool_iterations:
                if verbose_callback is not None:
                    verbose_callback(
                        f'GAVE UP: reached {max_tool_iterations} tool iterations '
                        f'without a final response'
                    )
                message = (
                    f'LLM Tool Service gave up after {max_tool_iterations} tool '
                    f'iterations without a final response.'
                )
                raise LlmRecoverableError(message)

            round_number = iteration_count + 1

            if verbose_callback is not None:
                verbose_callback(f'Round {round_number}: model requested {len(intel)} tool call(s)')

            if intel.summary and progress_callback is not None:
                progress_callback(StoryBeat(description=intel.summary, kind='narration'))

            for tool_call in intel:
                if stop_signal.is_set():
                    raise RunStoppedError('Run stopped by user.')

                if verbose_callback is not None:
                    verbose_callback(
                        f'  - {tool_call.name} args: {_tool_preview(tool_call.arguments)}'
                    )

                self._process_tool_call(
                    tool_call=tool_call,
                    tools_by_name=tools_by_name,
                    tool_functions=tool_functions,
                    progress_callback=progress_callback,
                    verbose_callback=verbose_callback,
                    tool_call_callback=tool_call_callback,
                    repeated_call_tracker=repeated_call_tracker,
                    repeated_result_tracker=repeated_result_tracker,
                )

            iteration_count += 1

    @staticmethod
    def _validate_no_tool_name_collision(
        user_tools: list[BaseTool], skill_service: SkillService
    ) -> None:
        colliding = sorted({tool.name for tool in user_tools} & skill_service.all_tool_names())

        if colliding:
            message = (
                f'The tool name(s) {colliding} collide with skill tool names; '
                f'rename the tool or the skill method.'
            )
            raise LlmCriticalError(message)

    def _compact_history_before_next_round(
        self, progress_callback: Callable[[StoryBeat], None] | None = None
    ) -> None:
        """Trim the accumulated conversation before the next LLM round.

        Long-running tool loops append a tool-call request plus its results per
        round, which can overflow the provider's context window when the loop is
        unbounded. Uses the resolved config's ``CONTEXT_SIZE`` (a default window
        when unset) and compacts to a fraction of it, keeping the system message
        and the newest exchange. Compaction only triggers once the estimate
        passes the higher trigger ratio, so a steady state where each round
        re-adds about what compaction just dropped does not compact every round.
        """
        context_size = getattr(self.obj.config, 'context_size', 0) or TOOL_LOOP_CONTEXT_DEFAULT
        target_token_count = max(1, int(context_size * TOOL_LOOP_COMPACTION_TARGET_RATIO))
        trigger_token_count = max(
            target_token_count + 1, int(context_size * TOOL_LOOP_COMPACTION_TRIGGER_RATIO)
        )

        current_token_count = self.obj.messages.estimated_token_count

        if current_token_count <= trigger_token_count:
            return

        if progress_callback is not None:
            description = f'Compacting conversation history ({current_token_count} tokens)...'
            progress_callback(StoryBeat(description=description))

        compact_message_history(history=self.obj.messages, max_context_tokens=target_token_count)

    def _process_tool_call(
        self,
        tool_call: ToolCallIntel,
        tools_by_name: dict[str, BaseTool],
        tool_functions: dict[str, ToolHandler],
        *,
        progress_callback: Callable[[StoryBeat], None] | None = None,
        verbose_callback: Callable[[str], None] | None = None,
        tool_call_callback: Callable[[str, dict[str, object]], None] | None = None,
        repeated_call_tracker: dict[tuple[str, str, str], int] | None = None,
        repeated_result_tracker: dict[tuple[str, str], int] | None = None,
    ) -> None:
        tool = tools_by_name.get(tool_call.name)

        if tool is None:
            message = f'No BaseTool with the name "{tool_call.name}" was provided.'
            raise LlmCriticalError(message)

        tool_function = tool_functions.get(tool_call.name)

        parameters_intel_class = tool.get_parameters_intel_class()

        try:
            arguments_intel = IntelFactory.json_str_to_intel_object(
                json_str=tool_call.arguments.strip() or '{}', intel=parameters_intel_class
            )
        except ValidationError as error:
            if verbose_callback is not None:
                verbose_callback(
                    f'  - {tool_call.name} args INVALID: '
                    f'{pydantic_validation_error_to_str(error)} (fed back to model)'
                )
            self.obj.messages.add_message(
                role='tool',
                tool_call_id=tool_call.id,
                text=(
                    f'Tool "{tool_call.name}" received arguments that could not '
                    f'be validated: {pydantic_validation_error_to_str(error)}'
                ),
            )
            return

        arguments_kwargs = arguments_intel.model_dump()

        if progress_callback is not None:
            label = tool.action_label or pascal_to_title_case(tool_call.name)
            description = tool.action_output(**arguments_kwargs) or ''
            progress_callback(
                StoryBeat(
                    label=label,
                    description=description,
                    ascii_char=tool.action_ascii_char,
                    can_mutate_state=tool.can_mutate_state,
                )
            )

        if tool_function is None:
            result = tool.handle(**arguments_kwargs)
        else:
            result = tool_function(arguments_intel)

        if tool_call_callback is not None:
            tool_call_callback(tool_call.name, arguments_kwargs)

        result_text = result if isinstance(result, str) else result.model_dump_json()

        if len(result_text) > _TOOL_RESULT_CHARACTER_LIMIT:
            result_text = result_text[:_TOOL_RESULT_CHARACTER_LIMIT] + '\n... (truncated)'

        if verbose_callback is not None:
            verbose_callback(f'  - {tool_call.name} result: {_tool_preview(result_text)}')

        recorder_add_tool_result_event(
            tool_name=tool_call.name, result=result_text, event_id=self.recorder_event_id
        )

        feedback_text = self._guard_repeated_call(
            tool_call=tool_call,
            arguments_kwargs=arguments_kwargs,
            result_text=result_text,
            tracker=repeated_call_tracker,
            result_tracker=repeated_result_tracker,
            verbose_callback=verbose_callback,
        )

        self.obj.messages.add_message(role='tool', tool_call_id=tool_call.id, text=feedback_text)

    def _guard_repeated_call(
        self,
        tool_call: ToolCallIntel,
        arguments_kwargs: dict,
        result_text: str,
        tracker: dict[tuple[str, str, str], int] | None = None,
        result_tracker: dict[tuple[str, str], int] | None = None,
        verbose_callback: Callable[[str], None] | None = None,
    ) -> str:
        """Break up degenerate repeat loops by steering or failing fast.

        Two counters, both per loop and neither consecutive-only: the signature
        counter counts (name, canonical arguments, result) triples, so re-typed
        calls with line-wrap, indent, or key-order drift still accumulate, and
        the result counter counts (name, result) pairs across any argument
        wording, so a reworded call that keeps producing the same output is
        caught too. A changed result never accumulates toward either, so
        legitimately time-varying commands do not trip them.
        """
        if tracker is None and result_tracker is None:
            return result_text

        signature_count = 0
        result_count = 0

        if tracker is not None:
            signature = (tool_call.name, _canonical_arguments(arguments_kwargs), result_text)
            signature_count = int(tracker.get(signature, 0)) + 1
            tracker[signature] = signature_count

        if result_tracker is not None:
            result_key = (tool_call.name, result_text)
            result_count = int(result_tracker.get(result_key, 0)) + 1
            result_tracker[result_key] = result_count

        if signature_count >= REPEATED_CALL_STOP_THRESHOLD:
            message = (
                f'LLM Tool Service stopped the loop: the model repeated the '
                f'identical tool call "{tool_call.name}" {signature_count} times in '
                'this conversation and the result never changed.'
            )
            raise LlmRecoverableError(message)

        if result_count >= REPEATED_CALL_STOP_THRESHOLD:
            message = (
                f'LLM Tool Service stopped the loop: the tool "{tool_call.name}" '
                f'returned the identical result {result_count} times in this '
                'conversation, so the model is not gathering new information.'
            )
            raise LlmRecoverableError(message)

        if signature_count >= REPEATED_CALL_WARNING_THRESHOLD:
            if verbose_callback is not None:
                verbose_callback(
                    f'  - {tool_call.name} repeated {signature_count}x: steering note added'
                )
            result_text += (
                '\n\n[Note: you have now run this exact same call '
                f'{signature_count} times in this conversation and received the '
                'identical result each time. Repeating it again will not change '
                'anything. Either change your approach (for example, edit the '
                'code or run a different command) or stop calling tools and give '
                'your final answer.]'
            )
        elif result_count >= REPEATED_CALL_WARNING_THRESHOLD:
            if verbose_callback is not None:
                verbose_callback(
                    f'  - {tool_call.name} same result {result_count}x: steering note added'
                )
            result_text += (
                f'\n\n[Note: the tool "{tool_call.name}" has now returned this '
                f'exact same result {result_count} times in this conversation. '
                'Reading it again will not change anything. Either change your '
                'approach (for example, edit the code or run a different command) '
                'or stop calling tools and give your final answer.]'
            )

        return result_text

    def reset(self):
        pass
