from dataclasses import dataclass
from pathlib import Path

from typing import Type, Sequence, List, ClassVar

from pydantic.main import IncEx

from dandy.processor.agent.exceptions import AgentCriticalException, AgentOverThoughtRecoverableException, \
    AgentRecoverableException
from dandy.processor.agent.llm_strategy import BaseLlmProcessorsStrategy
from dandy.processor.agent.plan.llm_plan import LlmAgentPlanIntel
from dandy.processor.agent.prompts import agent_do_task_prompt, agent_create_plan_prompt
from dandy.processor.agent.recorder import recorder_add_llm_agent_create_plan_event, \
    recorder_add_llm_agent_finished_creating_plan_event, recorder_add_llm_agent_running_plan_event, \
    recorder_add_llm_agent_start_task_event, recorder_add_llm_agent_completed_task_event, \
    recorder_add_llm_agent_done_executing_plan_event, recorder_add_llm_agent_processing_final_result_event
from dandy.processor.agent.service import AgentService
from dandy.processor.bot.bot import Bot
from dandy.http.mixin import HttpProcessorMixin
from dandy.intel.typing import IntelType
from dandy.llm.mixin import LlmProcessorMixin
from dandy.processor.processor import BaseProcessor
from dandy.conf import settings
from dandy.llm.prompt import Prompt
from dandy.llm.prompt.typing import PromptOrStr, PromptOrStrOrNone
from dandy.llm.request.message import MessageHistory
from dandy.vision.mixin import VisionProcessorMixin


@dataclass(kw_only=True)
class Agent(
    BaseProcessor,
    LlmProcessorMixin,
    HttpProcessorMixin,
    VisionProcessorMixin,
):
    plan_time_limit_seconds: int = settings.DEFAULT_AGENT_PLAN_TIME_LIMIT_SECONDS
    plan_task_count_limit: int = settings.DEFAULT_AGENT_PLAN_TASK_COUNT_LIMIT
    # _processors_strategy_class: Type[BaseProcessorsStrategy]
    # _processors_strategy: BaseProcessorsStrategy
    # processors: Sequence[Type[BaseProcessor]]
    _processors_strategy_class = BaseLlmProcessorsStrategy
    _processors_strategy: BaseLlmProcessorsStrategy | None = None
    processors: Sequence[Type[BaseProcessor]] = (
        Bot,
    )

    services: ClassVar[AgentService] = AgentService()

    def __init_subclass__(cls, **kwargs):
        if cls.processors is None or len(cls.processors) == 0:
            raise AgentCriticalException(
                f'{cls.__name__} must have a sequence of "BaseProcessor" sub classes defined on the "processors" class attribute.'
            )

        if cls._processors_strategy_class is None:
            raise AgentCriticalException(
                f'{cls.__name__} must have a "BaseProcessorsStrategy" sub class defined on the "_processors_strategy_class" class attribute.'
            )

        else:
            cls._processors_strategy = cls._processors_strategy_class(
                cls.processors
            )

    def process(
            self,
            prompt: PromptOrStr,
            intel_class: Type[IntelType] | None = None,
            intel_object: IntelType | None = None,
            images: List[str] | None = None,
            image_files: List[str | Path] | None = None,
            include_fields: IncEx | None = None,
            exclude_fields: IncEx | None = None,
            postfix_system_prompt: PromptOrStrOrNone = None,
            message_history: MessageHistory | None = None,
    ) -> IntelType:

        recorder_event_id = self._recorder_event_id

        recorder_add_llm_agent_create_plan_event(
            prompt,
            self.__class__._processors_strategy,
            recorder_event_id
        )

        plan = self._create_plan(prompt)

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
                    f'{self.__class__.__name__} exceeded the time limit of {self.plan_time_limit_seconds} seconds running a plan.'
                )

            task = plan.active_task

            recorder_add_llm_agent_start_task_event(
                task,
                self.__class__._processors_strategy,
                recorder_event_id
            )

            resource = self.__class__._processors_strategy.get_processor_from_key(task.processors_key)

            updated_task = resource.use(
                prompt=agent_do_task_prompt(task),
                intel_object=task,
                include_fields={'actual_result'}
            )

            task.actual_result = updated_task.actual_result
            plan.set_active_task_complete()

            recorder_add_llm_agent_completed_task_event(
                task,
                self.__class__._processors_strategy,
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

        return self.llm.prompt_to_intel(
            prompt=prompt,
            intel_class=intel_class or self.intel_class,
            intel_object=intel_object,
            images=images,
            image_files=image_files,
            include_fields=include_fields,
            exclude_fields=exclude_fields,
            postfix_system_prompt=postfix_system_prompt,
            message_history=message_history,
        )

    def _create_plan(
            self,
            prompt: PromptOrStr,
    ) -> LlmAgentPlanIntel:
        plan = self.llm.prompt_to_intel(
            prompt=agent_create_plan_prompt(
                user_prompt=prompt,
                instructions_prompt=self.llm_instructions_prompt,
                processors_strategy=self.__class__._processors_strategy,
            ),
            intel_class=LlmAgentPlanIntel,
            include_fields={
                'tasks': {'description', 'desired_result'}
            }
        )

        plan.set_plan_time_limit(self.plan_time_limit_seconds)

        self._validate_plan_or_error(plan)

        return plan

    def _validate_plan_or_error(self, plan: LlmAgentPlanIntel):
        if plan.tasks is None or len(plan.tasks) == 0:
            raise AgentRecoverableException(
                f'{self.__class__.__name__} created plan that has no tasks.'
            )

        if len(plan.tasks) > self.plan_task_count_limit:
            raise AgentOverThoughtRecoverableException(
                f'{self.__class__.__name__} created plan had {len(plan.tasks)} tasks which is more than the limit of {self.plan_task_count_limit}.'
            )


