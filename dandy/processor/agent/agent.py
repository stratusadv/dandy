from pathlib import Path
from typing import Sequence, ClassVar

from pydantic.main import IncEx

from dandy.processor.agent.intelligence.intel.task_intel import TaskIntel
from dandy.processor.bot.bot import Bot
from dandy.conf import settings
from dandy.http.mixin import HttpServiceMixin
from dandy.intel.mixin import IntelServiceMixin
from dandy.intel.typing import IntelType
from dandy.llm.mixin import LlmServiceMixin
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.prompt.typing import PromptOrStr, PromptOrStrOrNone
from dandy.llm.request.message import MessageHistory
from dandy.processor.agent.exceptions import AgentCriticalException, AgentOverThoughtRecoverableException, \
    AgentRecoverableException
from dandy.processor.agent.intelligence.intel.plan_intel import PlanIntel
from dandy.processor.agent.intelligence.bots.generic_task_bot import GenericTaskBot
from dandy.processor.agent.intelligence.prompts import agent_do_task_prompt, agent_create_plan_prompt
from dandy.processor.agent.recorder import recorder_add_llm_agent_create_plan_event, \
    recorder_add_llm_agent_finished_creating_plan_event, recorder_add_llm_agent_running_plan_event, \
    recorder_add_llm_agent_start_task_event, recorder_add_llm_agent_completed_task_event, \
    recorder_add_llm_agent_done_executing_plan_event, recorder_add_llm_agent_processing_final_result_event
from dandy.processor.agent.service import AgentService
from dandy.processor.agent.strategy import ProcessorsStrategy
from dandy.processor.processor import BaseProcessor
from dandy.vision.mixin import VisionProcessorMixin


class Agent(
    BaseProcessor,
    LlmServiceMixin,
    HttpServiceMixin,
    IntelServiceMixin,
    VisionProcessorMixin,
):
    plan_time_limit_seconds: int = settings.AGENT_DEFAULT_PLAN_TIME_LIMIT_SECONDS
    plan_task_count_limit: int = settings.AGENT_DEFAULT_PLAN_TASK_COUNT_LIMIT

    processors: Sequence[type[BaseProcessor]] = (
        GenericTaskBot,
    )

    services: ClassVar[AgentService] = AgentService()
    _AgentService_instance: AgentService | None = None

    def __init_subclass__(cls, **kwargs):
        if cls.processors is None or len(cls.processors) == 0:
            message = f'{cls.__name__} must have a sequence of "BaseProcessor" sub classes defined on the "processors" class attribute.'
            raise AgentCriticalException(message)

        for processor in cls.processors:
            if processor is Bot:
                message = f'{cls.__name__} cannot have a "Bot" class defined on the "processors" class attribute.'
                raise AgentCriticalException(message)

    def __post_init__(self):
        self._processors_strategy = ProcessorsStrategy(
            self.processors
        )

    @classmethod
    def get_description(cls) -> str | None:
        if cls.description is not None:
            return cls.description

        return cls.get_llm_description()

    def process(
            self,
            prompt: PromptOrStr,
            intel_class: type[IntelType] | None = None,
            intel_object: IntelType | None = None,
            images: list[str] | None = None,
            image_files: list[str | Path] | None = None,
            include_fields: IncEx | None = None,
            exclude_fields: IncEx | None = None,
            postfix_system_prompt: PromptOrStrOrNone = None,
            message_history: MessageHistory | None = None,
    ) -> IntelType:

        plan_intel = self._create_plan(prompt)

        completed_plan_intel = self._run_plan(plan_intel)

        recorder_add_llm_agent_processing_final_result_event(
            completed_plan_intel,
            self._recorder_event_id
        )

        if postfix_system_prompt is None:
            postfix_system_prompt = Prompt()

        postfix_system_prompt.text('Use the results of the below simulated plan to accomplish the user request:')
        postfix_system_prompt.line_break()
        postfix_system_prompt.prompt(plan_intel.to_prompt())

        return self.llm.prompt_to_intel(
            prompt=prompt,
            intel_class=intel_class,
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
    ) -> PlanIntel:

        recorder_add_llm_agent_create_plan_event(
            prompt,
            self._processors_strategy,
            self._recorder_event_id
        )

        plan_intel = self.llm.prompt_to_intel(
            prompt=agent_create_plan_prompt(
                user_prompt=prompt,
                instructions_prompt=self.llm_role,
                processors_strategy=self._processors_strategy,
            ),
            intel_class=PlanIntel,
            include_fields={
                'tasks': {'description', 'desired_result'}
            }
        )

        plan_intel.set_plan_time_limit(self.plan_time_limit_seconds)

        self._validate_plan_or_error(plan_intel)

        recorder_add_llm_agent_finished_creating_plan_event(
            plan_intel, self._recorder_event_id
        )

        return plan_intel

    def _execute_task(self, task_intel: TaskIntel) -> TaskIntel:
        recorder_add_llm_agent_start_task_event(
            task_intel, self._processors_strategy, self._recorder_event_id
        )

        processor_controller = self._processors_strategy.get_processor_controller_from_key(task_intel.processors_key)

        updated_task = processor_controller.use(
            prompt=agent_do_task_prompt(task_intel),
            intel_object=task_intel,
            include_fields={'actual_result'},
        )

        task_intel.actual_result = updated_task.actual_result

        recorder_add_llm_agent_completed_task_event(
            task_intel,
            self._processors_strategy,
            self._recorder_event_id
        )

        return task_intel


    def _run_plan(self, plan_intel: PlanIntel) -> PlanIntel:
        recorder_add_llm_agent_running_plan_event(
            plan_intel,
            self._recorder_event_id
        )

        while plan_intel.is_incomplete:
            if plan_intel.has_exceeded_time_limit:
                message = f'{self.__class__.__name__} exceeded the time limit of {self.plan_time_limit_seconds} seconds running a plan.'
                raise AgentOverThoughtRecoverableException(message)

            self._execute_task(plan_intel.active_task)

            plan_intel.set_active_task_complete()

        recorder_add_llm_agent_done_executing_plan_event(
            plan_intel,
            self._recorder_event_id
        )

        return plan_intel


    def _validate_plan_or_error(self, plan_intel: PlanIntel):
        if plan_intel.tasks is None or len(plan_intel.tasks) == 0:
            message = f'{self.__class__.__name__} created plan that has no tasks.'
            raise AgentRecoverableException(message)

        if len(plan_intel.tasks) > self.plan_task_count_limit:
            message = f'{self.__class__.__name__} created plan had {len(plan_intel.tasks)} tasks which is more than the limit of {self.plan_task_count_limit}.'
            raise AgentOverThoughtRecoverableException(message)
