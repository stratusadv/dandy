import json

from dandy.processor.agent.intelligence.intel.plan_intel import PlanIntel
from dandy.processor.agent.intelligence.intel.task_intel import TaskIntel
from dandy.processor.agent.strategy import ProcessorsStrategy
from dandy.core.utils import pascal_to_title_case
from dandy.recorder.utils import json_default
from dandy.llm.prompt.typing import PromptOrStr
from dandy.recorder.events import Event, EventAttribute, EventType
from dandy.recorder.recorder import Recorder

_EVENT_OBJECT_NAME = 'LLM Agent'


def _recorder_add_llm_agent_event(
        action_description: str,
        event_id: str,
        attributes: list[EventAttribute] | None = None,
):
    Recorder.add_event(
        Event(
            id=event_id,
            object_name=_EVENT_OBJECT_NAME,
            callable_name=action_description,
            type=EventType.OTHER,
            attributes=attributes
        )
    )


def recorder_add_llm_agent_create_plan_event(
        prompt: PromptOrStr,
        processors_strategy: ProcessorsStrategy,
        event_id: str,
):
    _recorder_add_llm_agent_event(
        action_description='Create Plan',
        event_id=event_id,
        attributes=[
            EventAttribute(
                key='Goal',
                value=str(prompt),
                is_card=True,
            ),
            EventAttribute(
                key=pascal_to_title_case(processors_strategy.__class__.__qualname__),
                value=json.dumps(
                    processors_strategy.as_dict(),
                    indent=4,
                    default=json_default
                ),
                is_card=True,
            )
        ]
    )


def recorder_add_llm_agent_finished_creating_plan_event(
        plan_intel: PlanIntel,
        event_id: str,
):
    _recorder_add_llm_agent_event(
        action_description='Finished Creating Plan',
        event_id=event_id,
        attributes=[
            EventAttribute(
                key='Base Plan',
                value=plan_intel.to_prompt().to_str(),
                is_card=True,
            )
        ]
    )


def recorder_add_llm_agent_running_plan_event(
        plan_intel: PlanIntel,
        event_id: str,
):
    _recorder_add_llm_agent_event(
        action_description='Running Plan',
        event_id=event_id,
        attributes=[
            EventAttribute(
                key='Plan',
                value=plan_intel.to_prompt().to_str(),
                is_card=True,
            )
        ]
    )


def recorder_add_llm_agent_start_task_event(
        task_intel: TaskIntel,
        processors_strategy: ProcessorsStrategy,
        event_id: str,
):
    _recorder_add_llm_agent_event(
        action_description=f'Starting Task #{task_intel.number}',
        event_id=event_id,
        attributes=[
            EventAttribute(
                key='Resource Processor',
                value=processors_strategy.get_processor_module_and_qualname_from_key(
                    task_intel.processors_key
                )
            ),
            EventAttribute(
                key='Starting State',
                value=task_intel.to_prompt().to_str(),
                is_card=True,
            )
        ]
    )


def recorder_add_llm_agent_completed_task_event(
        task_intel: TaskIntel,
        processors_strategy: ProcessorsStrategy,
        event_id: str,
):
    _recorder_add_llm_agent_event(
        action_description=f'Completed Task #{task_intel.number}',
        event_id=event_id,
        attributes=[
            EventAttribute(
                key='Resource Processor',
                value=processors_strategy.get_processor_module_and_qualname_from_key(
                    task_intel.processors_key
                )
            ),
            EventAttribute(
                key='Completed State',
                value=task_intel.to_prompt().to_str(),
                is_card=True,
            )
        ]
    )


def recorder_add_llm_agent_done_executing_plan_event(
        plan_intel: PlanIntel,
        event_id: str,
):
    _recorder_add_llm_agent_event(
        action_description='Done Executing Plan',
        event_id=event_id,
        attributes=[
            EventAttribute(
                key='Final Plan',
                value=plan_intel.to_prompt().to_str(),
                is_card=True,
            )
        ]
    )


def recorder_add_llm_agent_processing_final_result_event(
        plan_intel: PlanIntel,
        event_id: str,
):
    _recorder_add_llm_agent_event(
        action_description='Processing Final Result',
        event_id=event_id,
        attributes=[
            EventAttribute(
                key='Final Results',
                value='\n\n'.join(
                    [task.actual_result for task in plan_intel.tasks]
                ),
                is_card=True,
            )
        ]
    )
