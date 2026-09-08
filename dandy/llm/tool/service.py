from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from pydantic import ValidationError

from dandy.core.service.service import BaseService
from dandy.core.utils import pascal_to_title_case, pydantic_validation_error_to_str
from dandy.intel.factory import IntelFactory
from dandy.llm.exceptions import LlmCriticalError, LlmRecoverableError
from dandy.llm.request.message import compact_message_history
from dandy.llm.tool.intel import LlmToolCallIntel, LlmToolCallsIntel
from dandy.llm.tool.recorder import recorder_add_tool_result_event
from dandy.tool.tool import BaseTool, ToolType, ToolHandler, to_tool_instances

if TYPE_CHECKING:
    from dandy.intel.typing import IntelType
    from dandy.llm.prompt.prompt import Prompt

# Compaction in the tool loop keeps the accumulated conversation to this share
# of the model's context window, matching the agent's compaction target in
# dandy/cli/intelligence/coding_agent.py (0.70). The derived max_completion_tokens
# (LLM_OUTPUT_TOKEN_RATIO, 0.20) reserves the output, leaving a 0.10 margin so a
# long tool-calling session never overflows the provider's context window. The
# fallback window mirrors AGENT_MAX_CONTEXT_TOKENS_DEFAULT for configs without a
# CONTEXT_SIZE.

TOOL_LOOP_CONTEXT_DEFAULT = 65536
TOOL_LOOP_COMPACTION_TARGET_RATIO = 0.70


def _tool_preview(text: str, limit: int = 240) -> str:
    """One-line preview of tool arguments or results for verbose tracing."""
    text = text.replace('\n', '\\n')
    return f'{text[:limit]}{"..." if len(text) > limit else ""}'


class LlmToolService(BaseService['dandy.llm.tool.mixin.LlmToolServiceMixin']):
    def prompt_to_intel(
        self,
        prompt: Prompt | str | None = None,
        intel_class: type[IntelType] | None = None,
        intel_object: IntelType | None = None,
        tools: list[ToolType] | None = None,
        tool_functions: dict[str, ToolHandler] | None = None,
        max_tool_iterations: int | None = 5,
        progress_callback: Callable[[str], None] | None = None,
        verbose_callback: Callable[[str], None] | None = None,
        **kwargs,
    ) -> IntelType:
        tool_instances = to_tool_instances(tools)
        tools_by_name = {tool.name: tool for tool in tool_instances}
        tool_functions = tool_functions or {}

        iteration_count = 0

        while True:
            self._compact_history_before_next_round(progress_callback=progress_callback)

            if progress_callback is not None:
                progress_callback('Thinking')

            intel = self.obj.prompt_to_intel(
                prompt=prompt if iteration_count == 0 else None,
                intel_class=intel_class,
                intel_object=intel_object,
                tools=tool_instances,
                **kwargs,
            )

            if not isinstance(intel, LlmToolCallsIntel):
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

            for tool_call in intel:
                if progress_callback is not None:
                    progress_callback(pascal_to_title_case(tool_call.name))

                if verbose_callback is not None:
                    verbose_callback(
                        f'  - {tool_call.name} args: {_tool_preview(tool_call.arguments)}'
                    )

                self._process_tool_call(
                    tool_call=tool_call,
                    tools_by_name=tools_by_name,
                    tool_functions=tool_functions,
                    verbose_callback=verbose_callback,
                )

            iteration_count += 1

    def _compact_history_before_next_round(
        self, progress_callback: Callable[[str], None] | None = None
    ) -> None:
        """Trim the accumulated conversation before the next LLM round.

        Long-running tool loops append a tool-call request plus its results per
        round, which can overflow the provider's context window when the loop is
        unbounded. Uses the resolved config's ``CONTEXT_SIZE`` (a default window
        when unset) and compacts to a fraction of it, keeping the system message
        and the newest exchange.
        """
        context_size = getattr(self.obj.config, 'context_size', 0) or TOOL_LOOP_CONTEXT_DEFAULT
        target_token_count = max(1, int(context_size * TOOL_LOOP_COMPACTION_TARGET_RATIO))

        current_token_count = self.obj.messages.estimated_token_count

        if current_token_count <= target_token_count:
            return

        if progress_callback is not None:
            progress_callback(f'Compacting conversation history ({current_token_count} tokens)...')

        compact_message_history(history=self.obj.messages, max_context_tokens=target_token_count)

    def _process_tool_call(
        self,
        tool_call: LlmToolCallIntel,
        tools_by_name: dict[str, BaseTool],
        tool_functions: dict[str, ToolHandler],
        verbose_callback: Callable[[str], None] | None = None,
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

        if tool_function is None:
            result = tool.handle(**arguments_intel.model_dump())
        else:
            result = tool_function(arguments_intel)

        result_text = result if isinstance(result, str) else result.model_dump_json()

        if verbose_callback is not None:
            verbose_callback(f'  - {tool_call.name} result: {_tool_preview(result_text)}')

        recorder_add_tool_result_event(
            tool_name=tool_call.name, result=result_text, event_id=self.recorder_event_id
        )

        self.obj.messages.add_message(role='tool', tool_call_id=tool_call.id, text=result_text)

    def reset(self):
        pass
