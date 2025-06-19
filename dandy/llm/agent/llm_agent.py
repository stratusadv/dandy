from abc import ABC
from pathlib import Path
from typing import Generic

from pydantic.main import IncEx
from typing_extensions import Type, Union, List

from dandy.agent import BaseAgent
from dandy.agent.exceptions import AgentRecoverableException, AgentOverThoughtRecoverableException
from dandy.agent.strategy import BaseAgentStrategy
from dandy.conf import settings
from dandy.intel.type_vars import IntelType
from dandy.llm.agent.llm_plan import LlmAgentPlanIntel
from dandy.llm.agent.llm_strategy import DefaultLlmAgentStrategy
from dandy.llm.agent.recorder import recorder_add_llm_agent_event
from dandy.llm.bot.llm_bot import BaseLlmBot, LlmBot
from dandy.llm.intel import DefaultLlmIntel
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.service.config import LlmConfigOptions
from dandy.llm.service.request.message import MessageHistory
from dandy.recorder.utils import generate_new_recorder_event_id


class BaseLlmAgent(BaseLlmBot, BaseAgent, ABC, Generic[IntelType]):
    config: str = 'DEFAULT'
    config_options: LlmConfigOptions = LlmConfigOptions()
    description: Union[Prompt, str, None] = None
    instructions_prompt: Prompt = Prompt("You're a helpful assistant please follow the users instructions.")
    intel_class: Type[IntelType] = DefaultLlmIntel
    plan_time_limit_seconds: int = settings.DEFAULT_AGENT_PLAN_TIME_LIMIT_SECONDS
    plan_task_count_limit: int = settings.DEFAULT_AGENT_PLAN_TASK_COUNT_LIMIT
    strategy: Type[BaseAgentStrategy] = DefaultLlmAgentStrategy

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

        recorder_event_id = generate_new_recorder_event_id()

        recorder_add_llm_agent_event('Creating Plan', recorder_event_id)

        plan = cls._create_plan(prompt)

        recorder_add_llm_agent_event('Finished Plan', recorder_event_id)

        recorder_add_llm_agent_event('Running Plan', recorder_event_id)

        while not plan.is_complete:
            if plan.has_exceeded_time_limit:
                raise AgentOverThoughtRecoverableException(
                    f'{cls.__name__} exceeded the time limit of {cls.plan_time_limit_seconds} seconds running a plan.'
                )

            task = plan.active_task

            task_description = f'Task #{plan.active_task_number}'
            recorder_add_llm_agent_event(f'Starting {task_description}', recorder_event_id)

            do_task_prompt = (
                Prompt()
                .text('Use the description and desired result to accomplish the task:')
                .line_break()
                .text(f'Description: {task.description}')
                .line_break()
                .text(f'Desired Result: {task.desired_result_description}')
                .line_break()
            )

            resource = cls.strategy.get_resource_from_key(task.strategy_resource_key)

            updated_task = resource.process(
                prompt=do_task_prompt,
                intel_object=task,
                include_fields={'actual_result'}
            )

            task.actual_result = updated_task.actual_result
            plan.set_active_task_complete()

            recorder_add_llm_agent_event(f'Finished {task_description}', recorder_event_id)

        recorder_add_llm_agent_event('Done Executing Plan', recorder_event_id)

        recorder_add_llm_agent_event('Creating Final Result', recorder_event_id)

        print(plan.model_dump_json(indent=4))

        if postfix_system_prompt is None:
            postfix_system_prompt = Prompt()

        postfix_system_prompt.text(f'Use the results of the below simulated plan to accomplish the user request:')
        postfix_system_prompt.line_break()
        postfix_system_prompt.prompt(plan.to_prompt())

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
            .text('You need to create a plan with a set of tasks based on a given request by the user.')
            .text('Make sure to assign a strategy resource to each task created.')
            .line_break()
            .sub_heading('Strategy Resources')
            .dict(cls.strategy.as_dict())
            .prompt(prompt)
        )

        plan = LlmBot.process(
            prompt=create_plan_prompt,
            intel_class=LlmAgentPlanIntel,
            include_fields={
                'tasks': {'description', 'desired_result'}
            }
        )

        plan.set_plan_time_limit(cls.plan_time_limit_seconds)

        cls._validate_plan_or_error(plan)

        return plan

    @classmethod
    def _validate_plan_or_error(cls, plan: LlmAgentPlanIntel):
        if plan.tasks is None or len(plan.tasks) == 0:
            raise AgentRecoverableException(
                f'{cls.__name__} created plan that has no tasks.'
            )

        if len(plan.tasks) > cls.plan_task_count_limit:
            raise AgentOverThoughtRecoverableException(
                f'{cls.__name__} created plan had {len(plan.tasks)} tasks which is more than the limit of {cls.plan_task_count_limit}.'
            )


class LlmAgent(BaseLlmAgent, Generic[IntelType]):
    description = 'Default large language model agent that processes prompts into responses.'
