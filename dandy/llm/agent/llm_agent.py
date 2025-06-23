from abc import ABC
from pathlib import Path
from typing import Generic

from pydantic.main import IncEx
from typing_extensions import Type, Union, List, Sequence

from dandy.agent import BaseAgent
from dandy.agent.exceptions import AgentRecoverableException, AgentOverThoughtRecoverableException
from dandy.conf import settings
from dandy.intel.typing import IntelType
from dandy.llm.agent.llm_plan import LlmAgentPlanIntel
from dandy.llm.processor.llm_processor import BaseLlmProcessor
from dandy.llm.processor.llm_strategy import BaseLlmProcessorsStrategy
from dandy.llm.agent.prompts import agent_create_plan_prompt, agent_do_task_prompt
from dandy.llm.agent.recorder import recorder_add_llm_agent_create_plan_event, \
    recorder_add_llm_agent_finished_creating_plan_event, recorder_add_llm_agent_running_plan_event, \
    recorder_add_llm_agent_start_task_event, recorder_add_llm_agent_completed_task_event, \
    recorder_add_llm_agent_done_executing_plan_event, recorder_add_llm_agent_processing_final_result_event
from dandy.llm.bot.llm_bot import BaseLlmBot, LlmBot
from dandy.llm.intel import DefaultLlmIntel
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.prompt.typing import PromptOrStr, PromptOrStrOrNone
from dandy.llm.service.config import LlmConfigOptions
from dandy.llm.service.request.message import MessageHistory
from dandy.recorder.utils import generate_new_recorder_event_id


class BaseLlmAgent(BaseLlmBot, BaseAgent, ABC, Generic[IntelType]):
    config: str = 'DEFAULT'
    config_options: LlmConfigOptions = LlmConfigOptions()
    description: PromptOrStrOrNone = None
    instructions_prompt: Prompt = Prompt("You're a helpful assistant please follow the users instructions.")
    intel_class: Type[IntelType] = DefaultLlmIntel
    plan_time_limit_seconds: int = settings.DEFAULT_AGENT_PLAN_TIME_LIMIT_SECONDS
    plan_task_count_limit: int = settings.DEFAULT_AGENT_PLAN_TASK_COUNT_LIMIT
    _processors_strategy_class = BaseLlmProcessorsStrategy
    _processors_strategy: BaseLlmProcessorsStrategy
    processors: Sequence[Type[BaseLlmProcessor]] = (
        LlmBot,
    )

    @classmethod
    def process(
            cls,
            prompt: PromptOrStr,
            intel_class: Union[Type[IntelType], None] = None,
            intel_object: Union[IntelType, None] = None,
            images: Union[List[str], None] = None,
            image_files: Union[List[str | Path], None] = None,
            include_fields: Union[IncEx, None] = None,
            exclude_fields: Union[IncEx, None] = None,
            postfix_system_prompt: PromptOrStrOrNone = None,
            message_history: Union[MessageHistory, None] = None,
    ) -> IntelType:

        recorder_event_id = cls._recorder_event_id

        recorder_add_llm_agent_create_plan_event(
            prompt,
            cls._processors_strategy,
            recorder_event_id
        )

        plan = cls._create_plan(prompt)

        recorder_add_llm_agent_finished_creating_plan_event(
            plan,
            recorder_event_id
        )

        recorder_add_llm_agent_running_plan_event(
            plan,
            recorder_event_id
        )

        while plan.is_incomplete:
            if plan.has_exceeded_time_limit:
                raise AgentOverThoughtRecoverableException(
                    f'{cls.__name__} exceeded the time limit of {cls.plan_time_limit_seconds} seconds running a plan.'
                )

            task = plan.active_task

            recorder_add_llm_agent_start_task_event(
                task,
                cls._processors_strategy,
                recorder_event_id
            )

            resource = cls._processors_strategy.get_processor_from_key(task.processors_key)

            updated_task = resource.use(
                prompt=agent_do_task_prompt(task),
                intel_object=task,
                include_fields={'actual_result'}
            )

            task.actual_result = updated_task.actual_result
            plan.set_active_task_complete()

            recorder_add_llm_agent_completed_task_event(
                task,
                cls._processors_strategy,
                recorder_event_id
            )

        recorder_add_llm_agent_done_executing_plan_event(
            plan,
            recorder_event_id
        )

        recorder_add_llm_agent_processing_final_result_event(
            plan,
            recorder_event_id
        )

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
            prompt: PromptOrStr,
    ) -> LlmAgentPlanIntel:
        plan = LlmBot.process(
            prompt=agent_create_plan_prompt(
                user_prompt=prompt,
                instructions_prompt=cls.instructions_prompt,
                processors_strategy=cls._processors_strategy,
            ),
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
    processors: Sequence[Type[BaseLlmProcessor]] = (
        LlmBot,
    )
