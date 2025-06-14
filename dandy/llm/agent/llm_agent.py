from abc import ABC
from pathlib import Path
from typing import Generic

from pydantic.main import IncEx
from typing_extensions import Type, Union, List

from dandy.agent import BaseAgent
from dandy.agent.strategy.strategy import BaseAgentStrategy
from dandy.intel.type_vars import IntelType
from dandy.llm.agent.llm_plan import LlmAgentPlanIntel
from dandy.llm.bot.llm_bot import BaseLlmBot, LlmBot
from dandy.llm.intel import DefaultLlmIntel
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.service.config import LlmConfigOptions
from dandy.llm.service.request.message import MessageHistory


class BaseLlmAgent(BaseLlmBot, BaseAgent, ABC, Generic[IntelType]):
    config: str = 'DEFAULT'
    config_options: LlmConfigOptions = LlmConfigOptions()
    description: Union[Prompt, str, None] = None
    instructions_prompt: Prompt = Prompt("You're a helpful assistant please follow the users instructions.")
    intel_class: Type[IntelType] = DefaultLlmIntel
    strategy: Type[BaseAgentStrategy] | None = None

    @classmethod
    def process(
            cls,
            prompt: Union[Prompt, str],
            intel_class: Union[Type[IntelType], None] = None,
            intel_object: Union[IntelType, None] = None,
            images: Union[List[str], None] = None,
            image_files: Union[List[str | Path], None] = None,
            include_fields: Union[IncEx, None] = None,
            exclude_fields: Union[IncEx, None] = None,
            postfix_system_prompt: Union[Prompt, None] = None,
            message_history: Union[MessageHistory, None] = None,
    ) -> IntelType:
        plan = cls._create_plan(prompt)

        for task in plan.tasks:
            do_task_prompt = (
                Prompt()
                .text('Use the description and desired result to accomplish the task:')
                .line_break()
                .text(f'Description: {task.description}')
                .line_break()
                .text(f'Desired Result: {task.desired_result}')
                .line_break()
            )
            updated_task = LlmBot.process_prompt_to_intel(
                prompt=do_task_prompt,
                intel_object=task,
                include_fields={'actual_result'}
            )

            task.actual_result = updated_task.actual_result
            task.set_complete()

        print(plan.model_dump_json(indent=4))

        return cls.process_prompt_to_intel(
            prompt=prompt,
            intel_class=intel_class or cls.intel_class,
            intel_object=intel_object,
            images=images,
            image_files=image_files,
            include_fields=include_fields,
            exclude_fields=exclude_fields,
            postfix_system_prompt=postfix_system_prompt,
            message_history=message_history,
        )

    @classmethod
    def _create_plan(
            cls,
            prompt: Union[Prompt, str],
    ) -> LlmAgentPlanIntel:
        create_plan_prompt = (
            Prompt()
            .prompt(cls.instructions_prompt)
            .line_break()
            .text('You need to create a plan with a set of tasks to accomplish the following request:')
            .line_break()
            .prompt(prompt)
        )

        return LlmBot.process_prompt_to_intel(
            prompt=create_plan_prompt,
            intel_class=LlmAgentPlanIntel,
            include_fields={
                'tasks': {'description', 'desired_result'}
            }
        )
