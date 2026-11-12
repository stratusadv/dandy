from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from pydantic import ValidationError

from dandy.shared.cancellation import stop_signal
from dandy.shared.exceptions import RUN_STOPPED_MESSAGE, RunStoppedError
from dandy.shared.service.service import BaseService
from dandy.shared.utils import (
    pascal_to_title_case,
    pydantic_validation_error_to_str,
    truncate_output,
)
from dandy.domain.guard.context_guard import ContextPressureGuard
from dandy.domain.guard.guard import GuardChain, GuardEvent
from dandy.domain.guard.repeat_guard import RepeatGuard
from dandy.domain.intel.factory import IntelFactory
from dandy.domain.request.exceptions import LlmCriticalError, LlmRecoverableError
from dandy.domain.message.compaction import (
    COMPACTION_TARGET_RATIO,
    DEFAULT_CONTEXT_WINDOW,
    compact_message_history,
)
from dandy.domain.tool.beat import StoryBeat
from dandy.domain.tool.intel import ToolCallIntel, ToolCallsIntel
from dandy.infrastructure.recorder.tool_events import recorder_add_tool_result_event
from dandy.domain.tool.tool import BaseTool, ToolType, ToolHandler, to_tool_instances

if TYPE_CHECKING:
    from dandy.application.skill.service import SkillService
    from dandy.domain.intel.typing import IntelType
    from dandy.domain.prompt.prompt import Prompt


def _tool_preview(text: str, limit: int = 240) -> str:
    """One-line preview of tool arguments or results for verbose tracing."""
    text = text.replace('\n', '\\n')
    return f'{text[:limit]}{"..." if len(text) > limit else ""}'


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
        # The guards watch the model's behavior live: the repeat guard steers
        # the model out of degenerate repeat loops, and the context-pressure
        # guard keeps the conversation inside the window, failing the loop
        # fast when a correction stops working instead of letting the
        # provider reject the request.
        guard_chain = GuardChain([RepeatGuard(), ContextPressureGuard()])

        while True:
            if stop_signal.is_set():
                raise RunStoppedError(RUN_STOPPED_MESSAGE)

            context_size = getattr(self.obj.config, 'context_size', 0) or DEFAULT_CONTEXT_WINDOW

            round_outcome = guard_chain.on_round_start(
                self.obj.messages.estimated_token_count, context_size
            )

            if round_outcome.compact:
                self._compact_history(progress_callback=progress_callback)

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
                    raise RunStoppedError(RUN_STOPPED_MESSAGE)

                if verbose_callback is not None:
                    verbose_callback(
                        f'  - {tool_call.name} args: {_tool_preview(tool_call.arguments)}'
                    )

                self._process_tool_call(
                    tool_call=tool_call,
                    tools_by_name=tools_by_name,
                    tool_functions=tool_functions,
                    guard_chain=guard_chain,
                    round_number=round_number,
                    context_size=context_size,
                    progress_callback=progress_callback,
                    verbose_callback=verbose_callback,
                    tool_call_callback=tool_call_callback,
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

    def _compact_history(
        self, progress_callback: Callable[[StoryBeat], None] | None = None
    ) -> None:
        """Trim the accumulated conversation before the next LLM round.

        Long-running tool loops append a tool-call request plus its results per
        round, which can overflow the provider's context window when the loop
        is unbounded. Compacts to a fraction of the resolved config's
        ``CONTEXT_SIZE`` (a default window when unset), keeping the system
        message and the newest exchange. The context-pressure guard decides
        when this runs, so a steady state where each round re-adds about what
        compaction just dropped does not compact every round.
        """
        context_size = getattr(self.obj.config, 'context_size', 0) or DEFAULT_CONTEXT_WINDOW
        target_token_count = max(1, int(context_size * COMPACTION_TARGET_RATIO))

        if progress_callback is not None:
            progress_callback(
                StoryBeat(
                    description='Compacting my thoughts into a more manageable size',
                    kind='compaction',
                )
            )

        compact_message_history(history=self.obj.messages, max_context_tokens=target_token_count)

    def _process_tool_call(
        self,
        tool_call: ToolCallIntel,
        tools_by_name: dict[str, BaseTool],
        tool_functions: dict[str, ToolHandler],
        *,
        guard_chain: GuardChain,
        round_number: int,
        context_size: int,
        progress_callback: Callable[[StoryBeat], None] | None = None,
        verbose_callback: Callable[[str], None] | None = None,
        tool_call_callback: Callable[[str, dict[str, object]], None] | None = None,
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

        if progress_callback is not None and tool.emits_story_beat:
            label = tool.action_label or pascal_to_title_case(tool_call.name)
            description = tool.action_output(**arguments_kwargs) or ''
            progress_callback(
                StoryBeat(
                    label=label, description=description, can_mutate_state=tool.can_mutate_state
                )
            )

        if tool_function is None:
            result = tool.handle(**arguments_kwargs)
        else:
            result = tool_function(arguments_intel)

        if tool_call_callback is not None:
            tool_call_callback(tool_call.name, arguments_kwargs)

        result_text = result if isinstance(result, str) else result.model_dump_json()

        result_text = truncate_output(result_text)

        if verbose_callback is not None:
            verbose_callback(f'  - {tool_call.name} result: {_tool_preview(result_text)}')

        recorder_add_tool_result_event(
            tool_name=tool_call.name, result=result_text, event_id=self.recorder_event_id
        )

        feedback_text = guard_chain.on_tool_call(
            GuardEvent(
                tool_name=tool_call.name,
                arguments=arguments_kwargs,
                result_text=result_text,
                round_number=round_number,
                history_token_count=self.obj.messages.estimated_token_count,
                context_window=context_size,
            ),
            verbose_callback=verbose_callback,
        )

        self.obj.messages.add_message(role='tool', tool_call_id=tool_call.id, text=feedback_text)

    def reset(self) -> None:
        pass
