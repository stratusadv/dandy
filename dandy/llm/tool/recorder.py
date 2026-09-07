from dandy.core.utils import pascal_to_title_case
from dandy.llm.tool.intel import LlmToolCallsIntel
from dandy.recorder.events import Event, EventAttribute, EventType
from dandy.recorder.recorder import Recorder

_EVENT_OBJECT_NAME = 'LLM Tool Service'


def recorder_add_tool_call_event(
        tool_calls_intel: LlmToolCallsIntel,
        event_id: str,
):
    for tool_call in tool_calls_intel:
        Recorder.add_event(
            Event(
                id=event_id,
                object_name=_EVENT_OBJECT_NAME,
                callable_name='Tool Call',
                type=EventType.RESPONSE,
                attributes=[
                    EventAttribute(
                        key='Name',
                        value=tool_call.name,
                    ),
                    EventAttribute(
                        key='Arguments',
                        value=tool_call.arguments,
                        is_card=True,
                    ),
                ]
            )
        )


def recorder_add_tool_result_event(
        tool_name: str,
        result: str,
        event_id: str,
):
    Recorder.add_event(
        Event(
            id=event_id,
            object_name=_EVENT_OBJECT_NAME,
            callable_name=pascal_to_title_case(tool_name),
            type=EventType.SUCCESS,
            attributes=[
                EventAttribute(
                    key='Result',
                    value=result,
                    is_card=True,
                )
            ]
        )
    )
