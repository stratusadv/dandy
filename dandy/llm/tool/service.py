from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError

from dandy.core.service.service import BaseService
from dandy.core.utils import pydantic_validation_error_to_str
from dandy.intel.factory import IntelFactory
from dandy.llm.exceptions import LlmCriticalError, LlmRecoverableError
from dandy.llm.tool.intel import LlmToolCallIntel, LlmToolCallsIntel
from dandy.llm.tool.recorder import recorder_add_tool_result_event
from dandy.tool.tool import (
    BaseTool,
    ToolType,
    ToolHandler,
    to_tool_instances,
)

if TYPE_CHECKING:
    from dandy.intel.typing import IntelType
    from dandy.llm.prompt.prompt import Prompt


class LlmToolService(BaseService['dandy.llm.tool.mixin.LlmToolServiceMixin']):
    def prompt_to_intel(
            self,
            prompt: Prompt | str | None = None,
            intel_class: type[IntelType] | None = None,
            intel_object: IntelType | None = None,
            tools: list[ToolType] | None = None,
            tool_functions: dict[str, ToolHandler] | None = None,
            max_tool_iterations: int = 5,
            **kwargs,
    ) -> IntelType:
        tool_instances = to_tool_instances(tools)
        tools_by_name = {tool.name: tool for tool in tool_instances}
        tool_functions = tool_functions or {}

        iteration_count = 0

        while True:
            intel = self.obj.prompt_to_intel(
                prompt=prompt if iteration_count == 0 else None,
                intel_class=intel_class,
                intel_object=intel_object,
                tools=tool_instances,
                **kwargs,
            )

            if not isinstance(intel, LlmToolCallsIntel):
                return intel

            if iteration_count >= max_tool_iterations:
                message = (
                    f'LLM Tool Service gave up after {max_tool_iterations} tool '
                    f'iterations without a final response.'
                )
                raise LlmRecoverableError(message)

            for tool_call in intel:
                self._process_tool_call(
                    tool_call=tool_call,
                    tools_by_name=tools_by_name,
                    tool_functions=tool_functions,
                )

            iteration_count += 1

    def _process_tool_call(
            self,
            tool_call: LlmToolCallIntel,
            tools_by_name: dict[str, BaseTool],
            tool_functions: dict[str, ToolHandler],
    ) -> None:
        tool = tools_by_name.get(tool_call.name)

        if tool is None:
            message = f'No BaseTool with the name "{tool_call.name}" was provided.'
            raise LlmCriticalError(message)

        tool_function = tool_functions.get(tool_call.name) or tool.handle

        parameters_intel_class = tool.get_parameters_intel_class()

        if parameters_intel_class is not None:
            try:
                arguments_intel = IntelFactory.json_str_to_intel_object(
                    json_str=tool_call.arguments,
                    intel=parameters_intel_class,
                )
            except ValidationError as error:
                self.obj.messages.add_message(
                    role='tool',
                    tool_call_id=tool_call.id,
                    text=(
                        f'Tool "{tool_call.name}" received arguments that could not '
                        f'be validated: {pydantic_validation_error_to_str(error)}'
                    ),
                )
                return
        else:
            arguments_intel = tool_call.arguments

        result = tool_function(arguments_intel)
        result_text = result if isinstance(result, str) else result.model_dump_json()

        recorder_add_tool_result_event(
            tool_name=tool_call.name,
            result=result_text,
            event_id=self.recorder_event_id,
        )

        self.obj.messages.add_message(
            role='tool',
            tool_call_id=tool_call.id,
            text=result_text,
        )

    def reset(self):
        pass
